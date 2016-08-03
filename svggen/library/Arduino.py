from svggen.api.ports.ElectricalInputPort import ElectricalInputPort
from svggen.api.ports.ElectricalOutputPort import ElectricalOutputPort
from svggen.api.ports.SerialRXPort import SerialRXPort
from svggen.api.ports.SerialTXPort import SerialTXPort
from svggen.api.ports.DigitalInputPort import DigitalInputPort
from svggen.api.ports.DigitalOutputPort import DigitalOutputPort
from svggen.api.ports.PWMOutputPort import PWMOutputPort
from svggen.api.ports.ServoOutputPort import ServoOutputPort
from svggen.api.ports.AnalogInputPort import AnalogInputPort
from svggen.library.Microcontroller import Microcontroller

__author__ = 'Joseph'

class Arduino(Microcontroller):
  def __init__(self, name="Arduino", numDigitalPins=14, numAnalogPins=6, pwmPins=(3, 5, 6, 9, 10, 11), powerSupply=5):
    """
    For each i in the range of of the number of digital pins (numDigitalPins),
    we set the ith port to allow for the possible types:

    * ElectricalInputPort
    * ElectricalOutputPort
    * DigitalOutputPort
    * DigitalInputPort
    * SerialTXPort
    * SerialRXPort

    Additionally, if i is in the given tuple of pwmPins, we add PWMOutputPort
    as a potential port

    We do the same for the number of analog pins (numAnalogPins), but limit
    the possible types to:

    * ElectricalInputPort
    * ElectricalOutputPort
    * (???) SerialTXPort
    * (???) SerialRXPort

    """
    self._numDigitalPins = numDigitalPins
    self._numAnalogPins = numAnalogPins
    self._pwmPins = pwmPins[:]

    Microcontroller.__init__(self, name, numDigitalPins + numAnalogPins, powerSupply, powerOutPin='VCC', powerInPin='Vin', groundPin='GND')

    for i in range(numDigitalPins):
      self.getPort(i).addPossibleType(ElectricalInputPort)
      self.getPort(i).addPossibleType(ElectricalOutputPort)
      self.getPort(i).addPossibleType(DigitalOutputPort)
      self.getPort(i).addPossibleType(DigitalInputPort)
      self.getPort(i).addPossibleType(SerialTXPort)
      self.getPort(i).addPossibleType(SerialRXPort)
      if i in pwmPins:
        self.getPort(i).addPossibleType(PWMOutputPort)
        self.getPort(i).addPossibleType(ServoOutputPort)
    for i in range(numAnalogPins):
      self.getPort('A' + str(i)).addPossibleType(AnalogInputPort)
      self.getPort('A' + str(i)).addPossibleType(ElectricalInputPort)
      self.getPort('A' + str(i)).addPossibleType(ElectricalOutputPort)
      self.getPort('A' + str(i)).addPossibleType(DigitalOutputPort)
      self.getPort('A' + str(i)).addPossibleType(DigitalInputPort)
      self.getPort('A' + str(i)).addPossibleType(SerialTXPort)
      self.getPort('A' + str(i)).addPossibleType(SerialRXPort)


    self.reservePort(0)
    self.reservePort(1)

    #self.addPort(PowerOutput(power, "PowerOut"))
    self.addCodeFile('code/arduino.ino')
    self.addCodeFile('code/robot_code_arduino.cpp')

  def getPort(self, port):
    """
    Gets the port with the given key.  If port is an integer, performs
    a straightforward lookup.  If the port is 'A' + an integer, it
    gets the integer plus the number of digital pins

    :param port: the port number or 'A%d' % (the port number)
    :type port: int or str

    :returns: the port with the given index
    :rtype: Port (api.ports.Port.Port)
    """
    if isinstance(port, str) and port[0] == 'A':
      # XXX: throw an error if isinstance(port, str) and port[0] != 'A'?
      num = port[1:]
      return Microcontroller.getPort(self, int(num)+self._numDigitalPins)
    return Microcontroller.getPort(self, port)

  def getCodeName(self, port):
    portName = Microcontroller.getCodeName(self, port)
    try:
      num = int(portName)
      if num >= self._numDigitalPins:
        return 'A' + str(num - self._numDigitalPins)
    except ValueError:
      pass
    return portName

  def getCode(self):
    """
    Create the C Arduino code for setting the pin modes
    """

    code = '\n'
    outputTypes = {
      'ElectricalOutput':'OUTPUT',
      'PWMOutput':'OUTPUT',
      'DigitalOutput':'OUTPUT',
      'ElectricalInput':'INPUT',
    }

    code += '@@insert<setup()>'
    code += '\nsetupPinModes();'

    code += '\n@@method<void setupPinModes()>'
    code += '\nvoid setupPinModes()'
    code += '\n{'
    code += '\n}'
    code += '\n@@insert<void setupPinModes()>'
    res = 'making code for setupPinModes'
    for i in range(self._numDigitalPins + self._numAnalogPins):
      port = self.getPort(i)
      portType = str(port.getType())
      res += '\n\tsee port ' + port.getName() + ' of type ' + portType
      for outputType in outputTypes:
        if outputType in portType:
          code += '\npinMode(' + str(i) + ', ' + outputTypes[outputType] + ');'
    #print res
    return Microcontroller.getCode(self) + [code]

class ArduinoProMini(Arduino):
  def __init__(self, name=""):
    numDigitalPins = 14
    numAnalogPins = 6
    pwmPins = [3, 5, 6, 9, 10, 11]
    Arduino.__init__(self, "ArduinoProMini" if name=="" else name, numDigitalPins, numAnalogPins, pwmPins, 3.3)

    self._dimensions.setParameter("length", 39)
    self._dimensions.setParameter("width", 19)
    self._dimensions.setParameter("height", 9)

    self._dimensions.setParameter("nrows", 12)
    self._dimensions.setParameter("ncols", 2)
    self._dimensions.setParameter("rowsep", 0.1 * 25.4)
    self._dimensions.setParameter("colsep", 0.6 * 25.4)

