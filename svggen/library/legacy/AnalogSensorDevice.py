from svggen.api.ElectricalComponent import ElectricalComponent
from svggen.api.ports.AnalogOutputPort import AnalogOutputPort
from svggen.api.ports.PowerInputPort import PowerInputPort
from svggen.api.ports.Ground import Ground

__author__ = 'Joseph'

class AnalogSensorDevice(ElectricalComponent):
  def define(self):
    ElectricalComponent.define(self)
    self.addInterface('signal', AnalogOutputPort(parent=self, name='signal'))
    self.addInterface('ground', Ground(parent=self, name='ground', voltage=0))

  def assemble(self):
    ElectricalComponent.assemble(self)
    ElectricalComponent.setControllerPins(self)
