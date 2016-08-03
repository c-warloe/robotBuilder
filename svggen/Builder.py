from __future__ import print_function
from svggen.Menu import Menu
from svggen.api.component import Component
from svggen import library


class Builder:

  def __init__(self):
    self.c = Component()

    self.mainmenu = {
      "title": "Choose an operation",
      "options": (("a", "Add"),
                  ("d", "Delete"),
                  ("l", "List"),
                  ("p", "Display"),
                  ("s", "Save"),
                  ("f", "Load"),
                  ("q", "Quit")),
      "functions": {"a": self.widget,
                    "d": self.widget,
                    "l": self.widget,
                    "p": self.display,
                    "s": self.save,
                    "f": self.load,
                    "q": self.quit}
    }

    self.widgetmenu = {
      "title": "Choose an attribute",
      "options": (("s", "Subcomponent"),
                  ("p", "Parameter"),
                  ("x", "Constraint"),
                  ("c", "Connection"),
                  ("i", "Interface")),
      "functions": {"s": self.subcomponent,
                    "p": self.parameter,
                    "x": self.constraint,
                    "c": self.connection,
                    "i": self.interface}
    }

  def go(self):
    self.name = raw_input("Enter the name of the new component: ")
    while self.main():
      pass

  def main(self):
    m = Menu(self.mainmenu).go()
    if m is None:
      return True
    return self.mainmenu['functions'][m](m)

  def display(self, option):
    try:
      self.c.makeOutput(displayOnly = True)
    except Exception as e:
      print (repr(e))
    return True

  def save(self, option):
    # XXX prompt for filename?
    print ("")
    print ("New component written to %s.yaml" % self.name)
    print ("")
    self.c.toYaml(self.name + ".yaml")
    return True

  def load(self, option):
    filename = raw_input("Enter the filename of the component definition: ")
    self.c.fromYaml(filename)
    return True

  def quit(self, option):
    return False

  def widget(self, option):
    m = Menu(self.widgetmenu).go()
    if m is None: return True
    return self.widgetmenu['functions'][m](option, m)

  def selectSubcomponent(self):
    subcomponents = [(x[0], x[1]['object']) for x in self.c.subcomponents.iteritems()]
    selectmenu = { "title" : "Choose a subcomponent" }
    selectmenu['options'] = ["%s (%s)" % x for x in subcomponents]
    selected = Menu(selectmenu).go('index')
    if selected is None: return None
    return subcomponents[selected]

  def selectInterface(self, sub):
    c = library.getComponent(sub)
    selectmenu = { "title" : "Choose an interface" }
    selectmenu['options'] = c.interfaces.keys()
    selected = Menu(selectmenu).go('option')
    return selected

  def selectParameter(self, sub=None):
    selectmenu = { "title" : "Choose a parameter" }
    if sub is None:
      selectmenu['options'] = self.c.parameters.keys()
    else:
      c = library.getComponent(sub)
      selectmenu['options'] = c.parameters.keys()
    selected = Menu(selectmenu).go('option')
    return selected

  def subcomponent(self, option, widget):
    if option == 'a':
      addmenu = { "title" : "Choose a subcomponent to add" }
      addmenu['options'] = sorted(library.allComponents)
      added = Menu(addmenu).go('option')
      if added is None: return True
      name = raw_input("Enter the name of the new %s subcomponent: " % added)
      if name == '': return True
      self.c.addSubcomponent(name, added)
      print ("*** Added subcomponent: " + name + " of type " + added)
    elif option == 'd':
      c = self.selectSubcomponent()
      if c is None: return True
      self.c.delSubcomponent(c[0])
      print ("*** Deleted subcomponent: " + c[0])
    elif option == 'l':
      self.printSubcomponents()
    return True

  def printSubcomponents(self):
      print ( repr(self.c.subcomponents) ),

  def parameter(self, option, widget):
    if option == 'a':
      name = raw_input("Enter the name of the new parameter: ")
      if name == '': return True
      val = raw_input("Enter the default value for %s: " % name)
      if val == '':
        val = 'None'
      from ast import literal_eval
      self.c.addParameter(name, literal_eval(val))
      print ("*** Added parameter: " + name + " with default value " + val)
    elif option == 'd':
      parameters = self.c.parameters.keys()
      deletemenu = { "title" : "Choose a parameter to delete" }
      deletemenu['options'] = parameters
      deleted = Menu(deletemenu).go('option')
      if deleted is None: return True
      self.c.delParameter(deleted)
      print ("*** Deleted subcomponent: " + deleted)
    elif option == 'l':
      # XXX pretty print
      print ( repr(self.c.parameters) ),
    return True

  def constraint(self, option, widget):
    if option == 'a':
      sub = self.selectSubcomponent()
      if sub is None: return True
      param = self.selectParameter(sub[1])
      if param is None: return True

      plist = []
      p = ""
      print("Define a function of these parameters --")
      while p is not None:
        p = self.selectParameter()
        plist.append(p)
      plist.pop()
      print (plist)

      if len(plist) == 1:
        print ("x = " + plist[0])
        val = raw_input("%s.%s = f(x) = " % (sub[0], param))
        if val == '':
          val = "x"
        self.c.addConstraint((sub[0], param), plist[0], val)
        print("*** Added constraint %s.%s = f(x) = %s" % (sub[0], param, val))
      elif len(plist):
        print ("x = " + repr(plist))
        val = raw_input("%s.%s = f(x) = " % (sub[0], param))
        self.c.addConstraint((sub[0], param), plist, val)
        print("*** Added constraint %s.%s = f(x) = %s" % (sub[0], param, val))
      else:
        val = raw_input("%s.%s = constant = " % (sub[0], param))
        from ast import literal_eval
        self.c.addConstConstraint((sub[0], param), literal_eval(val))
        print("*** Added constant constraint %s.%s = %s" % (sub[0], param, val))

    elif option == 'd':
      sub = self.selectSubcomponent()
      if sub is None: return True
      sub = sub[0]
      deletemenu = {'title' : "Select constrained parameter to release"}
      deletemenu['options'] = self.c.subcomponents[sub]['parameters'].keys()
      param = Menu(deletemenu).go("option")
      if param is None: return True
      self.c.delConstraint(sub, param)
      print ("*** Deleted constraint: %s.%s" % (sub, param))
    elif option == 'l':
      self.printSubcomponents()
    return True

  def connection(self, option, widget):
    if option == 'a':
      print("First object -- ", end = '')
      fromSub = self.selectSubcomponent()
      if fromSub is None: return True
      fromInt = self.selectInterface(fromSub[1])
      if fromInt is None: return True

      print("Second object -- ", end = '')
      toSub = self.selectSubcomponent()
      if toSub is None: return True
      toInt = self.selectInterface(toSub[1])
      if toInt is None: return True

      from svggen.api.edge import allEdges
      from svggen.library.connector import allConnectors
      types = allEdges + allConnectors
      typemenu = {"title": "Select type of connection"}
      typemenu["options"] = types
      conntype = Menu(typemenu).go("option")
      if conntype is None: return True

      from ast import literal_eval
      params = {}
      while (True):
        pname = raw_input("Enter connection parameter name: ")
        if pname == '': break
        val = raw_input("%s.%s = " % (conntype, pname))
        params[pname] = literal_eval(val)

      self.c.addConnection([fromSub[0], fromInt], [toSub[0], toInt], conntype, **params)
      print ("*** Added connection : %s.%s - %s.%s (%s) " % (fromSub[0], fromInt, toSub[0], toInt, conntype))

    elif option == 'd':
      deletemenu = {"title": "Select connection to delete"}
      deletemenu["options"] = ["%s.%s - %s.%s (%s)" % tuple(x[0]+x[1]+[x[2],]) for x in self.c.connections]
      deleted = Menu(deletemenu).go("index")
      if deleted is None: return True
      # XXX create function in Component()
      deleted = self.c.connections.pop(deleted)
      print ("*** Deleted connection : %s.%s - %s.%s (%s) " % tuple(deleted[0]+deleted[1]+[deleted[2],]))

    elif option == 'l':
      print ("\n".join( ["%s.%s - %s.%s : %s%s" % (tuple(x[0] + x[1]) + (x[2], repr(x[3]))) for x in self.c.connections] ) )

    return True

  def interface(self, option, widget):
    if option == 'a':
      sub = self.selectSubcomponent()
      if sub is None: return True
      param = self.selectInterface(sub[1])
      if param is None: return True
      name = raw_input("Enter the name of the new interface: ")
      if name == '' : return True
      self.c.inheritInterface(name, (sub[0], param))
      print ("*** Inherited interface %s = %s.%s" % (name, sub[0], param))
    elif option == 'd':
      deletemenu = {"title": "Select connection to delete"}
      interfaces = [(x[0], x[1]["subcomponent"], x[1]["interface"]) for x in self.c.interfaces.iteritems()]
      deletemenu["options"] = ["%s = %s.%s" % x for x in interfaces]
      deleted = Menu(deletemenu).go("index")
      if deleted is None: return True
      print (deleted)
      # XXX create function in Component()
      self.c.interfaces.pop(interfaces[deleted][0])
      print ("*** Deleted interface: " + interfaces[deleted][0])
    elif option == 'l':
      print(repr(self.c.interfaces))
    return True

if __name__ == "__main__":
  b = Builder()
  b.go()
