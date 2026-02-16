import os
from client import GeminiClient, GeminiMessage
from tools import tool_manager

token = os.getenv("API_KEY")
client = GeminiClient(token, tool_manager)

resp = client.send(GeminiMessage(text="Could you roll me 10 6 sided dice please?", is_model=False))
print(resp.text)
print()

while True:
  inp = input("> ")
  resp = client.send(GeminiMessage(text=inp, is_model=False))
  print(resp.text)
  print()