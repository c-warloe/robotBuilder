from Port import Port
from svggen.utils.transforms import get6DOF


class SixDOFPort(Port):
  def __init__(self, parent, obj):
    try:
      params = obj.get6DOF()
    except AttributeError:
      params = get6DOF(obj)
    Port.__init__(self, parent, params)

  def getPts(self):
    return [[self.getParameter(x) for x in ["dx", "dy", "dz"]]]
