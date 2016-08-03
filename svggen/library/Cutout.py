from svggen.api.component import Component
from svggen.api.composables.graph.Face import Rectangle
from svggen.api.composables.GraphComposable import Decoration

class Cutout(Component):

  _test_params = {
    'd': 10,
  }

  def define(self):
    self.addParameter("dx", 10)
    self.addParameter("dy", 10)

  def assemble(self):
    dx = self.getParameter("dx")
    dy = self.getParameter("dy")

    graph = Decoration()
    graph.addFace(Rectangle("r0", dx, dy), prefix="r0")
    self.composables["decoration"] = graph

if __name__ == "__main__":
    h = Cutout()
