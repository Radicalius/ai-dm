import random, requests, os
from typing import List
from bs4 import BeautifulSoup

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

def read_note(args):
  if os.path.exists("notes/"+args["path"]):
    return {
      "contents": open("notes/"+args["path"]).read()
    }
  
tool_manager.register(Tool(
  read_note,
  "read_note",
  """Notes are markdown files containing context useful for the dungeon master. 
     This tool reads a note into context.""",
  [
    ToolParameter("path", "STRING", "path of the note to read", True),
  ]
))
  
def write_note(args):
  open("notes/"+args["path"], "w").write(args["contents"])

tool_manager.register(Tool(
  write_note,
  "write_note",
  """Notes are markdown files containing context useful for the dungeon master. 
     This tool creates a new note with the specified contents""",
  [
    ToolParameter("path", "STRING", "path of the note to read", True),
  ]
))

def list_notes(args):
  return {
    "notes": os.listdir("notes/"+args["path_prefix"])
  }

tool_manager.register(Tool(
  list_notes,
  "list_notes",
  """Notes are markdown files containing context useful for the dungeon master. 
     This tool lists all notes at a specified path prefix""",
  [
    ToolParameter("path_prefix", "STRING", "note path prefix to list", True),
  ]
))

def list_rulebook_entries(args):
  url = ""
  if args["type"] == "spells":
    url = "https://www.aidedd.org/dnd-filters/spells-5e.php"
  elif args["type"] == "monsters":
    url = "https://www.aidedd.org/dnd-filters/monsters.php"
  elif args["type"] == "invocations":
    url = "https://www.aidedd.org/dnd-filters/eldritch-invocations.php"
  elif args["type"] == "items":
    url = "https://www.aidedd.org/dnd-filters/magic-items.php"
  else:
    return {
      "error": "invalid type argument"
    }

  req = requests.get(url)
  soup = BeautifulSoup(req.text, 'html.parser')
  entries = []
  for link in soup.select("#liste tr td.item a"):
    name = link.getText()
    href = link.get("href")
    if "filter" in args and args["filter"].lower() not in name.lower():
      continue

    entries.append(
      {
        "name": name,
        "link": href
      }
    )
  
  return {
    "entries": entries
  }

tool_manager.register(Tool(
  list_rulebook_entries,
  "list_rulebook_entries",
  "List D&D rulebook entries on monsters and spells",
  [
    ToolParameter("filter", "STRING", "filter only rulebook entries which contain this in the title", True),
    ToolParameter("type", "STRING", "entry type (one of spells, monsters, invocations, items)", True)
  ]
))

def get_rulebook_entry(args):
  text = requests.get(args["link"]).text
  only_text = BeautifulSoup(text, "html.parser").get_text()
  return {
    "contents": only_text.strip()
  }

tool_manager.register(Tool(
  get_rulebook_entry,
  "get_rulebook_entry",
  "Get D&D rulebook entry from link url. Use in combination with `list_rulebook_entries` to search for entries",
  [
    ToolParameter("link", "STRING", "link to the rulebook entry", True),
  ]
))