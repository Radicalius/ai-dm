import os
import json
from client import GeminiClient, GeminiMessage
from tools import tool_manager

token = os.getenv("API_KEY")
client = GeminiClient(token, tool_manager)

system_prompt = open("prompts/SYSTEM.md").read()
create_prompt = open("prompts/CREATE.md").read()
prompt = create_prompt.replace("{{ system_prompt }}", system_prompt)

print(prompt)
resp = client.send(GeminiMessage(text=prompt, role="user"))

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