import requests
from tools import ToolManager

class GeminiFunctionResult:
  def __init__(self, name, args):
    self.name = name
    self.args = args

class GeminiMessage:

  def __init__(self, text="", function_res: GeminiFunctionResult=None, is_model=False):
    self.text = text
    self.is_model = is_model
    self.function_res = function_res

  def serialize(self):
    if self.function_res:
      return {
        "parts": {
          "functionResponse": self.function_res
        },
        "role": "function"
      }
    else:
      return {
        "parts": {
          "text": self.text
        },
        "role": "model" if self.is_model else "user"
      }
  
class GeminiRequest:

  def __init__(self, messages, tools):
    self.messages = messages
    self.tools = tools

  def serialize(self):
    return {
      "contents": [m.serialize() for m in self.messages],
      "tools": [
        self.tools.serialize(),
      ]
    }

class GeminiClient:

  def __init__(self, token, tool_manager: ToolManager):
    self.token = token
    self.tool_manager = tool_manager
    self.messages = []

  def send(self, new_message: GeminiMessage) -> GeminiMessage:
    self.messages.append(new_message)
    resp = requests.post(
      "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", 
      headers={
        "x-goog-api-key": self.token             
      },
      json=GeminiRequest(self.messages + [new_message], self.tool_manager).serialize()
    )
    
    assert resp.status_code == 200, f"error sending request to llm api: {resp.status_code}; {resp.text}"
    
    json_resp = resp.json()
    
    assert "candidates" in json_resp and len(json_resp["candidates"]) > 0 and "content" in json_resp["candidates"][0], f"invalid llm response: {resp.text}"
    data = resp.json()["candidates"][0]["content"]
  
    assert "parts" in data and len(data["parts"]) > 0

    if "text" in data["parts"][0]:
      llm_text = data["parts"][0]["text"]
      resp_message = GeminiMessage(text=llm_text, is_model=True)
      self.messages.append(resp_message)
    elif "functionCall" in data["parts"][0]:
      function_call = data["parts"][0]["functionCall"]
      tool_response = GeminiMessage(function_res=self.tool_manager.invoke(function_call["name"], function_call["args"]), is_model=False)
      return self.send(tool_response)
    else:
      assert False, f"invalid llm response: {resp.text}"
    
    return resp_message