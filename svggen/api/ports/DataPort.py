from Port import Port

class DataPort(Port):
  def __init__(self, parent, name='', dataType='string'):
    Port.__init__(self, parent, params={}, name=name)
    self.addAllowableMate(DataPort)
    self.addParameter('dataType', dataType)
    self.addParameter('protocol', 'direct')

  def getParameter(self, name, strict=True):
    return Port.getParameter(self, name, strict=False)

  def setParameter(self, name, value):
    if name == 'dataType':
      return Port.setParameter(self, name, str(value) if value is not None else None)
    return Port.setParameter(self, name, value)

  def canMate(self, otherPort):
    if not otherPort.hasParameter('dataType'):
      return False

    myType = self.getParameter('dataType')
    otherType = otherPort.getParameter('dataType')
    if myType is not None and otherType is not None:
      if myType != otherType:
        return False
    return Port.canMate(self, otherPort)

