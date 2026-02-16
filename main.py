import os
import json
from client import GeminiClient, GeminiMessage
from tools import tool_manager

token = os.getenv("API_KEY")
client = GeminiClient(token, tool_manager)


while True:
  resp = client.send(GeminiMessage(text="I'd like to play out a dnd battle between a chimera and a stone giant. I will play as the stone giant. Please handle all the die rolling and resolve all the actions.", role="user"))
  while True:
    tool_calls = []
    for part in resp.parts:
      if part.text is not None:
        print(part.text)
      elif part.functionCall is not None:
        name, args = part.functionCall["name"], part.functionCall["args"]
        tool_resp = tool_manager.invoke(name, args)
        print(f"called tool {name}({json.dumps(args)})")
        tool_calls.append(tool_resp)

    if not tool_calls:
      break

    resp = client.send(GeminiMessage(functionResponses=tool_calls, role="tool"))

  inp = input("> ")
  resp = client.send(GeminiMessage(text=inp))