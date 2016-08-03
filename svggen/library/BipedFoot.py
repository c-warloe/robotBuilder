from svggen.api.component import Component
from svggen.utils.mymath import sin, pi, deg2rad, tan, cos, N, array
from svggen.api.composables.graph.Face import Face
from svggen.api.composables.GraphComposable import Graph
from svggen.api.composables.graph.Joint import Joint
from svggen.api.ports.FacePort import FacePort
from svggen.api.ports.EdgePort import EdgePort
import IPython
import copy

class BipedFoot(Component):
  def define(self):
    self.addParameter("width")
    self.addParameter("height")
    self.addParameter("w_indent")
    self.addParameter("h_indent")
    self.addInterface("heel", EdgePort(self, None))
    
    

  def assemble(self):
    height = self.getParameter("height")
    width = self.getParameter("width")
    h_indent = self.getParameter("h_indent")
    w_indent = self.getParameter("w_indent")


    
    
    graph = Graph()
    
    faces = []

    #faces.append(Face('', ((0, 0), (crop, 0), (crop, legwidth), (crop, length - legwidth), (crop, length), (0, length), (width, length), (width - crop, length), (width - crop, length - legwidth), (width - crop, legwidth), (width - crop, 0), (width, 0))))
    
    faces.append(Face('', ( (0, 0), (0, height), (-width, height), (-width, height - h_indent), (-w_indent, height - h_indent), (-w_indent, h_indent), (-width, h_indent), (-width, 0))   ))
                          


    
    #faces.append(Face('', ((0, 0),  (0, length), (width, length),  (width, 0))))
    

    graph.attachFace(None, faces[0], 'e0', prefix="r0", angle = 0.0)

      
      
    self.composables["graph"] = graph
      
 
    
    self.setInterface("heel", EdgePort(self, "r0.e1"))
    

  

if __name__ == "__main__":
  b = BipedFoot()
  # b.toYaml("output/Beam/beam.yaml")

  b.setParameter("height", 50)
  b.setParameter("width", 50)
  b.setParameter("h_indent", 10)
  b.setParameter("w_indent", 10)


  b.sympyicize("height")
  b.sympyicize("width")
  b.sympyicize("w_indent")
  b.sympyicize("h_indent")


  b.makeOutput("output/BipedFoot", protobuf=True, display=False)
