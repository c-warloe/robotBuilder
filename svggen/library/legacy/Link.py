from svggen.api.component import Component
from svggen.api.ports.LinkPort import LinkPort
import svggen.utils.mymath as np


class Link(Component):
  def define(self, **kwargs):
    x0 = self.addParameter("x0", 1)
    y0 = self.addParameter("y0", 0)
    x1 = self.addParameter("x1", 0)
    y1 = self.addParameter("y1", 0)
    l = self.addParameter("length", 1, positive=True)
    h = self.addParameter("heading", 0)

    self.addInterface("p0", LinkPort(self, (x0, y0), h))
    self.addInterface("p1", LinkPort(self, (x1, y1), h + np.pi))

    dx = x1-x0
    dy = y1-y0

    self.addSemanticConstraint(np.Eq(l*l, dx*dx + dy*dy))
    self.addSemanticConstraint(np.Eq(h, np.atan2(dy, dx)))

    self.knownConstraints = {
      "length": [l, None],
      "heading": [h, None],
      "x0": [x0, None],
      "y0": [y0, None],
      "x1": [x1, None],
      "y1": [y1, None],
    }

  def updateConstraint(self, constraint, value):
    if self.knownConstraints[constraint][1] is not None:
      self.semanticConstraints.remove(self.knownConstraints[constraint][1])
    self.addSemanticConstraint(np.Eq(value, self.knownConstraints[constraint][0]))
    self.knownConstraints[constraint][1] = self.semanticConstraints[-1]

  def setLength(self, l):
    self.updateConstraint("length", l)

  def setHeading(self, h):
    self.updateConstraint("heading", h)

  def setP0(self, (x, y)):
    self.updateConstraint("x0", x)
    self.updateConstraint("y0", y)

  def setP1(self, (x, y)):
    self.updateConstraint("x1", x)
    self.updateConstraint("y1", y)


if __name__ == "__main__":
    h = Link()
    #h._make_test()
    from svggen.utils.utils import printSummary

    h.setLength(0)
    h.setP0((0,0))
    printSummary(h)
    h.setLength(1)
    printSummary(h)
    h.setP0((1,-1))
    h.setLength(2)
    printSummary(h)
    h.setHeading(90)
    printSummary(h)
    h.setLength(3)
    printSummary(h)
    h.setHeading(45)
    printSummary(h)

    for i,c in enumerate(h.getRelations()):
      print c

