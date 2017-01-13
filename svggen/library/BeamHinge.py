from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import IsoscelesTriangle,Trapezoid
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
from svggen.utils.utils import prefix
import math


class BeamHinge(FoldedComponent):

  def define(self, **kwargs):
    FoldedComponent.define(self, **kwargs)
    self.addParameter("length", 50, positive=True)
    self.addParameter("width", 50, positive=True)


  def assemble(self):

    trapBase = self.getParameter("length")
    triBase = self.getParameter("width")
    trapTop = trapBase+triBase
    height = triBase*math.sqrt(3)/2
    rs = []
    rs.append(IsoscelesTriangle('',triBase,height))
    rs.append(Trapezoid('',trapBase,trapTop,height))
    rs.append(IsoscelesTriangle('', triBase, height))
    rs.append(Trapezoid('', trapBase, trapTop, height))
    rs.append(Trapezoid('', trapBase, trapTop, height))
    rs.append(IsoscelesTriangle('', triBase, height))
    rs.append(Trapezoid('', trapBase, trapTop, height))
    rs.append(IsoscelesTriangle('', triBase, height))

    self.attachFace(None, rs[0], "e1", prefix="t1", angle=-35)
    self.attachFace(prefix('t1','e2'), rs[1], "e0", prefix="tr1", angle=109.5)
    self.attachFace(prefix('tr1', 'e2'), rs[2], "e0", prefix="t2", angle=109.5)
    self.attachFace(prefix('t2', 'e2'), rs[3], "e0", prefix="tr2", angle=109.5)
    self.attachFace(prefix('tr2', 'e3'), rs[4], "e3", prefix="tr3", angle=-70)
    self.attachFace(prefix('tr3', 'e2'), rs[5], "e0", prefix="t3", angle=109.5)
    self.attachFace(prefix('t3', 'e2'), rs[6], "e0", prefix="tr4", angle=109.5)
    self.attachFace(prefix('tr4', 'e2'), rs[7], "e0", prefix="t4", angle=109.5)
    self.mergeEdge(prefix('tr1', 'e3'), prefix('tr4', 'e3'), angle=-70)
    self.mergeEdge(prefix('tr2', 'e2'), prefix('t1', 'e0'), angle=109.5)
    self.mergeEdge(prefix('tr3', 'e0'), prefix('t4', 'e2'), angle=109.5)



    self.place()

    self.addInterface("t_A", EdgePort(self, prefix("tr1", "e1")))
    self.addInterface("b_A", EdgePort(self, prefix("tr2", "e1")))
    self.addInterface("r_A", EdgePort(self, prefix("t1", "e1")))
    self.addInterface("l_A", EdgePort(self, prefix("t2", "e1")))
    self.addInterface("t_B", EdgePort(self, prefix("tr3", "e1")))
    self.addInterface("b_B", EdgePort(self, prefix("tr4", "e1")))
    self.addInterface("r_B", EdgePort(self, prefix("t3", "e1")))
    self.addInterface("l_B", EdgePort(self, prefix("t4", "e1")))




if __name__ == "__main__":
  b = BeamHinge()
  #b._make_test()

