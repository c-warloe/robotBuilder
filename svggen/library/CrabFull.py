from svggen.api.component import Component
from svggen.api.composables.graph.Joint import JointList, Joint
from copy import deepcopy
import sys
import IPython


class CrabFull(Component):
 
 _test_params = {
    "base.height" : 30,
    "base.length" : 50,
    "base.width" : 40,
    "l" : 100,
    "w" : 10
    }
    
 
 def define(self):
 
   angle = -90.0
   self.addSubcomponent("leg1", "BeamBasic", inherit=True)
   self.addSubcomponent("leg2", "BeamBasic", inherit=True)
   self.addSubcomponent("leg3", "BeamBasic", inherit=True)
   self.addSubcomponent("leg4", "BeamBasic", inherit=True)
   self.addSubcomponent("base", "Crab", inherit=True)
   self.addParameter("l", 100)
   self.addParameter("w", 10)
   self.addConstraint(("leg1", "beamwidth"), "w")
   self.addConstraint(("leg2", "beamwidth"), "w")
   self.addConstraint(("leg3", "beamwidth"), "w")
   self.addConstraint(("leg4", "beamwidth"), "w")
   self.addConstraint(("base", "legwidth"), "w")
   self.addConstraint(("leg1", "beamlength"), "l")
   self.addConstraint(("leg2", "beamlength"), "l")
   self.addConstraint(("leg3", "beamlength"), "l")
   self.addConstraint(("leg4", "beamlength"), "l")
   
   basJOINT = [Joint("REVOLUTE", sys.float_info.max, -sys.float_info.max, "ALONG"),
                Joint("REVOLUTE", sys.float_info.max, -sys.float_info.max, "ACROSS")]
   
   
   #basJOINT = []
   
   self.addConnection(("leg1", "topedge"),
                       ("base", "leg1"),
                       angle=angle, edgeType="JOINT", joints=JointList( deepcopy(basJOINT) ))
                    
     
   self.addConnection(("leg2", "botedge"),
                       ("base", "leg2"),
                       angle=angle, edgeType="JOINT", joints=JointList( deepcopy(basJOINT) ))
     
                     
   self.addConnection(("leg3", "topedge"),
                       ("base", "leg3"),
                       angle=angle, edgeType="JOINT", joints=JointList( deepcopy(basJOINT) ))
                       
   self.addConnection(("leg4", "botedge"),
                       ("base", "leg4"),
                       angle=angle, edgeType="JOINT", joints=JointList( deepcopy(basJOINT) ))
   


if __name__ == "__main__":
 f = CrabFull()
 
 f.setParameter("base.height", 30)
 f.setParameter("base.width", 50)
 f.setParameter("base.length", 50)
 
 f.sympyicize("base.height")
 f.sympyicize("base.length")
 f.sympyicize("base.width")
 f.sympyicize("l")
 f.sympyicize("w")
 

 f.make()
 f.toProtoBuf("output/CrabFull")
 f.rebuild()
 f._make_test()
