from svggen.api.component import Component
from svggen.api.composables.graph.Face import Rectangle
from svggen.api.composables.GraphComposable import Graph
from svggen.api.ports.EdgePort import EdgePort


class FourBar(Component):

    _test_params = {
        'flexlengthx': 100,
        'flexlengthy': 200,
        'flexwidth': 20,
        'depth': 50,
    }

    def define(self):
        self.addParameter("flexlengthx")
        self.addParameter("flexlengthy")
        self.addParameter("flexwidth", 5)
        self.addParameter("depth")

        self.addInterface("topedge", EdgePort(self, None))
        self.addInterface("botedge", EdgePort(self, None))
        self.addInterface("output", EdgePort(self, None))

    def assemble(self):
        lx = self.getParameter("flexlengthx")
        ly = self.getParameter("flexlengthy")
        w = self.getParameter("flexwidth")
        t = self.getParameter("depth")

        graph = Graph()

        r = Rectangle('r0', w, lx)
        graph.addFace(r, 'r0')

        s = Rectangle('r1', w, t)
        graph.attachFace('r0.e2', s, 'e0', 'r1', angle=90)

        r = Rectangle('r2', w, lx)
        graph.attachFace('r1.e2', r, 'e0', 'r2', angle=90)

        r = Rectangle('r3', t, lx/2.)
        graph.attachFace('r1.e1', r, 'e0', 'r3', angle=90)

        r = Rectangle('r5', t, ly)
        graph.attachFace('r3.e2', r, 'e0', 'r5', angle=90)

        self.composables["graph"] = graph

        self.setInterface("topedge", EdgePort(self, "r0.e0"))
        self.setInterface("botedge", EdgePort(self, "r2.e2"))
        self.setInterface("output", EdgePort(self, "r5.e2"))

if __name__ == "__main__":
  e = FourBar()
  e._make_test()

