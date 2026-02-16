import requests
import os
from client import GeminiClient

token = os.getenv("API_KEY")
client = GeminiClient(token)

resp = client.send("Let's play dnd")
print(resp.text)
print()

while True:
  inp = input("> ")
  resp = client.send(inp)
  print(resp.text)
  print()