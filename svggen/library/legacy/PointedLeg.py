from svggen.utils.mymath import sqrt, atan2, rad2deg

from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import Face, Rectangle
from svggen.api.ports.EdgePort import EdgePort
from svggen.api.ports.PointPort import PointPort
from svggen.utils.mymath import Eq


class PointedLeg(FoldedComponent):
    _test_params = {
        'length': 150,
    }

    def define(self, **kwargs):
        FoldedComponent.define(self, **kwargs)
        self.addParameter("rightwidth", 7, positive=True)
        self.addParameter("frontwidth", 7, positive=True)
        self.addParameter("length", 150, positive=True)
        self.addSemanticConstraint(Eq(self.getParameter("rightwidth"), self.getParameter("frontwidth")))

        self.addConstant("phase", False, **kwargs)
        self.addConstant("top", 0, **kwargs)

    def assemble(self):
        rw = self.getParameter("rightwidth")
        fw = self.getParameter("frontwidth")
        l = self.getParameter("length")
        phase = self.getParameter("phase")

        w2 = sqrt(rw * rw + fw * fw)
        w = fw # min(fw, rw)

        r = Rectangle("", w2, l)
        t = self.getParameter("top")

        self.attachFace(None, Face("", ((fw, -w), (fw, l), (0, l), (0,0))), None, "r1")
        self.attachFace("r1.e2", Rectangle("", fw, t), "e0", "t1", angle=0)
        self.attachFace("r1.e1", Face("", ((rw, w), (rw, l+w), (0, l+w), (0,0))), "e3", "r2", angle=90)
        self.attachFace("r2.e2", Rectangle("", rw, t), "e0", "t2", angle=0)
        self.mergeEdge("t1.e1", "t2.e3", angle=90)
        angle = rad2deg(atan2(rw, fw))
        if phase:
          self.attachFace("r2.e1", r, "e3", "r0", angle=180-angle)
          self.attachFace("r0.e2", Rectangle("", w2, t), "e0", "t0", angle=0)
          self.mergeEdge("t2.e1", "t0.e3", angle=180-angle)
          self.addTab("r1.e3", "r0.e1", angle = 90+angle, width=w2)
        else:
          self.attachFace("r1.e3", r, "e1", "r0", angle=180-angle)
          self.attachFace("r0.e2", Rectangle("", w2, t), "e0", "t0", angle=0)
          self.mergeEdge("t1.e3", "t0.e1", angle=180-angle)
          self.addTab("r2.e1", "r0.e3", angle = 90+angle, width=w2)

        self.place()

        self.addInterface("slots", EdgePort(self, "r0.e%d" % (phase and 1 or 3)))
        self.addInterface("top", EdgePort(self, "t0.e%d" % (phase and 1 or 3)))
        self.addInterface("front", EdgePort(self, "t1.e2"))
        self.addInterface("right", EdgePort(self, "t2.e2"))
        self.addInterface("diag", EdgePort(self, "t0.e2"))
        self.addInterface("topface", [EdgePort(self, x) for x in ["t0.e2", "t1.e2", "t2.e2"]])
        self.addInterface("foot", PointPort(self, edge=self.getEdge("r1.e0"), cross=self.getEdge("r2.e0")))


if __name__ == "__main__":
  e = PointedLeg()
  e.setParameter("length", 20)
  e.setParameter("frontwidth", 2)
  e.printAllSolutions()

  '''
  e.setParameter("phase", True)
  e.setParameter("top", 20)
  e._make_test()
  '''

