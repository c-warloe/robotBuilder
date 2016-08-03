import svggen.api.ports
from svggen.api.ports.ElectricalPort import ElectricalPort

class ElectricalOutputPort(ElectricalPort):
  def __init__(self, parent=None, name='', physical=True, voltage=None):
    ElectricalPort.__init__(self, parent, name, physical=physical, voltage=voltage)
    self.addAllowableMate(svggen.api.ports.ElectricalInputPort)
    self.addRecommendedMate(svggen.api.ports.ElectricalInputPort)
