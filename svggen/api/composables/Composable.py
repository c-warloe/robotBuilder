class Composable:
  def __init__(self):
    self.component = None
  def new(self):
    return self.__class__()
  def append(self, newComposable, newPrefix):
    raise NotImplementedError
  def addComponent(self, componentObj):
    pass
  def addInterface(self, newInterface):
    pass
  def setComponent(self, component):
    self.component = component
  def attach(self, fromPort, toPort, kwargs):
    raise NotImplementedError
  def makeOutput(self, filedir, **kwargs):
    raise NotImplementedError
