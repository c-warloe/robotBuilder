from svggen.api.Driver import Driver
from svggen.api.ports.DataOutputPort import DataOutputPort

__author__ = 'Joseph'

class AnalogSensorDriver(Driver):
  def define(self):
    Driver.define(self)
    self.addInterface('curValue', DataOutputPort(parent=self, name='curValue'))

  def assemble(self):
    Driver.assemble(self)

    self.addCodeFile('code/analog_sensor.cpp')

    self.setAutoPolls()

