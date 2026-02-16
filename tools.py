import random, requests, os
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

tool_manager = ToolManager()

def read_note(args):
  if os.path.exists("notes/"+args["path"]):
    return {
      "contents": open("notes/"+args["path"]).read()
    }
  
def write_note(args):
  open("notes/"+args["path"], "w").write(args["contents"])

def roll_dice(args):
  rolls = [random.randint(1, args["sides"]) for i in range(args["count"])]
  return {
    "rolls": rolls,
    "sum":  sum(rolls)
  }

tool_manager.register(Tool(
  roll_dice,
  "roll_dice",
  "Simulates rolling a specified number of dice with a specified number of sides and returns the rolls and the sum",
  [
    ToolParameter("sides", "INTEGER", "number of sides on each of the dice", True),
    ToolParameter("count", "INTEGER", "number of dice to roll", True),
  ]
))

def get_monster_stats(args):
  note = read_note({"path": f"monsters/{args['name']}"})
  if note:
    return note
  
  content = requests.get(f"https://www.aidedd.org/dnd/monstres.php?vo={args['name']}").text
  write_note({"path": f"monsters/{args['name']}", "contents": content})
  return {
    "contents": content
  }
  
tool_manager.register(Tool(
  get_monster_stats,
  "get_monster_stats",
  "Returns monster stats for a specified monster",
  [
    ToolParameter("name", "STRING", "name of the monster to fetch stats for", True),
  ]
))