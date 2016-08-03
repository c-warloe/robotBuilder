
from svggen.api.Driver import Driver
from svggen.api.ports.DataInputPort import DataInputPort

class LEDDriver(Driver):
  def define(self):
    Driver.define(self)
    self.addParameter('type', 'digital')
    self.addInterface('control', DataInputPort(parent=self, name='control'))

  def assemble(self):
    Driver.assemble(self)

    if self.getParameter('type') == 'analog':
      self.addCodeFile('code/led_analog.cpp')
    else:
      self.addCodeFile('code/led_digital.cpp')

    self.setAutoPolls()
