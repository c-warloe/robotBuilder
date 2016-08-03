
from svggen.api.Driver import Driver
from svggen.api.ports.DataOutputPort import DataOutputPort

class LineDetectorDriver(Driver):
  def define(self):
    Driver.define(self)
    self.addInterface('seeLine', DataOutputPort(parent=self, name='seeLine'))
    self.addInterface('curValue', DataOutputPort(parent=self, name='curValue'))

  def assemble(self):
    Driver.assemble(self)

    self.addCodeFile('code/lineDetector.cpp')

    self.setAutoPolls()
