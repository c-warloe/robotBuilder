import svggen.api.ports
from svggen.api.ports.DataPort import DataPort

class DataInputPort(DataPort):
  def __init__(self, parent, name='', dataType='string'):
    DataPort.__init__(self, parent, name, dataType)
    self.addAllowableMate(svggen.api.ports.DataOutputPort)
    self.addParameter('autoPoll', False)
