from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import Rectangle as Rect
from svggen.api.composables.GraphComposable import Graph
from svggen.api.ports.EdgePort import EdgePort
from svggen.api.ports.FacePort import FacePort


class Rectangle(FoldedComponent):

  _test_params = {
    'l': 100,
    'w': 400,
  }

  def define(self, **kwargs):
    FoldedComponent.define(self, **kwargs)

    self.addParameter("l", 100, positive=True)
    self.addParameter("w", 400, positive=True)

  def assemble(self):
    dx = self.getParameter("l")
    dy = self.getParameter("w")

    self.addFace(Rect("r", dx, dy))

    self.place() 

    self.addInterface("face", FacePort(self, "r"))
    self.addInterface("b", EdgePort(self, "e0"))
    self.addInterface("r", EdgePort(self, "e1"))
    self.addInterface("t", EdgePort(self, "e2"))
    self.addInterface("l", EdgePort(self, "e3"))

if __name__ == "__main__":
    h = Rectangle()
    #h._make_test()

