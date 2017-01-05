from svggen.api.component import Component
from svggen.utils.mymath import sin, pi, deg2rad, tan, cos, N
from svggen.api.composables.graph.Face import Face
from svggen.api.composables.GraphComposable import Graph
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
import IPython

class Beam(Component):
  def define(self):
    self.addParameter("length")
    #ANDY TODO: figure out what these keys were for and implement them more elegantly
    #self.addParameter("diameter")
    self.addParameter("beamwidth")

    self.addParameter("shape", 3)
    self.addParameter("phase", 0)

    self.addParameter("angle")
    self.addParameter("tangle", 90)
    self.addParameter("bangle", 90)

    self.addInterface("topface")
    self.addInterface("botface")
    self.addInterface("topedge")
    self.addInterface("botedge")

  def assemble(self):
    ### Assemble the object
    try:
      tangle = self.getParameter("angle")
      bangle = self.getParameter("angle")
    except KeyError:
      tangle = self.getParameter("tangle")
      bangle = self.getParameter("bangle")

    try:
      d = self.getParameter("diameter")
      t = self.getParameter("diameter") * sin(N(pi) / self.getParameter("shape"))
    except KeyError:
      d = self.getParameter("beamwidth") / sin(N(pi) / self.getParameter("shape"))
      t = self.getParameter("beamwidth")

    length = self.getParameter("length")
    shape = self.getParameter("shape")
    phase = self.getParameter("phase")

    radius = d/2.
    dtheta = deg2rad(360. / shape)
    thetas = [ dtheta / 2. + dtheta * i for i in range(shape) ]

    thickness = 2 * radius * sin(dtheta / 2.)

    dl = [ radius * (1 - cos(t)) / tan(deg2rad(bangle)) for t in thetas ]
    dl = [ l - dl[-phase % shape] for l in dl ]
    dr = [ radius * (1 - cos(t)) / tan(deg2rad(tangle)) for t in thetas ]
    dr = [ r - dr[-phase % shape] for r in dr ]

    graph = Graph()
    angle = 360.0 / shape
    faces = []
    for i in range(len(thetas)):
      faces.append(Face('', ((thickness, dr[i]), (thickness, length - dl[i]), (0, length - dl[i-1]), (0, dr[i-1]))))
    for i in range(phase):
      faces.append(faces.pop(0))

    fromEdge = None
    for i in range(len(faces)):
      graph.attachFace(fromEdge, faces[i], 'e3', prefix="r%d"%i, angle = angle)
      fromEdge = "r%d.e1" % i

    #addTabs(self.graph, "t1", fromEdge, ("r0", "r0.e3"), width=min(thickness, 10), angle=angle)
    """ ANDYTODO: put back tabs
    if phase < 0:
      graph.addTab(fromEdge, faces[0].name + ".e3", angle = angle, width=thickness)
    else:
      graph.addTab(faces[0].name + ".e3", fromEdge, angle = angle, width=thickness)
    """
    self.composables["graph"] = graph

    # Assign interfaces
    self.setInterface("topface", FacePort(self, ["r%d.e0" % n for n in range(shape)], ""))
    self.setInterface("botface", FacePort(self, ["r%d.e2" % n for n in range(shape)], ""))
    self.setInterface("topedge", EdgePort(self, "r%d.e0" % (-phase % shape), "beamwidth"))
    self.setInterface("botedge", EdgePort(self, "r%d.e2" % (-phase % shape), "beamwidth"))
    
    

if __name__ == "__main__":
  b = Beam()
  # b.toYaml("output/Beam/beam.yaml")

  b.setParameter("length", 100)
  b.setParameter("beamwidth", 10)
  b.setParameter("shape", 3)
  b.setParameter("tangle", 90)
  b.setParameter("bangle", 90)
  b.setParameter("phase", 2)
  
  b.sympyicize("length")
  b.sympyicize("beamwidth")
  #b.symbolicize("length")

  b.makeOutput("output/BeamConstrained", protobuf=True, display=False)
