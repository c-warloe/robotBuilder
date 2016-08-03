from svggen.api.component import Component
from svggen.utils.mymath import sin, pi, deg2rad, tan, cos, N, array
from svggen.api.composables.graph.Face import Face
from svggen.api.composables.GraphComposable import Graph
from svggen.api.composables.graph.Joint import Joint
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
import IPython
import copy

class BipedSide(Component):
  def define(self):
    self.addParameter("width")
    self.addParameter("height")
    self.addParameter("length")
    self.addParameter("leg_length")
    
    self.addInterface("foot", EdgePort(self, None))
    self.addInterface("other_half", EdgePort(self, None))
    
    

  def assemble(self):
    height = self.getParameter("height")
    width = self.getParameter("width")
    length = self.getParameter("length")
    leg_length = self.getParameter("leg_length")
    


    
    
    graph = Graph()
    
    faces = []

    #faces.append(Face('', ((0, 0), (crop, 0), (crop, legwidth), (crop, length - legwidth), (crop, length), (0, length), (width, length), (width - crop, length), (width - crop, length - legwidth), (width - crop, legwidth), (width - crop, 0), (width, 0))))
    
    faces.append( Face('', ( (width, 0), (width, leg_length), (0, leg_length), (0, 0)) ) )
    
    
    faces.append( Face('', ( (width, 0), (width, height), (0, height), (0, 0)) ) )
    
    faces.append( Face('', ( (width, 0), (width, length), (0, length), (0, 0)) ) )
    
    faces.append( Face('', ( (height, 0), (height, length), (0, length), (0, 0)) ) )
    faces.append( Face('', ( (height, 0), (height, length), (0, length), (0, 0)) ) )
                 


    
    #faces.append(Face('', ((0, 0),  (0, length), (width, length),  (width, 0))))
    

    graph.attachFace(None, faces[0], 'e0', prefix="r0", angle = 90.0)
    
    
    graph.attachFace('r0.e2', faces[1], 'e0', prefix="r1", angle = 0.0)
    graph.attachFace('r1.e2', faces[2], 'e0', prefix="r2", angle = 90.0)
    graph.attachFace('r1.e1', faces[3], 'e0', prefix="r3", angle = 90.0)
    graph.attachFace('r1.e3', faces[4], 'e0', prefix="r4", angle = 90.0)
    
      
      
    self.composables["graph"] = graph
    
    self.setInterface("foot", EdgePort(self, "r0.e0"))
    self.setInterface("other_half", EdgePort(self, "r2.e2")) 
      
 
    
    

  

if __name__ == "__main__":
  b = BipedSide()
  # b.toYaml("output/Beam/beam.yaml")

  b.setParameter("height", 100)
  b.setParameter("width", 50)
  b.setParameter("length", 50)
  b.setParameter("leg_length", 20)


  b.sympyicize("height")
  b.sympyicize("width")
  b.sympyicize("length")
  b.sympyicize("leg_length")


  b.makeOutput("output/BipedSide", protobuf=True, display=False)
