from svggen.api.component import Component
from svggen.api.composables.graph.Face import Face, Rectangle
from svggen.api.composables.GraphComposable import Graph
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
import svggen.utils.mymath as math

class MotorMount(Component):

  _test_params = {
    'length': 25,
    'width': 10,
    'depth': 25,
    'phase': 0,
    'faces': None,
  }


  def __init__(self):
    Component.__init__(self)


  def define(self):
    self.addParameter("length")
    self.addParameter("width")
    self.addParameter("depth")
    self.addParameter("phase", 0)
    self.addParameter("beltlength", 0)

    self.addParameter("noflap", False)
    self.addParameter("faces")

    self.addInterface("topface", FacePort(self, None))
    self.addInterface("botface", FacePort(self, None))
    self.addInterface("tabedge", EdgePort(self, None))
    self.addInterface("slotedge", EdgePort(self, None))

  def assemble(self):
    graph = Graph()

    try:
      faces = self.getParameter("faces")
    except KeyError:
      faces = None

    length = self.getParameter("length")
    width = self.getParameter("width")
    depth = self.getParameter("depth")
    phase = self.getParameter("phase")
    beltlength = self.getParameter("beltlength")

    rs = []
    rs.append(Rectangle("", width, length))
    rs.append(Rectangle("", depth, length))
    rs.append(Rectangle("", width, length))
    rs.append(Rectangle("", depth, length))

    crown1 = Face("", (
      (depth, 0),
      (depth, depth/2),
      (depth/2, 0),
      (0, depth/2),
      (0, 0)
    ))

    crown2 = Face("", (
      (depth, 0),
      (depth, depth/2),
      (depth/2, 0),
      (0, depth/2),
      (0, 0)
    ))

    belt_recver = Rectangle("", width, depth/2)
    belt_sender = Rectangle("", width, depth/2)
    belt = Rectangle("", width, beltlength or ((math.N(math.pi) * 2 ** 0.5)/4.) * depth)

    for i in range(phase):
      rs.append(rs.pop(0))

    fromEdge = None
    for i in faces or range(4):
      graph.attachFace(fromEdge, rs[i], "e3", prefix="r%d"%i, angle=90)
      fromEdge = 'r%d.e1' % i

    graph.attachFace('r1.e0', crown1, "e0", prefix="c1", angle=0)
    graph.attachFace('r3.e0', crown2, "e0", prefix="c2", angle=0)
    graph.attachFace('r2.e0', belt_recver, "e0", prefix="br", angle=0)
    graph.attachFace('r0.e0', belt_sender, "e0", prefix="bs", angle=0)
    graph.attachFace('bs.e2', belt, "e0", prefix="b", angle=0)

    graph.mergeEdge('bs.e3', 'c1.e1', angle=90)
    graph.mergeEdge('c1.e4', 'br.e1', angle=90)
    graph.mergeEdge('br.e3', 'c2.e1', angle=90)

    if faces is None:
      graph.addTab("r0.e3", "r3.e1", angle= 90, width=min(10, [depth, width][phase % 2]))

    graph.addTab("b.e2", "br.e2", angle=90, width=10)

    self.composables["graph"] = graph

    #Define interfaces
    self.setInterface("topface", FacePort(self, ["r%d.e0" % n for n in faces or range(4)]))
    self.setInterface("botface", FacePort(self, ["r%d.e2" % n for n in faces or range(4)]))
    self.setInterface("tabedge", EdgePort(self, fromEdge))
    self.setInterface("slotedge", EdgePort(self, "r%d.e3" % (faces or range(4))[0]))

if __name__ == "__main__":

  b = MotorMount()
  b._make_test()

