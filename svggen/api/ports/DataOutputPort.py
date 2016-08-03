import svggen.api.ports
from svggen.api.ports.DataPort import DataPort

class DataOutputPort(DataPort):
  def __init__(self, parent, name='', dataType='string'):
    DataPort.__init__(self, parent, name, dataType)
    self.addAllowableMate(svggen.api.ports.DataInputPort)
