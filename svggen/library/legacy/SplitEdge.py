from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import Face
from svggen.api.ports.EdgePort import EdgePort
from svggen.utils.mymath import cumsum, Eq


class SplitEdge(FoldedComponent):

    _test_params = {
        'toplength': (10, 30, 60),
        'botlength': (80, 20),
        'tolerance': 10,
    }

    def define(self, **kwargs):
        FoldedComponent.define(self, euler=None, **kwargs)
        self.addConstant("splits", (1,1), **kwargs)
        self.addConstant("tolerance", 0, **kwargs)

        splits = self.getParameter("splits")
        tsum = 0
        for i in range(splits[0]):
          self.addParameter("toplength%d" % i, 10, positive=True)
          tsum += self.getParameter("toplength%d" % i)
        bsum = 0
        for i in range(splits[1]):
          self.addParameter("botlength%d" % i, 10, positive=True)
          bsum += self.getParameter("botlength%d" % i)

        self.addSemanticConstraint(Eq(tsum, bsum))

    def assemble(self):
        splits = self.getParameter("splits")

        tl = [self.getParameter("toplength%d" % i) for i in range(splits[0])]
        bl = [self.getParameter("botlength%d" % i) for i in range(splits[1])]
        t = cumsum(tl[::-1])
        b = cumsum(bl[::-1])

        TOL = self.getParameter("tolerance")
        pts = [(x, 0) for x in b]
        pts += [(x, TOL) for x in t[::-1]]
        pts += [(0, TOL), (0,0)]

        self.addFace(Face("split", pts))
        self.place()

        tops = ["e%d" % (len(b) + d + 1) for d in range(len(t))]
        bots = ["e%d" % d for d in range(len(b))[::-1]]
        for i, topedge in enumerate(tops):
          self.addInterface("topedge%d" % i, EdgePort(self, topedge))
        for i, botedge in enumerate(bots):
          self.addInterface("botedge%d" % i, EdgePort(self, botedge))

if __name__ == "__main__":
    e = SplitEdge()
    # e._make_test()

