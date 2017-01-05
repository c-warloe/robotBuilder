from svggen.api.Driver import Driver
from svggen.api.ports.DataInputPort import DataInputPort

class EServoDriver(Driver):
  def define(self):
    Driver.define(self)
    self.addParameter('motionType', 'angle')
    self.addInterface('control', DataInputPort(parent=self, name='control'))

  def assemble(self):
    Driver.assemble(self)

    self.setInterface('control', DataInputPort(parent=self, name='control'))

    if self.getParameter('motionType') == 'continuous':
      self.addCodeFile('code/servo_continuous.cpp')
    else:
      self.addCodeFile('code/servo_angle.cpp')

    self.setAutoPolls()
