from Port import Port

class ElectricalPort(Port):
  def __init__(self, parent=None, name='', physical=True, voltage=None, required=True):
    Port.__init__(self, parent, params={}, name=name)
    self.addAllowableMate(ElectricalPort)
    self.addParameter('voltage')
    self.addParameter('physical')
    self.addParameter('controllerPin')
    self.addParameter('required')

    self.setParameter('voltage', voltage)
    self.setParameter('physical', physical)
    self.setParameter('required', required)

  def getParameter(self, name, strict=True):
    return Port.getParameter(self, name, strict=False)

  def setParameter(self, name, value):
    if name.lower() == 'voltage' and value is not None:
      if not isinstance(value, (list, tuple)):
        return Port.setParameter(self, name, (value, value))
      try:
        toSet = list(value[:])
        toSet[0] = float(toSet[0])
        toSet[1] = float(toSet[1])
        toSet.sort()
        return Port.setParameter(self, name, toSet)
      except ValueError:
        return None
    return Port.setParameter(self, name, value)
    
  def canMate(self, otherPort):
    if isinstance(otherPort, ElectricalPort):
      #if not self.isPhysical() or not otherPort.isPhysical():
      #  return True
      myVoltage = self.getParameter('voltage')
      otherVoltage = otherPort.getParameter('voltage')
      if myVoltage is not None and otherVoltage is not None:
        if myVoltage[1] < otherVoltage[0]:
          return False
        if myVoltage[0] > otherVoltage[1]:
          return False
    return Port.canMate(self, otherPort)

  def isPhysical(self):
    return self.getParameter('physical')
        
