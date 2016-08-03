from svggen.api.Driver import Driver
from svggen.api.ports.DataOutputPort import DataOutputPort

__author__ = 'Joseph'

class DistanceSensorDriver(Driver):
  def define(self):
    Driver.define(self)
    self.addInterface('curValue', DataOutputPort(parent=self, name='curValue'))

  def assemble(self):
    Driver.assemble(self)

    self.addCodeFile('code/distance_sensor.cpp')

    self.setAutoPolls()

