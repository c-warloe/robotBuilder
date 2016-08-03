from collections import OrderedDict

import os
from svggen import SVGGEN_DIR
from svggen.api.ports.ElectricalPort import ElectricalPort
from svggen.api.ports.Ground import Ground
from svggen.api.ports.Port import Port
from svggen.api.ports.PowerInputPort import PowerInputPort
from svggen.api.ports.PowerOutputPort import PowerOutputPort
from svggen.utils.dimensions import BrainDimensions

__author__ = 'Joseph'

class MicrocontrollerPort(ElectricalPort):
  def __init__(self, parent, name='', physical=True, voltage=None):
    ElectricalPort.__init__(self, parent, name, physical=physical, voltage=voltage)
    self.addParameter('portType', None)
    self.addParameter('codeName', name)
    self._possibleTypes = []

  def getParameter(self, name, strict=True):
    if 'portType' == name:
      if ElectricalPort.getParameter(self, 'portType'):
        return ElectricalPort.getParameter(self, 'portType')
      return self.__class__
    return ElectricalPort.getParameter(self, name)

  def setParameter(self, name, value):
    #if name == 'portType':
      #print 'setting portType to', value
    return ElectricalPort.setParameter(self, name, value)

  def isTypeSet(self):
    return self.getParameter('portType') is not self.__class__

  def setType(self, portOrType):
    if isinstance(portOrType, Port):
      for nextType in self.getPossibleTypes():
        if portOrType.shouldMate(nextType()):
          return self.setType(nextType)
      for nextType in self.getPossibleTypes():
        if portOrType.canMate(nextType()):
          return self.setType(nextType)
    elif self.canBeType(portOrType):
      self.setParameter('portType', portOrType)

  def getType(self):
    if self.isTypeSet():
      return self.getParameter('portType')
    return ElectricalPort

  def addPossibleType(self, portType):
    if not isinstance(portType, (list, tuple)):
      portType = [portType]
    for nextType in portType:
      if not isinstance(nextType, type(self.__class__)):
        continue
      if nextType not in self._possibleTypes:
        self._possibleTypes.append(nextType)

  def getPossibleTypes(self):
    return self._possibleTypes[:]

  def canBeType(self, inType):
    if inType in self._possibleTypes:
      return True
    for nextType in self.getPossibleTypes():
      if isinstance(nextType(), inType):
        return True
    return False

  def canMate(self, otherPort):
    if self.isTypeSet():
      return self.getParameter('portType')().canMate(otherPort)
    for nextType in self.getPossibleTypes():
      if otherPort.canMate(nextType()):
        return True
    return False

  def shouldMate(self, otherPort):
    if isinstance(otherPort, MicrocontrollerPort):
      if self.isTypeSet() and otherPort.isTypeSet():
        myType = self.getParameter('portType')
        return myType().shouldMate(otherPort.getParameter('portType'))
      else:
        return True
    if self.isTypeSet():
      return otherPort.shouldMate(self.getParameter('portType')())
    for myType in self._possibleTypes:
      if otherPort.shouldMate(myType()):
        return True
    return False

class Microcontroller():
  def __init__(self, name="", numPins=0, powerSupply=5, powerInPin=-1, powerOutPin=-1, groundPin=-1):
    self._name = "Microcontroller" if name=="" else name
    self._ports = OrderedDict()          # map of port names to port objects
    self._connections = OrderedDict()    # map of port objects to connected ports
    self._reserved = []                  # list of pins which should not be used for automatic pin connections
    self._dimensions = BrainDimensions()

    self._numPins = numPins
    for i in range(numPins+2):
      if i is powerInPin or i is powerOutPin  or i is groundPin:
        continue
      name = 'Pin ' + str(i)
      self._ports[name] = MicrocontrollerPort(parent=self, name=name)
      self._ports[name].setParameter('codeName', self.getCodeName(self._ports[name]))
      self._connections[self._ports[name]] = []

    name = 'powerInput'
    if isinstance(powerInPin, int) and powerInPin >= 0:
      name = 'Pin ' + str(powerInPin)
    elif isinstance(powerInPin, str):
      name = powerInPin
    self._ports[name] = PowerInputPort(parent=self, name=name, voltage=powerSupply)
    self._connections[self._ports[name]] = []

    name = 'powerOutput'
    if isinstance(powerOutPin, int) and powerOutPin >= 0:
      name = 'Pin ' + str(powerOutPin)
    elif isinstance(powerOutPin, str):
      name = powerOutPin
    self._ports[name] = PowerOutputPort(parent=self, name=name, voltage=powerSupply)
    self._connections[self._ports[name]] = []

    name = 'ground'
    if isinstance(groundPin, int) and groundPin >= 0:
      name = 'Pin ' + str(groundPin)
    elif isinstance(groundPin, str):
      name = groundPin
    self._ports[name] = Ground(parent=self, name=name)
    self._connections[self._ports[name]] = []

    self._codeFiles = []
    self._code = []

  def getName(self):
    return self._name

  def getDimension(self, name):
    return self._dimensions.getParameter(name)

  def getCodeName(self, port):
    portName = self.getPort(port).getName()
    if 'Pin ' in portName:
      portName = portName[portName.find('Pin ') + len('Pin '):]
    return portName

  def getPort(self, port):
    if isinstance(port, Port):
      return port
    if isinstance(port, (int, long)):
      port = 'Pin ' + str(port)
    if isinstance(port, str) and port in self._ports:
      return self._ports[port]
    return None

  def reservePort(self, port):
    self._reserved.append(self.getPort(port))

  def addCodeFile(self, codeFiles):
    if not isinstance(codeFiles, (list, tuple)):
      codeFiles = [codeFiles]
    for file in codeFiles:
      if file not in self._codeFiles:
        fullFile = os.path.join(SVGGEN_DIR, file)
        if not os.path.exists(fullFile):
          fullFile = os.path.join(SVGGEN_DIR, 'library')
          fullFile = os.path.join(fullFile, file)
        if not os.path.exists(fullFile):
          fullFile = os.path.join(SVGGEN_DIR, 'library/code')
          fullFile = os.path.join(fullFile, file)
        if not os.path.exists(fullFile):
          raise ValueError('Code file %s does not exist (added by %s)' % (file, self.getName()))
        self._codeFiles.append(fullFile)

  def getCodeFiles(self, parent=None):
    return self._codeFiles[:]

  def addCode(self, code):
    self._code.append(code)

  def getCode(self):
    return self._code[:]

  def attach(self, otherPorts, myPorts=None, existingConnections=None):
    if existingConnections is None:
      existingConnections = {}
    if not isinstance(myPorts, (list, tuple)):
      myPorts = [myPorts]
    if not isinstance(otherPorts, (list, tuple)):
      otherPorts = [otherPorts]
    if not isinstance(existingConnections, dict):
      if not isinstance(existingConnections, (list, tuple)):
        existingConnections = [existingConnections]
      newArg = {}
      newArg[otherPorts[0]] = existingConnections
      existingConnections = newArg
    myPortsInput = myPorts[:]
    myPorts = []
    for myPort in myPortsInput:
      myPorts.append(self.getPort(myPort))
    for i in range(len(otherPorts)):
      if i >= len(myPorts):
        myPorts.append(None)

    res = ''
    for i in range(len(otherPorts)):
      otherPort = otherPorts[i]
      myPort = myPorts[i]
      otherConnections = []
      if otherPort in existingConnections:
        otherConnections = existingConnections[otherPort]
      res += '\nmicrocontroller trying to attach ' + otherPort.getName() + ' and ' + (myPort.getName() if myPort is not None else 'None')
      res += '\n\tother is type ' + str(otherPort.__class__)
      if myPort is None:
        possiblePorts = []
        bestPorts = []
        for port in self._ports.values():
          if port in self._reserved:
            continue
          res += '\n\tconsidering my port ' + port.getName()
          canMate = True
          shouldMate = True
          if not port.canMate(otherPort):
            canMate = False
          if not port.shouldMate(otherPort):
            shouldMate = False
          for existingPort in otherConnections:
            if not existingPort.canMate(otherPort):
              canMate = False
            if not existingPort.shouldMate(otherPort):
              shouldMate = False
          if canMate:
            possiblePorts.append(port)
            res += '\n\t\tpossible'
          if shouldMate:
            res += '\n\t\trecommended'
            bestPorts.append(port)
        if len(bestPorts) == 0:
          if len(possiblePorts) == 0:
            continue
          bestPorts.extend(possiblePorts)
        counts = []
        for port in bestPorts:
          counts.append(len(self._connections[port]))
        myPort = bestPorts[counts.index(min(counts))]
      if myPort is None:
        continue
      myPorts[i] = myPort
      res += 'microcontroller attaching ' + otherPort.getName() + ' to ' + myPort.getName()
      #print 'microcontroller attaching', otherPort.getName(), 'to', myPort.getName()
      if isinstance(myPort, MicrocontrollerPort):
        myPort.setType(otherPort)
      self._connections[myPort].append(otherPort)
    #print res
    return myPorts


if __name__ == '__main__':
  print 'testing microcontroller'
