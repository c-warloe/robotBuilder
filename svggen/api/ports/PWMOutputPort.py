import svggen.api.ports
from svggen.api.ports.ElectricalOutputPort import ElectricalOutputPort

class PWMOutputPort(ElectricalOutputPort):
  def __init__(self, parent=None, name='', physical=True, voltage=None):
    ElectricalOutputPort.__init__(self, parent, name, physical=physical, voltage=voltage)
    self.addRecommendedMate(svggen.api.ports.PWMInputPort)
