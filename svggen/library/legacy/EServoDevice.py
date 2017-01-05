from svggen.api.ElectricalComponent import ElectricalComponent
from svggen.api.ports.ServoInputPort import ServoInputPort
from svggen.api.ports.ServoOutputPort import ServoOutputPort
from svggen.api.ports.PowerInputPort import PowerInputPort
from svggen.api.ports.Ground import Ground
from svggen.api.composables.FunctionComposable import FunctionComposable

class EServoDevice(ElectricalComponent):
  def define(self):
    ElectricalComponent.define(self)
    self.addInterface('output', ServoOutputPort(parent=self, name='output'))
    self.addInterface('signal', ServoInputPort(parent=self, name='signal'))
    self.addInterface('power', PowerInputPort(parent=self, name='power', voltage=(3,5)))
    self.addInterface('ground', Ground(parent=self, name='ground', voltage=0))

  def assemble(self):
    ElectricalComponent.assemble(self)
    ElectricalComponent.setControllerPins(self)

    cf = FunctionComposable()
    cf.addInput(self, "signal", default=0)
    cf.setOutput(self, "output", lambda signal: 90 * signal)
    self.composables["function"] = cf

if __name__ == "__main__": 
  c = EServoDevice()
  c.make()
  # c.cf.setInputValue("signal", 0.5)
  # print c.cf.getOutputValue("output")

  print c.getInterface("output").getValue()
  c.getInterface("signal").setInputValue(0.2)
  print c.getInterface("output").getValue()
