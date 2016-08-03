from svggen.api.Driver import Driver


class BluetoothModuleDriver(Driver):
  def define(self):
    Driver.define(self)

  def assemble(self):
    Driver.assemble(self)

    self.addCodeFile('code/bluetooth_module.cpp')