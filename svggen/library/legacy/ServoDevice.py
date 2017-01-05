from svggen.api.MechanicalComponent import MechanicalComponent
from svggen.api.ports.ParameterPort import ParameterPort
from svggen.api.ports.Port import Port
from svggen.api.ports.MountPort import MountPort
from svggen.api.ports.SixDOFPort import SixDOFPort
from svggen.api.composables.graph.Face import Face
from svggen.api.composables.GraphComposable import Decoration
from svggen.utils.mymath import D, Eq
from svggen.utils.transforms import RotateZ, Translate
from svggen.utils.utils import printSummary


class ServoDevice(MechanicalComponent):
  def define(self, **kwargs):
    MechanicalComponent.define(self, **kwargs)

    cont = self.addConstant("continuous", False, **kwargs)
    if cont:
      self.addParameter("angle", 0, dynamic=True)

    self.addParameter("input", 0, dynamic=True)
    self.addParameter("scale", 1, positive=True)

    '''
                 |<-G->|
    ^      =====v===== { H
    E          _I_
    v ________| | |_____
      ^ |       |<-F->|<> D
      | |             |
      B | <--- A ---> |
      | | (X) C       |
      v |_____________|

    A : motorlength
    B : motorheight
    C : motorwidth
    D : shoulderlength

    E : hornheight
    F : hornoffset

    G : hornlength
    H : horndepth
    '''
    self.addParameter("length", 30, positive=True)
    self.addParameter("height", 10, positive=True)
    self.addParameter("width", 20, positive=True)
    self.addParameter("shoulderlength", 5, positive=True)

    self.addParameter("hornheight", 5, positive=True)
    self.addParameter("hornoffset", 10, positive=True)

    self.addParameter("hornlength", 5, positive=True)
    self.addParameter("horndepth", 1, positive=True)


  def assemble(self):
    l = self.getParameter("length")
    w = self.getParameter("width")/2
    o = self.getParameter("hornoffset")

    mount = Decoration()
    mount.addFace(Face("", ((o-l, -w), (o, -w), (o, w), (o-l, w))), prefix="mount")
    self.addInterface('mount', MountPort(self, mount))
    
    if self.getParameter("continuous"):
      angle = self.getParameter("angle")
      rate = self.getParameter("input") * self.getParameter("scale")
      self.addSemanticConstraint(Eq(D(angle), rate))
    else:
      angle = self.getParameter("input") * self.getParameter("scale")

    dz = self.getParameter("hornheight")
    dx = self.getParameter("hornlength")

    pre = self.transform3D * RotateZ(angle)
    dcm0 = pre * Translate([0, 0, dz]) 
    dcm1 = pre * Translate([dx, 0, dz]) 

    self.addInterface('input', ParameterPort(self, "input"))
    self.addInterface('angle', Port(self, {"angle": angle}))
    self.addInterface('shaft', SixDOFPort(self, dcm0))
    # Should permit free rotation about z?
    self.addInterface('horn', SixDOFPort(self, dcm1))


if __name__ == "__main__": 
  c = ServoDevice()

  from svggen.api.component import Component
  c = Component()
  c.addSubcomponent("s", "Simulation")
  c.addSubcomponent("c", "ServoDevice", continuous=True)
  c.addConnection(("s", "sim"),
                  ("c", "input"), input=True)
  c.addConnection(("s", "sim"),
                  ("c", "angle"), output=True)
  c.addConnection(("s", "sim"),
                  ("c", "horn"), ground=True, slide=True)
  c.make()
  printSummary(c)
