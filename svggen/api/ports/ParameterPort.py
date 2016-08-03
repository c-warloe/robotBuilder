from Port import Port
from svggen.utils.utils import prefix as prefixString

class ParameterPort(Port):
  def __init__(self, parent, pname):
    params = {pname: parent.getParameter(pname)}
    Port.__init__(self, parent, params)
