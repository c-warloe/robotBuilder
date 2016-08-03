from Port import Port
from svggen.utils.utils import prefix as prefixString
from svggen.utils.utils import prefix as prefixString
import svggen.utils.mymath as np


class LinkPort(Port):
  def __init__(self, parent, pt, heading):
    params = {'x': pt[0], 'y': pt[1], 'heading': heading}
    Port.__init__(self, parent, params)

  def constrain(self, parent, toPort, **kwargs):
    # Can't use default constrain function because pt1 connects to pt2 and vice versa
    constraints = []
    constraints.append(np.Eq(self.getParameter('x'), toPort.getParameter('x')))
    constraints.append(np.Eq(self.getParameter('y'), toPort.getParameter('y')))

    # XXX Hack: How should we name this new angle parameter?
    for k, c in parent.subcomponents.iteritems():
      if c["component"] is self.parent:
        myName = k
      if c["component"] is toPort.parent:
        toName = k
    a = parent.addParameter(myName + toName + "angle", 0)
    constraints.append(np.Eq(a, (toPort.getParameter('heading') - self.getParameter('heading') - np.pi) % (2 * np.pi)))

    try:
      angle = kwargs["angle"]
      constraints.append(np.Eq(angle, a))
    except KeyError:
      # no angle given
      pass

    return constraints

