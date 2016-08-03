from getch import getch
from string import letters

class Menu:
  def __init__(self, menus):
    if isinstance(menus, dict):
      menus = [menus,]
    self.menus = menus

  def go(self, retval = "key"):
    choices = []
    for menu in self.menus:
      print 
      print menu['title']
      keys = []
      options = []
      if len(menu['options']) == 0:
        continue
      for (index, item) in enumerate(menu['options']):
        if isinstance(item, (list, tuple)): 
          key, option = item
        else:
          option = item
          key = letters[index]

        print key, ":", option
        keys.append(key)
        options.append(option)

      choice = None
      while choice not in keys:
        print "input >",
        choice = getch()
        if choice == '\x7f':
          break
        print choice

      if choice == '\x7f':
        choices.append(None)
        continue

      if retval == "key":
        choices.append(choice)
      elif retval == "index":
        choices.append(keys.index(choice))
      else:
        choices.append(options[keys.index(choice)])

    if len(choices) == 0:
      return None
    if len(choices) == 1:
      return choices[0]
    return choices

if __name__ == "__main__":
  top = {
    "title": "Choose an operation",
    "options": (("a", "Add"),
                ("d", "Delete"),
                ("l", "List"))
  }

  second = {
    "title": "Choose a widget",
    "options": (("s", "Subcomponent"),
                ("p", "Parameter"),
                ("x", "Constraint"),
                ("c", "Connection"),
                ("i", "Interface"))
  }

  third = {
    "title": "Choose a widget",
    "options": ("Item 1",
                "Item 2",
                "Item 3",
                "Item 4",
                "Item 5")
  }

  m = Menu([top, second, third])
  a = m.go('option')
  print "You chose: " + repr(a)
