from svggen.api.FoldedComponent import FoldedComponent
from svggen.api.composables.graph.Face import Face, Rectangle
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
from svggen.utils.utils import prefix
import svggen.utils.mymath as math


class RectBeam(FoldedComponent):

  def define(self, **kwargs):
    FoldedComponent.define(self, **kwargs)
    self.addParameter("length", 100, positive=True)
    self.addParameter("width", 20, positive=True)
    self.addParameter("depth", 50, positive=True)


    self.addConstant("tangle", 90, **kwargs)
    self.addConstant("bangle", 90, **kwargs)

    self.addConstant("phase", 0, **kwargs)

    self.addConstant("faces", False, **kwargs)

  def assemble(self):
    tangle = 90 - self.getParameter("tangle")
    bangle = 90 - self.getParameter("bangle")

    faces = self.getParameter("faces")

    length = self.getParameter("length")
    width = self.getParameter("width")
    depth = self.getParameter("depth")
    phase = self.getParameter("phase")

    rs = []
    rs.append(Rectangle("", width, length))
    rs.append(Face("", (
      (depth, math.tan(math.deg2rad(bangle)) * depth),
      (depth, length - math.tan(math.deg2rad(tangle)) * depth),
      (0, length), (0,0)
    )))
    rs.append(Rectangle("", width, length - (math.tan(math.deg2rad(bangle)) + math.tan(math.deg2rad(tangle))) * depth))
    rs.append(Face("", (
      (0, length), (0,0),
      (depth, math.tan(math.deg2rad(tangle)) * depth),
      (depth, length - math.tan(math.deg2rad(bangle)) * depth),
    )))

    for i in range(phase):
      rs.append(rs.pop(0))

    fromEdge = None
    for i in faces or range(4):
      self.attachFace(fromEdge, rs[i], "e3", prefix="r%d"%i, angle=90)
      fromEdge = prefix('r%d' % i,'e1')

    if faces is False:
      self.addTab(prefix("r0","e3"), prefix("r3","e1"), angle= 90, width=[depth, width][phase % 2])

    self.place()

    #Define interfaces
    for i in faces or range(4):
      self.addInterface("face%d"%i, FacePort(self, "r%d"%i))

    self.addInterface("topface", [EdgePort(self, prefix("r%d" % n,"e0")) for n in faces or range(4)])
    self.addInterface("botface", [EdgePort(self, prefix("r%d" % n,"e2")) for n in faces or range(4)])
    for i, n in enumerate(faces or range(4)):
      self.addInterface("topedge%d" % i, EdgePort(self, prefix("r%d" % n,"e0")))
      self.addInterface("botedge%d" % i, EdgePort(self, prefix("r%d" % n,"e2")))

    if faces is not False:
      # If faces is False, then we have connected tabedge and slotedge with a tab
      self.addInterface("tabedge", EdgePort(self, fromEdge))
      self.addInterface("slotedge", EdgePort(self, prefix("r%d" % (faces or range(4))[0],"e3")))


if __name__ == "__main__":
  b = RectBeam()
  # b._make_test()

