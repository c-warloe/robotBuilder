from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import Trapezoid as Trap
from svggen.api.ports.EdgePort import EdgePort
from svggen.api.ports.FacePort import FacePort
from svggen.utils.utils import prefix
from sympy import LessThan


class Trapezoid(FoldedComponent):

    _test_params = {
        'a': 300,
        'b': 400,
        'c': 500
    }

    def define(self, **kwargs):
        FoldedComponent.define(self, **kwargs)

        self.addParameter("h", 200, positive=True)
        self.addParameter("l2", 300, positive=True)
        self.addParameter("l1", 500, positive=True)


    def assemble(self):
        h = self.getParameter("h")
        l1 = self.getParameter("l2")
        l2 = self.getParameter("l1")

        self.addFace(Trap("tr", l1, l2, h))

        self.place()

        self.addInterface("face", FacePort(self, "tr"))
        self.addInterface("t", EdgePort(self, "e1"))
        self.addInterface("b", EdgePort(self, "e3"))

    if __name__ == "__main__":
        h = Trapezoid()
