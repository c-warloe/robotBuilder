__author__ = 'Joseph'

from svggen.api.ElectricalComponent import ElectricalComponent
from svggen.api.ports.PWMInputPort import PWMInputPort
from svggen.api.ports.DigitalInputPort import DigitalInputPort
from svggen.api.ports.Ground import Ground

class LEDDevice(ElectricalComponent):
  def define(self):
    ElectricalComponent.define(self)
    self.addParameter('type', 'digital')
    self.addInterface('signal', DigitalInputPort(parent=self, name='signal'))
    self.addInterface('ground', Ground(parent=self, name='ground', voltage=0))

  def assemble(self):
    ElectricalComponent.assemble(self)

    if self.getParameter('type') == 'analog':
      self.setInterface('signal', PWMInputPort(parent=self, name='signal'))
    else:
      self.setInterface('signal', DigitalInputPort(parent=self, name='signal'))

    ElectricalComponent.setControllerPins(self)
