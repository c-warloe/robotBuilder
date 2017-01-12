from svggen.api.component import Component
from svggen.api.composables.GraphComposable import Decoration
from svggen.api.composables.graph.Face import Face
from svggen.utils.utils import decorateGraph
from svggen.api.ports.MountPort import MountPort

class Header(Component):

  def define(self):
      self.addParameter("nrows", 10)
      self.addParameter("ncols", 10)
      self.addParameter("rowsep", 2.54)
      self.addParameter("colsep", 2.54)
      self.addParameter("diameter", 1)

  def assemble(self):
    d = self.getParameter("diameter")/2.

    def hole(i, j):
      dx = (j - (self.getParameter("ncols").getValue()-1)/2.)*self.getParameter("colsep").getValue()
      dy = (i - (self.getParameter("nrows").getValue()-1)/2.)*self.getParameter("rowsep").getValue()
      return Face("r-%d-%d" % (i,j),
                        ((dx-d, dy-d), (dx+d, dy-d), (dx+d, dy+d), (dx-d, dy+d)),
                        recenter=False)

    graph = Decoration()
    for i in range(self.getParameter("nrows").getValue()):
      for j in range(self.getParameter("ncols").getValue()):
        graph.addFace(hole(i,j), prefix="r-%d-%d" % (i,j))
    self.addInterface("mount", MountPort(self, graph))
    self.composables["decoration"] = graph

if __name__ == "__main__":
    h = Header()
    h.setParameter("nrows", 11)
    h.setParameter("ncols", 2)
    h.setParameter("rowsep", 0.1 * 25.4)
    h.setParameter("colsep", 0.6 * 25.4)
    h.make()

    from svggen.library.Rectangle import Rectangle
    r = Rectangle()
    r.setParameter("l", 19)
    r.setParameter("w", 40)
    decorateGraph(r, "r", "header", mode="hole")

    for f in h.graph.faces:
      r.graph.getFace("r").addDecoration(([(p[0], p[1]) for p in f.pts2d], "hole"))

    from svggen.api.drawing import Drawing
    d = Drawing()
    d.fromGraph(r.graph)
    d.transform(relative=(0,0))

    from svggen.utils.utils.display import displayTkinter
    displayTkinter(d)
