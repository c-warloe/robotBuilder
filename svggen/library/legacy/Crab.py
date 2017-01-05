from svggen.api.component import Component
from svggen.utils.mymath import sin, pi, deg2rad, tan, cos, N, array
from svggen.api.composables.graph.Face import Face
from svggen.api.composables.GraphComposable import Graph
from svggen.api.composables.graph.Joint import Joint
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
import IPython
import copy

class Crab(Component):
  def define(self):
    self.addParameter("width")
    self.addParameter("length")
    self.addParameter("legwidth")
    self.addParameter("height")
    
    self.addInterface("leg1", EdgePort(self, None))
    self.addInterface("leg2", EdgePort(self, None))
    self.addInterface("leg3", EdgePort(self, None))
    self.addInterface("leg4", EdgePort(self, None))

  def assemble(self):
    length = self.getParameter("length")
    width = self.getParameter("width")
    legwidth = self.getParameter("legwidth")
    height = self.getParameter("height")
    #self.addSemanticConstraint("2*legwidth", "<", "length")
    
    
    graph = Graph()
    
    faces = []
    angle = 90.0
    crop = -0.2 * width
    #faces.append(Face('', ((0, 0), (crop, 0), (crop, legwidth), (crop, length - legwidth), (crop, length), (0, length), (width, length), (width - crop, length), (width - crop, length - legwidth), (width - crop, legwidth), (width - crop, 0), (width, 0))))
    
    faces.append(Face('', ((crop, 0), (crop, legwidth), (0, legwidth), (0, length - legwidth), (crop, length - legwidth), (crop, length), 
                          (width - crop, length), (width - crop, length - legwidth), (width, length - legwidth), (width, legwidth), (width - crop, legwidth), (width - crop, 0))))
                          
    owidth = width - 2*crop
    faces.append(Face('', ((0, 0), (0, height), (owidth, height), (owidth, 0))))
    
    faces.append(Face('', ((0, 0), (0, length), (owidth, length), (owidth, 0))))
    
    faces.append(Face('', ((0, 0), (0, height), (owidth, height), (owidth, 0))))
    
    #faces.append(Face('', ((0, 0),  (0, length), (width, length),  (width, 0))))
    

    graph.attachFace(None, faces[0], 'e0', prefix="r0", angle = 0.0)
    graph.attachFace("r0.e6", faces[1], 'e0', prefix="r1", angle=angle)
    graph.attachFace("r1.e2", faces[2], 'e0', prefix="r2", angle=angle)
    graph.attachFace("r2.e2", faces[3], 'e0', prefix="r3", angle=angle)
      
      
    self.composables["graph"] = graph
      
    self.setInterface("leg1", EdgePort(self, "r0.e1"))
    self.setInterface("leg2", EdgePort(self, "r0.e5"))
    self.setInterface("leg3", EdgePort(self, "r0.e7"))
    self.setInterface("leg4", EdgePort(self, "r0.e11"))      
    
    

  

if __name__ == "__main__":
  b = Crab()
  # b.toYaml("output/Beam/beam.yaml")

  b.setParameter("length", 50)
  b.setParameter("width", 50)
  b.setParameter("legwidth", 10)
  b.setParameter("height", 30)
  
  #b.symbolicize("length")
  b.sympyicize("length")
  b.sympyicize("width")
  b.sympyicize("legwidth")
  b.sympyicize("height")

  b.makeOutput("output/Crab", protobuf=True, display=False)
