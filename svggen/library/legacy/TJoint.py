from svggen.api.component import Component
from svggen.api.composables.GraphComposable import Graph
from svggen.api.composables.graph.Face import Rectangle
from svggen.api.ports.EdgePort import EdgePort


class TJoint(Component):

    _test_params = {
        'stemwidth': 50,
        'crosswidth': 30,
        'thickness': 10,
    }

    def define(self):
        self.addParameter("thickness")
        self.addParameter("stemwidth")
        self.addParameter("crosswidth")

        self.addInterface("stemedge", EdgePort(self, None))
        self.addInterface("stemtab", EdgePort(self, None))
        for i in range(3):
          self.addInterface("leftedge%d" % i, EdgePort(self, None))
          self.addInterface("rightedge%d" % i, EdgePort(self, None))

    def assemble(self):
        graph = Graph()

        sw = self.getParameter("stemwidth")
        cw = self.getParameter("crosswidth")
        t = self.getParameter("thickness")

        s = Rectangle("", sw, t)
        r1 = Rectangle("", sw, cw)
        r2 = Rectangle("", sw, cw)

        graph.addFace(r1, 'r0')
        graph.attachFace('r0.e2', s, 'e0', 'r1', angle = 90)
        graph.attachFace('r1.e2', r2, 'e0', 'r2', angle = 90)

        self.composables["graph"] = graph

        self.setInterface("stemedge", EdgePort(self, "r0.e0"))
        self.setInterface("stemtab", EdgePort(self, "r2.e2"))
        for i in range(3):
          self.setInterface("leftedge%d" % i, EdgePort(self, "r%d.e1" % i))
          self.setInterface("rightedge%d" % i, EdgePort(self, "r%d.e3" % i))

if __name__ == "__main__":
  e = TJoint()
  e._make_test()

