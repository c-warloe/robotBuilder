from svggen.api.component import Component
from svggen.utils.mymath import sin, pi, deg2rad, tan, cos, N
from svggen.api.composables.graph.Face import Face
from svggen.api.composables.GraphComposable import Graph
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
import IPython

class BeamBasic(Component):
  def define(self):
    self.addParameter("beamlength")
    self.addParameter("beamwidth")


    self.addInterface("topedge", EdgePort(self, None))
    self.addInterface("botedge", EdgePort(self, None))

  def assemble(self):
    ### Assemble the object
    shape = 4
    beamwidth = self.getParameter("beamwidth")

    length = self.getParameter("beamlength")

    
    angle = 360.0 / shape
    
    temp_angle = 30 * pi / 180
    
    
    graph = Graph()
    point_length = beamwidth * cos(temp_angle)
    
    faces = []
    faces.append(Face('', ((beamwidth, 0.0), (beamwidth, length), (0, length), (0.0, 0.0))))
    faces.append(Face('', ((beamwidth, 0.0), (beamwidth, length), (0, length), (0.0, 0.0))))
    faces.append(Face('', ((beamwidth, 0.0), (beamwidth, length), (0, length), (0.0, 0.0))))
    faces.append(Face('', ((beamwidth, 0.0), (beamwidth, length), (0, length), (0.0, 0.0))))


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
    self.setInterface("topedge", EdgePort(self, "r0.e0"))
    self.setInterface("botedge", EdgePort(self, "r0.e2"))
    
    

if __name__ == "__main__":
  b = BeamBasic()
  # b.toYaml("output/Beam/beam.yaml")

  b.setParameter("beamlength", 100)
  b.setParameter("beamwidth", 10)

  
  b.sympyicize("beamlength")
  b.sympyicize("beamwidth")
  #b.symbolicize("length")

  b.makeOutput("output/BeamBasic", protobuf=True, display=False)
