from svggen.api.FoldedComponent import FoldedComponent
from svggen.utils.mymath import sin, pi, deg2rad, tan, cos
from svggen.api.composables.graph.Face import Face
from svggen.api.composables.GraphComposable import Graph
from svggen.api.composables.FunctionComposable import FunctionComposable
from svggen.api.ports.EdgePort import EdgePort
from svggen.api.ports.FacePort import FacePort
from svggen.utils.utils import prefix

class Beam(FoldedComponent):

  def define(self, **kwargs):
    FoldedComponent.define(self, **kwargs)

    self.addParameter("length", 100, positive=True)
    self.addParameter("beamwidth", 10, positive=True)

    self.addConstant("shape", 3, **kwargs)
    self.addConstant("phase", 0, **kwargs)
    self.addConstant("tangle", 90, **kwargs)
    self.addConstant("bangle", 90, **kwargs)

  def assemble(self):
    ### Assemble the object
    shape = self.getParameter("shape")
    phase = self.getParameter("phase")

    length = self.getParameter("length")
    d = self.getParameter("beamwidth") / sin(pi / shape)
    t = self.getParameter("beamwidth")

    tangle = self.getParameter("tangle")
    bangle = self.getParameter("bangle")

    radius = d/2
    dtheta = deg2rad(360 / shape)
    thetas = [ dtheta / 2 + dtheta * i for i in range(shape) ]

    thickness = 2 * radius * sin(dtheta / 2)

    dl = [ radius * (1 - cos(t)) / tan(deg2rad(bangle)) for t in thetas ]
    dl = [ l - dl[-phase % shape] for l in dl ]
    dr = [ radius * (1 - cos(t)) / tan(deg2rad(tangle)) for t in thetas ]
    dr = [ r - dr[-phase % shape] for r in dr ]

    angle = 360 / shape
    faces = []
    for i in range(len(thetas)):
      faces.append(Face('', ((thickness, dr[i]), (thickness, length - dl[i]), (0, length - dl[i-1]), (0, dr[i-1]))))
    for i in range(phase):
      faces.append(faces.pop(0))

    fromEdge = None
    for i in range(len(faces)):
      self.attachFace(fromEdge, faces[i], 'e3', prefix="r%d"%i, angle = angle)
      fromEdge = prefix("r%d" % i,"e1")

    if phase < 0:
      self.addTab(fromEdge, prefix(faces[0].name,"e3"), angle = angle, width=thickness)
    else:
      self.addTab(prefix(faces[0].name,"e3"), fromEdge, angle = angle, width=thickness)

    self.place()
    
    # Assign interfaces
    for i in range(len(faces)):
      self.addInterface("face%d"%i, FacePort(self, "r%d"%i))

    self.addInterface("topface", [EdgePort(self, prefix("r%d" % n,"e0")) for n in range(shape)])
    self.addInterface("botface", [EdgePort(self, prefix("r%d" % n,"e2")) for n in range(shape)])
    self.addInterface("topedge", EdgePort(self, prefix("r%d" % (-phase % shape),"e0")))
    self.addInterface("botedge", EdgePort(self, prefix("r%d" % (-phase % shape),"e2")))

    cf = FunctionComposable()
    cf.addInput(self, "topedge", default=0)
    cf.setOutput(self, "botedge", lambda topedge: length + topedge)
    self.composables["function"] = cf

if __name__ == "__main__":
  b = Beam()

  '''
  print b.getInterface("botedge").getValue()
  b.getInterface("topedge").setInputValue(-10)
  print b.getInterface("botedge").getValue()
  '''

  b.setParameter('q_a', 1)
  b.setParameter('q_i', 0)
  b.setParameter('q_j', 0)
  b.setParameter('q_k', 0)

  for edge in b.composables['graph'].edges:
    print [x.subs(b.getAllSubs()) for x in edge.pts3D]

  '''
  b._make_test()

  print b.getInterface("botedge").getValue()
  b.getInterface("topedge").setInputValue(-10)
  print b.getInterface("botedge").getValue()
  '''
