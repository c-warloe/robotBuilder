from svggen.utils import mymath as math


class Joint:
    #ANDYTODO: transform these into sublclasses of HyperEdge and/or component
    def __repr__(self):
        return repr(None)

    types = ["REVOLUTE", "PRISMATIC"]
    dirs = ["ALONG", "ACROSS", "NORM"]
    
    jointType = "REVOLUTE"
    lowerLimit = None
    upperLimit = None
    axis = None
    control = None

    def __init__(self, jointType, lowerLimit, upperLimit, axis = None, control = None):
        self.jointType = jointType
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        self.axis = axis
        self.control = control
        
class JointList:
    def __repr__(self):
        return repr(None)

    def __init__(self, joints):
        if not type(joints) == list:
            raise Exception("Joints must be provided as a list")
        self.joints = joints
    
