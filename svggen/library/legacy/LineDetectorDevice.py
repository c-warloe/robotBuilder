from svggen.api.ElectricalComponent import ElectricalComponent
from svggen.api.ports.AnalogInputPort import AnalogInputPort
from svggen.api.ports.PowerInputPort import PowerInputPort
from svggen.api.ports.DigitalInputPort import DigitalInputPort
from svggen.api.ports.Ground import Ground

__author__ = 'Joseph'

class LineDetectorDevice(ElectricalComponent):
  def define(self):
    ElectricalComponent.define(self)
    self.addInterface('ledSignal', DigitalInputPort(parent=self, name='ledSignal'))
    self.addInterface('sensorSignal', AnalogInputPort(parent=self, name='sensorSignal'))
    self.addInterface('ground', Ground(parent=self, name='ground', voltage=0))


  def assemble(self):
    ElectricalComponent.assemble(self)
    ElectricalComponent.setControllerPins(self)
