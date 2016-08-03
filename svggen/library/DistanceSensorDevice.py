from svggen.api.ElectricalComponent import ElectricalComponent
from svggen.api.ports.AnalogInputPort import AnalogInputPort
from svggen.api.ports.PowerInputPort import PowerInputPort
from svggen.api.ports.Ground import Ground

__author__ = 'Joseph'

class DistanceSensorDevice(ElectricalComponent):
  def define(self):
    ElectricalComponent.define(self)
    self.addInterface('signal', AnalogInputPort(parent=self, name='signal'))
    self.addInterface('power', PowerInputPort(parent=self, name='power', voltage=(3,5)))
    self.addInterface('ground', Ground(parent=self, name='ground', voltage=0))

  def assemble(self):
    ElectricalComponent.assemble(self)
    ElectricalComponent.setControllerPins(self)
