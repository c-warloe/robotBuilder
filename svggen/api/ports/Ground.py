from svggen.api.ports.PowerInputPort import PowerInputPort
from svggen.api.ports.PowerOutputPort import PowerOutputPort


class Ground(PowerInputPort, PowerOutputPort):
  def __init__(self, parent=None, name='', physical=True, voltage=0):
    PowerInputPort.__init__(self, parent, name, physical=physical, voltage=voltage)
    PowerOutputPort.__init__(self, parent, name, physical=physical, voltage=voltage)
