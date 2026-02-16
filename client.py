import requests
from tools import ToolManager

class GeminiMessagePart:
  def __init__(self, text=None, functionCall=None, functionResponse=None, is_model=False):
    self.is_model = is_model
    self.text = text
    self.functionCall = functionCall
    self.functionResponse = functionResponse

  def serialize(self):
    return {
      "text": self.text,
      "functionCall": self.functionCall,
      "functionResponse": self.functionResponse,
    }

class GeminiMessage:

  def __init__(self, parts=[], text=None, functionResponses=None, role=""):
    if text is not None:
      self.parts=[GeminiMessagePart(text=text)]
    elif functionResponses is not None:
      self.parts=[GeminiMessagePart(functionResponse=i) for i in functionResponses]
    else:
      self.parts = parts

    self.role = role

  def serialize(self):
    return {
      "parts": [p.serialize() for p in self.parts],
      "role": self.role
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

    parts = []
    for part in data["parts"]:
      if "text" in part:
        llm_text = part["text"]
        parts.append(GeminiMessagePart(text=llm_text))
      elif "functionCall" in part:
        function_call = part["functionCall"]
        parts.append(GeminiMessagePart(functionCall=function_call))
      else:
        assert False, f"invalid llm response: {resp.text}"
    
    next_message = GeminiMessage(parts, role="model")
    self.messages.append(next_message)
    return next_message