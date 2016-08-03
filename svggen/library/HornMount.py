from svggen.api.MechanicalComponent import MechanicalComponent
from svggen.api.composables.graph.Face import Face
from svggen.api.composables.GraphComposable import Decoration
from svggen.api.ports.MountPort import MountPort
from svggen.api.ports.SixDOFPort import SixDOFPort


class HornMount(MechanicalComponent):
  def define(self, **kwargs):
      MechanicalComponent.define(self, **kwargs)

      self.addParameter("sep", 10)
      self.addParameter("d", 1)

  def assemble(self):
    x = self.getParameter("sep") / 2.
    d = self.getParameter("d") / 2.

    graph = Decoration()
    graph.addFace(Face("r0", (
        (-x-d, -d),
        (-x-d, d),
        (-x+d, d),
        (-x+d, 0.01),
        (x-d, 0.01),
        (x-d, d),
        (x+d, d),
        (x+d, -d),
        (x-d, -d),
        (x-d, 0),
        (-x+d, 0),
        (-x+d, -d),
      )), prefix="r0")
    self.addInterface("mount", MountPort(self, graph))
    self.addInterface("horn", SixDOFPort(self, self.transform3D))

if __name__ == "__main__":
    h = HornMount()

