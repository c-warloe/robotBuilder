import svggen.api.ports
from svggen.api.ports.ElectricalInputPort import ElectricalInputPort

class DigitalInputPort(ElectricalInputPort):
  def __init__(self, parent=None, name='', physical=True, voltage=None):
    ElectricalInputPort.__init__(self, parent, name, physical=physical, voltage=voltage)
    self.addRecommendedMate(svggen.api.ports.DigitalOutputPort)
