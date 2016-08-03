from svggen.utils.utils import prefix 
from Composable import Composable

class FunctionComposable(Composable):
  def __init__(self):
    self.ports = {}

  def addInput(self, component, name, default=None):
    self.ports[name] = component.getInterface(name)
    self.ports[name].setInputValue(default)

  def setOutput(self, component, name, fn):
    self.ports[name] = component.getInterface(name)
    self.ports[name].setOutputFunction(lambda: self.evaluate(fn))

  def evaluate(self, fn):
    fnvars = fn.func_code.co_varnames
    kwargs = {}
    for var in fnvars:
      kwargs[var] = self.ports[var].getValue()
    return fn(**kwargs)

  def setInputValue(self, name, value):
    self.ports[name].setInputValue(value)

  def getOutputValue(self, name):
    return self.ports[name].getValue()

  def append(self, newComposable, newPrefix):
    for key, value in newComposable.ports.iteritems():
      self.ports[prefix(newPrefix, key)] = value

  def attach(self, fromInterface, toInterface, kwargs):
    if fromInterface.isInput and toInterface.isOutput:
      fromInterface.setDrivenFunction(toInterface.valueFunction)
    elif fromInterface.isOutput and toInterface.isInput:
      toInterface.setDrivenFunction(fromInterface.valueFunction)
    elif fromInterface.isInput and toInterface.isInput:
      raise AttributeError("Cannot connect two inputs")
    elif fromInterface.isOutput and toInterface.isOutput:
      raise AttributeError("Cannot connect two outputs")

  def makeOutput(self, filedir, **kwargs):
    pass
