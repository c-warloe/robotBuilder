from svggen.api.component import Component
from svggen.api.composables.graph.Face import Face, Rectangle
from svggen.api.composables.GraphComposable import Graph
from svggen.api.ports.EdgePort import EdgePort
from svggen.utils.utils import decorateGraph


class Tetrahedron(Component):

    _test_params = {
        'perimeter': 400,
        'start': 1,
        'end': 0,
        'tetherwidth': 10,
        'tetheroffset': 0,
    }

    def define(self):
        self.addParameter("perimeter")
        self.addParameter("start", 0)
        self.addParameter("end", 1)
        self.addParameter("min", 1)

        self.addParameter("tetherwidth", 0)
        self.addParameter("tetheroffset", 0)

        for i in range(5):
          self.addInterface("endedge%d" % i, EdgePort(self, None))
          self.addInterface("startedge%d" % i, EdgePort(self, None))

    def assemble(self):
       #an equilateral triangular face requires width = unitheight* rt(3)
       fullwidth = self.getParameter("perimeter")/4.
       fullheight = fullwidth*(3**.5)/2.
       h = fullheight * abs(self.getParameter("end") - self.getParameter("start"))

       def splits(width, frac):
         return [width * x for x in (frac/2., 1-frac, 1+frac, 1-frac, 1+frac/2.)]

       se = splits(fullwidth, self.getParameter("end"))
       ss = splits(fullwidth, self.getParameter("start"))

       m = min(self.getParameter("start"),
               self.getParameter("end"),
               self.getParameter("min")) * fullwidth / 2.

       se[0] -= m
       ss[0] -= m
       se[-1] += m
       ss[-1] += m
       xb, xt, index = 0, 0, 0

       graph = Graph()
       fromEdge = None
       for (xstart, xend) in zip(ss, se):
         r = Face("", ((xb, 0), (xb+xstart, 0), (xt+xend, h), (xt, h)))
         graph.attachFace(fromEdge, r, "e0", "r%d" % index, angle = 109.5)
         fromEdge = "r%d.e2" % index
         xb += xstart
         xt += xend
         index += 1

       # self.addConnectors((Tab(), "t1"), "r0.e0", "r4.e2", min(10, fullwidth / 2.), (Flat(), Cut()))
       #addTabs(self.graph, "t1", "r0.e0", ("r4", "r4.e2"), min(10, fullwidth / 2.))
       graph.addTab("r0.e0", "r4.e2")

       self.composables["graph"] = graph

       def tetherOffsets(h, face, olddist = None):
         f = graph.getFace(face)
         c = f.edgeCoords(f.edgeIndex(face + ".e0"))
         dy = (c[0][1] + c[1][1]) / 2.
         c = f.edgeCoords(f.edgeIndex(face + ".e1"))
         if olddist is None:
           dx = (c[0][0] + c[1][0]) / 2.
         else:
           dx = -olddist-c[0][0]
         dist = dx - c[0][0]
         return -dx, dy, dist

       if self.getParameter("tetherwidth"):
         t2 = self.getParameter("tetherwidth")/2.
         to = self.getParameter("tetheroffset")
         cut = Rectangle("cut", .01, h)
         dx, dy, dist = tetherOffsets(h, "r2")
         decorateGraph(self, "r2", decoration=cut, offset=(dx-t2+to, dy), mode="hole")
         decorateGraph(self, "r2", decoration=cut, offset=(dx+t2+to, dy), mode="hole")

         dx, dy, dist = tetherOffsets(h, "r4", dist)
         decorateGraph(self, "r4", decoration=cut, offset=(dx-t2-to, dy), mode="hole")
         decorateGraph(self, "r4", decoration=cut, offset=(dx+t2-to, dy), mode="hole")

       for i in range(5):
         self.setInterface("startedge%d" % i, EdgePort(self, "r%d.e1" % i))
         self.setInterface("endedge%d" % i, EdgePort(self, "r%d.e3" % i))

if __name__ == "__main__":
    h = Tetrahedron()
    h._make_test()

