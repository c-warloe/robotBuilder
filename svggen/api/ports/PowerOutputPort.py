import svggen.api.ports
from svggen.api.ports.ElectricalPort import ElectricalPort

class PowerOutputPort(ElectricalPort):
  def __init__(self, parent=None, name='', physical=True, voltage=None, required=True):
    ElectricalPort.__init__(self, parent, name, physical=physical, voltage=voltage, required=required)
    self.addAllowableMate(svggen.api.ports.PowerInputPort)
    self.addRecommendedMate(svggen.api.ports.PowerInputPort)
