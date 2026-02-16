import requests

class GeminiMessage:

  def __init__(self, text="", is_model=False):
    self.text = text
    self.is_model = is_model

  def serialize(self):
    return {
      "parts": {
        "text": self.text
      },
      "role": "model" if self.is_model else "user"
    }
  
class GeminiRequest:

  def __init__(self, messages):
    self.messages = messages

  def serialize(self):
    return {
      "contents": [m.serialize() for m in self.messages]
    }

class GeminiClient:

  def __init__(self, token):
    self.token = token
    self.messages = []

  def send(self, text) -> GeminiMessage:
    new_message = GeminiMessage(text=text)
    resp = requests.post(
      "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", 
      headers={
        "x-goog-api-key": self.token             
      },
      json=GeminiRequest(self.messages + [new_message]).serialize()
    )
    
    assert resp.status_code == 200, f"error sending request to llm api: {resp.status_code}; {resp.text}"
    
    json_resp = resp.json()
    
    assert "candidates" in json_resp and len(json_resp["candidates"]) > 0 and "content" in json_resp["candidates"][0], f"invalid llm response: {resp.text}"
    data = resp.json()["candidates"][0]["content"]
  
    assert "parts" in data and len(data["parts"]) > 0 and "text" in data["parts"][0], f"invalid llm response: {resp.text}"
    llm_text = data["parts"][0]["text"]
  
    resp_message = GeminiMessage(text=llm_text, is_model=True)
    
    self.messages.append(new_message)
    self.messages.append(resp_message)
    
    return resp_message