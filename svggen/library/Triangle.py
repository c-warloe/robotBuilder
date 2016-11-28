from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import Triangle as Tri
from svggen.api.ports.EdgePort import EdgePort
from svggen.api.ports.FacePort import FacePort


class Triangle(FoldedComponent):

    _test_params = {
        'a': 300,
        'b': 400,
        'c': 500
    }

    def define(self, **kwargs):
        FoldedComponent.define(self, **kwargs)

        self.addParameter("a", 300, positive=True)
        self.addParameter("b", 400, positive=True)
        self.addParameter("c", 500, positive=True)
        da = self.getParameter("a")
        db = self.getParameter("b")
        dc = self.getParameter("c")
        self.addConstraint(da <  db + dc)
        self.addConstraint(db <  dc + da)
        self.addConstraint(dc <  da + db)

    def assemble(self):
        da = self.getParameter("a")
        db = self.getParameter("b")
        dc = self.getParameter("c")

        self.addFace(Tri("t", da, db, dc))

        self.place()

        self.addInterface("face", FacePort(self, "t"))
        self.addInterface("b", EdgePort(self, "e0"))
        self.addInterface("a", EdgePort(self, "e1"))
        self.addInterface("c", EdgePort(self, "e2"))

    if __name__ == "__main__":
        h = Triangle()
