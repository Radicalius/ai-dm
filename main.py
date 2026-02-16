import os
import json
from client import GeminiClient, GeminiMessage
from tools import tool_manager

token = os.getenv("API_KEY")
client = GeminiClient(token, tool_manager)

resp = client.send(GeminiMessage(text="I would like to play a battle between 2 roughly evenly matched D&D monsters. Could you suggest the monsters? Then I'll play 1 and you'll play the other. Please evaluate all of the actions and dice rolls.", role="user"))

while True:
  while True:
    tool_calls = []
    for part in resp.parts:
      if part.text is not None:
        print(part.text)
      elif part.functionCall is not None:
        name, args = part.functionCall["name"], part.functionCall["args"]
        tool_resp = tool_manager.invoke(name, args)
        print(f"::: called tool {name}({json.dumps(args)[:128]}) -> {json.dumps(tool_resp)[:128]}")
        tool_calls.append(tool_resp)

    if not tool_calls:
      break

    resp = client.send(GeminiMessage(functionResponses=tool_calls, role="tool"))

  inp = input("> ")
  resp = client.send(GeminiMessage(text=inp))