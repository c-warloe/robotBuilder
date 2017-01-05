from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import RegularNGon2 as Shape
from svggen.api.composables.GraphComposable import Graph
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.SixDOFPort import SixDOFPort


class Wheel(FoldedComponent):

  index = 0

  def __init__(self, *args, **kwargs):
    FoldedComponent.__init__(self, *args, **kwargs)
    self.index = Wheel.index
    Wheel.index += 1

  def define(self, **kwargs):
    self.GRAPH = self.addConstant("label", "wheel%d" % self.index, **kwargs)
    FoldedComponent.define(self, **kwargs)

    self.addConstant("n", 36, **kwargs)
    self.addParameter("radius", 25, positive=True)

  def assemble(self):
    n = self.getParameter("n")
    l = self.getParameter("radius")
    self.addFace(Shape("r", n, l))
    self.place()

    self.addInterface("wheel", FacePort(self, "r"))
    self.addInterface("origin", SixDOFPort(self, self))

if __name__ == "__main__":
    from svggen.utils.utils import printSummary
    h = Wheel(n=6)
    for p in h.getInterface("wheel").getPts():
      print p
    printSummary(h)
