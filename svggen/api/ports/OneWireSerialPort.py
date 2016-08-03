import svggen.api.ports
from svggen.api.ports.ElectricalPort import ElectricalPort


class OneWireSerialPort(ElectricalPort):
  def __init__(self, parent=None, name='', physical=True, voltage=None, required=True):
    ElectricalPort.__init__(self, parent, name, physical=physical, voltage=voltage, required=required)
    self.addRecommendedMate(svggen.api.ports.OneWireSerialPort)
