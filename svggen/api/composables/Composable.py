class Composable:
  def new(self):
    return self.__class__()
  def append(self, newComposable, newPrefix):
    raise NotImplementedError
  def addComponent(self, componentObj):
    pass
  def addInterface(self, newInterface):
    pass

  def attach(self, fromPort, toPort, kwargs):
    raise NotImplementedError
  def makeOutput(self, filedir, **kwargs):
    raise NotImplementedError
