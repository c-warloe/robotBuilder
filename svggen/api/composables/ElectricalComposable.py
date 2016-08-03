from collections import OrderedDict

from Composable import Composable
from svggen.api.ports.ElectricalPort import ElectricalPort


class ElectricalComposable(Composable):
  def new(self):
    return self.__class__()

  def __init__(self):
    self._connections = OrderedDict()         # Map of each port to list of all connected ports
    self._physicalConnections = OrderedDict() # Map of each port to list of connected physical ports

  # Check whether interface is stored in given list (or in connections if list is omitted)
  # Needed since copies of ports are passed to methods like attach
  #  So instance may different but may be a clone of a known port
  def haveInterface(self, interface, list=None):
    return self.getInterface(interface, list) is not None

  # Return the stored copy of the given interface if it is currently known
  # (May be a clone of the desired one - checks equality by checking name and parent)
  def getInterface(self, interface, list=None):
    toCheck = self._connections if list is None else list
    for storedInterface in toCheck:
      if storedInterface.getParent() is interface.getParent() and storedInterface.getName() == interface.getName():
        return storedInterface
    return None

  # Append another composable - get its stored connections and ports
  def append(self, newComposable, newPrefix):#, **kwargs):
    for (fromPort, toPorts) in newComposable.getConnections().iteritems():
      self.addInterface(fromPort)
      for toPort in toPorts:
        self.attach(fromPort, toPort, {})

  # Learn about a new port in the design
  def addInterface(self, newInterface):
    if (not isinstance(newInterface, ElectricalPort)):
      return

    if not self.haveInterface(newInterface):
      self._connections[newInterface] = []
      if newInterface.isPhysical():
        self._physicalConnections[newInterface] = []

  # Learn about a new connection in the design
  def attach(self, selfInterface, newInterface, kwargs):
    # Record that we have seen these ports and/or get stored one if already seen it
    self.addInterface(selfInterface)
    self.addInterface(newInterface)
    storedSelfInterface = self.getInterface(selfInterface)
    storedNewInterface = self.getInterface(newInterface)

    # Only store connections between electrical ports
    if (not isinstance(selfInterface, ElectricalPort)) or (not isinstance(newInterface, ElectricalPort)):
      return

    # Record the connection if haven't seen it already
    if not self.haveInterface(storedNewInterface, self._connections[storedSelfInterface]):
      self._connections[storedSelfInterface].append(storedNewInterface)
      if storedSelfInterface.isPhysical() and storedNewInterface.isPhysical():
        self._physicalConnections[storedSelfInterface].append(storedNewInterface)

    if not self.haveInterface(storedSelfInterface, self._connections[storedNewInterface]):
      self._connections[storedNewInterface].append(storedSelfInterface)
      if storedSelfInterface.isPhysical() and storedNewInterface.isPhysical():
        self._physicalConnections[storedNewInterface].append(storedSelfInterface)

  def makeOutput(self, filedir, **kwargs):
    res = '\nElectrical Composable makeOutput'

    # Get microcontrollers from parameters of each device
    controllers = {} # Map of microcontrollers to controlled devices
    for port in self._connections:
      parent = port.getParent()
      if parent.hasParameter('controller'):
        parentController = parent.getParameter('controller')
      else:
        parentController = None
      if parentController not in controllers:
        controllers[parentController] = []
      if parent not in controllers[parentController]:
        controllers[parentController].append(parent)

    # For each port not yet connected to a physical port, find a connection on the microcontroller
    for port in self._physicalConnections.keys()[:]:
      if len(self._physicalConnections[port]) == 0 and port.getParameter('required'):
        parent = port.getParent()
        res += '\nsee port ' + port.getName() + ' of parent ' + str(parent)
        if not parent.hasParameter('controller'):
          res += ' - no controller'
          continue
        microcontroller = parent.getParameter('controller')
        chosenPort = microcontroller.attach(port, port.getParameter('controllerPin', strict=False))[0]
        port.setParameter('controllerPin', chosenPort)
        if chosenPort is not None:
          self._connections[port].append(chosenPort)
          self._physicalConnections[port].append(chosenPort)

    # Group interfaces by device
    deviceConnections = {}
    for (fromPort, toPorts) in self._physicalConnections.iteritems():
      parent = fromPort.getParent()
      if parent not in deviceConnections:
        deviceConnections[parent] = []
      deviceConnections[parent].append((fromPort, toPorts))

    # Output a list of wiring instructions
    fres = '\nWiring Instructions:'
    printedConnections = []
    for (controller, devices) in controllers.iteritems():
      for device in devices:
        if device not in deviceConnections:
          continue
        deviceRes = ''
        for (fromPort, toPorts) in deviceConnections[device]:
          for toPort in toPorts:
            if (fromPort, toPort) not in printedConnections and (toPort, fromPort) not in printedConnections:
              deviceRes += '\n\t\tConnect ' + fromPort.getName() + ' to ' + toPort.getName() + ' of ' + toPort.getParent().getName()
              printedConnections.append((fromPort, toPort))
        if len(deviceRes) > 0:
          fres += '\n\tDevice ' + device.getName() + ':'
          fres += deviceRes
    f = open(filedir + '/wiring_instructions.txt', 'w')
    f.write(fres)
    f.close()
    res += fres
    #print fres

  def getConnections(self):
    return self._connections.copy()

  def getPhysicalConnections(self):
    return self._physicalConnections.copy()

  def printConnections(self):
    print 'electrical composable sees connections'
    for (fromPort, toPorts) in self._connections.iteritems():
      print '\t', fromPort.getName(), 'to',
      for toPort in toPorts:
        print toPort.getName() + ', '
      if len(toPorts) == 0:
        print ''

  def printPhysicalConnections(self):
    print 'composable makeoutput sees physical connections'
    for (fromPort, toPorts) in self._physicalConnections.iteritems():
      print '\t', fromPort.getName(), 'to',
      for toPort in toPorts:
        print toPort.getName() + ', '
      if len(toPorts) == 0:
        print ''
