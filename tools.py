import random, re
from typing import List

class ToolParameter:
  def __init__(self, name: str, type: str, desc: str, is_required=False):
    self.name = name
    self.type = type
    self.desc = desc
    self.is_required = is_required

  def serialize(self):
    return {
      "type": self.type,
      "description": self.desc,
    }

class Tool:
  def __init__(self, f, name: str, desc: str, params: List[ToolParameter]):
    self.f = f
    self.name = name
    self.desc = desc
    self.params = params

  def serialize(self):
    return {
      "name": self.name,
      "description": self.desc,
      "parameters": {
        "type": "OBJECT",
        "properties": {param.name: param.serialize() for param in self.params},
        "required": [param.name for param in self.params],
      },
    }

class ToolManager:
  def __init__(self):
    self.functions = {}

  def register(self, tool: Tool):
    self.functions[tool.name] = tool

  def invoke(self, name: str, args):
    return {
      "name": name,
      "response": self.functions[name].f(args)
    }
  
  def serialize(self):
    return {
      "function_declarations": [tool.serialize() for tool in self.functions.values()]
    }

def roll_dice(args):
  rolls = [random.randint(1, args["sides"]) for i in range(args["count"])]
  return {
    "rolls": rolls,
    "sum":  sum(rolls)
  }

tool_manager = ToolManager()
tool_manager.register(Tool(
  roll_dice,
  "roll_dice",
  "Simulates rolling a specified number of dice with a specified number of sides and returns the rolls and the sum",
  [
    ToolParameter("sides", "INTEGER", "number of sides on each of the dice", True),
    ToolParameter("count", "INTEGER", "number of dice to roll", True),
  ]
))