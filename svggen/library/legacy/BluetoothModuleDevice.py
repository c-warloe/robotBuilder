from svggen.api.ElectricalComponent import ElectricalComponent
from svggen.api.ports.PowerInputPort import PowerInputPort
from svggen.api.ports.Ground import Ground
from svggen.api.ports.SerialTXPort import SerialTXPort
from svggen.api.ports.SerialRXPort import SerialRXPort

class BluetoothModuleDevice(ElectricalComponent):
  def define(self):
    ElectricalComponent.define(self)
    self.addInterface('TX', SerialTXPort(parent=self, name='TX'))
    self.addInterface('RX', SerialRXPort(parent=self, name='RX'))
    self.addInterface('VCC', PowerInputPort(parent=self, name='VCC', voltage=3.3))
    self.addInterface('ground', Ground(parent=self, name='ground', voltage=0))

  def assemble(self):
    ElectricalComponent.assemble(self)

    self.setInterface('TX', SerialTXPort(parent=self, name='TX'))
    self.setInterface('RX', SerialRXPort(parent=self, name='RX'))
    self.setInterface('VCC', PowerInputPort(parent=self, name='VCC', voltage=3.3))
    self.setInterface('ground', Ground(parent=self, name='ground', voltage=0))

    ElectricalComponent.setControllerPins(self)
