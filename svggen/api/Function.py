class Function:
  def __init__(self, params, fnstring):
    self.params = params
    self.fnstring = fnstring

  def toYamlObject(self):
    if self.params is None:
      return eval(obj)
    elif self.fnstring == "x":
      return {"parameter": self.params}
    else:
      return {"function": self.fnstring, "parameter": self.params}

  def fromYamlObject(self, obj):
    if isinstance(obj, dict):
      self.params = obj["parameter"]
      self.fnstring = obj.get("function", "x")
    else:
      self.params = None
      self.fnstring = repr(obj)

  def eval(self, parameterizable):
    function = eval("lambda x : " + self.fnstring)
    if isinstance(self.params, (list, tuple)):
      output = function(map(lambda x : parameterizable.getParameter(x, strict=False), self.params))
    elif self.params:
      output = function(parameterizable.getParameter(self.params, strict=False))
    else:
      output = function(None)
    return output

class ConstantFunction(Function):
  def __init__(self, value):
    Function.__init__(self, None, repr(value))

class IdentityFunction(Function):
  def __init__(self, params):
    Function.__init__(self, params, "x")

class YamlFunction(Function):
  def __init__(self, obj):
    Function.__init__(self, None, None)
    self.fromYamlObject(obj)

