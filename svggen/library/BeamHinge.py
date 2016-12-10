from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import IsoscelesTriangle,Trapezoid
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
from svggen.utils.utils import prefix
import math


class BeamHinge(FoldedComponent):

  def define(self, **kwargs):
    FoldedComponent.define(self, **kwargs)
    self.addParameter("length", 100, positive=True)
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


    fromEdge = None
    self.attachFace(fromEdge, rs[0], "e0", prefix="r0", angle=109.5)
    self.attachFace(prefix('r0','e2'), rs[1], "e0", prefix="r1", angle=109.5)
    self.attachFace(prefix('r1', 'e2'), rs[2], "e2", prefix="r2", angle=109.5)
    #self.attachFace(fromEdge, rs[0], "e3", prefix="r%d" % 0, angle=109.5)
    #self.attachFace(fromEdge, rs[0], "e3", prefix="r%d" % 0, angle=109.5)
    #fromEdge = prefix('r%d' % i,'e1')


    self.place()

    #Define interfaces
    '''for i in faces or range(4):
      self.addInterface("face%d"%i, FacePort(self, "r%d"%i))

    self.addInterface("topface", [EdgePort(self, prefix("r%d" % n,"e0")) for n in faces or range(4)])
    self.addInterface("botface", [EdgePort(self, prefix("r%d" % n,"e2")) for n in faces or range(4)])
    for i, n in enumerate(faces or range(4)):
      self.addInterface("topedge%d" % i, EdgePort(self, prefix("r%d" % n,"e0")))
      self.addInterface("botedge%d" % i, EdgePort(self, prefix("r%d" % n,"e2")))'''

    '''if faces is not False:
      # If faces is False, then we have connected tabedge and slotedge with a tab
      self.addInterface("tabedge", EdgePort(self, fromEdge))
      self.addInterface("slotedge", EdgePort(self, prefix("r%d" % (faces or range(4))[0],"e3")))'''


if __name__ == "__main__":
  b = RectBeam()
  # b._make_test()

