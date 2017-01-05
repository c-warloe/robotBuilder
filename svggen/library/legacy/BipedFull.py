from svggen.api.component import Component
from svggen.api.composables.graph.Joint import JointList, Joint
from copy import deepcopy
import sys
import IPython


class BipedFull(Component):
 def define(self):
 
   
   self.addSubcomponent("leftfoot", "BipedFoot", inherit=True)
   self.addSubcomponent("leftside", "BipedSide", inherit=True)
   self.addSubcomponent("rightfoot", "BipedFoot", inherit=True)
   self.addSubcomponent("rightside", "BipedSide", inherit=True)
   
   self.addParameter("l", 50)
   self.addParameter("h",100)
   self.addParameter("w", 50)
   self.addParameter("ll", 20)
   
   
   self.addConstraint(("leftside", "width"), "w")
   self.addConstraint(("leftside", "length"), "l")
   self.addConstraint(("leftside", "height"), "h")
   self.addConstraint(("leftside", "leg_length"), "ll")
   
   self.addConstraint(("rightside", "width"), "w")
   self.addConstraint(("rightside", "length"), "l")
   self.addConstraint(("rightside", "height"), "h")
   self.addConstraint(("rightside", "leg_length"), "ll")
   
   self.addConstraint(("leftfoot", "height"), "w")
   self.addConstraint(("rightfoot", "height"), "w")

   
   
  

   
   planarJoint = [Joint("PRISMATIC", sys.float_info.max, -sys.float_info.max, "ALONG"),
               Joint("PRISMATIC", sys.float_info.max, -sys.float_info.max, "ALONG")]
   
   #planarJoint = []
   
   self.addConnection(("leftfoot", "heel"),
                       ("leftside", "foot"),
                       angle=90.0, edgeType="JOINT", joints=JointList( planarJoint ))
                       
   self.addConnection(("leftside", "other_half"),
                       ("rightside", "other_half"),
                       angle=0.0, edgeType="JOINT", joints=JointList( [] ))
   
   self.addConnection(("rightfoot", "heel"),
                       ("rightside", "foot"),
                       angle=90.0, edgeType="JOINT", joints=JointList( [] ))
                    
     



if __name__ == "__main__":
 f = BipedFull()
 

 f.setParameter("rightfoot.width", 50)
 f.setParameter("leftfoot.width", 50)
 
 f.setParameter("rightfoot.w_indent", 10)
 f.setParameter("leftfoot.w_indent", 10)
 
 f.setParameter("rightfoot.h_indent", 10)
 f.setParameter("leftfoot.h_indent", 10)
 
 f.sympyicize("ll")
 f.sympyicize("h")
 f.sympyicize("l")
 f.sympyicize("w")
 
 f.sympyicize("rightfoot.width")
 f.sympyicize("leftfoot.width")
 
 f.sympyicize("rightfoot.w_indent")
 f.sympyicize("leftfoot.w_indent")
 
 f.sympyicize("rightfoot.h_indent")
 f.sympyicize("leftfoot.h_indent")
 
 

 f.makeOutput("output/BipedFull", protobuf=True, display=False)
