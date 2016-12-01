from svggen.utils import mymath as np
from svggen.api.composables.graph.Joint import Joint


class HyperEdge:

  #ANDYTODO: transform these into sublclasses of HyperEdge and/or componenet
  edgeTypes = ["FOLD", "BEND", "JOINT"]

  @staticmethod
  def edge(allEdges, name, length, face, angle=0, flip=False):
    if allEdges is not None:
      for e in allEdges:
        if e.name == name:
          e.join(length, face=face, angle=angle, flip=flip)
          return e

    e = HyperEdge(name, length, face, angle, flip)
    try:
      allEdges.append(e)
    except:
      pass

    return e

  def __init__(self, name, length, face=None, angle=0, flip=False):
    self.name = name
    self.length = length
    self.tabWidth = None
    self.pts2D = None
    self.pts3D = None
    self.edgeType = "FOLD"
    self.joints = []

    #self.pt1 = pt1
    #self.pt2 = pt2
    if face:
      self.faces = {face: (angle, flip)}
    else:
      self.faces = {}

  def remove(self, face):
    if face in self.faces:
      self.faces.pop(face)
      try:
        face.disconnectFrom(self.name)
      except (ValueError, AttributeError):
        pass

  def rename(self, name):
    self.name = name

  def isTab(self):
    return self.tabWidth is not None

  def setAngle(self, face, angle, flip=False):
    if face in self.faces:
      self.faces[face] = (angle, flip)

  def getInteriorAngle(self):
    if len(self.faces) == 1:
      return None
    elif len(self.faces) == 2:
      angles = self.faces.values()
      if angles[0][1]:
        return angles[0][0] - angles[1][0]
      else:
        return angles[1][0] - angles[0][0]
    else:
      raise ValueError("Don't know how to handle edge with %d faces" % len(self.faces))

  def flipConnection(self, face):
    if face in self.faces:
      oldangle = self.faces[face]
      self.faces[face] = (oldangle[0], not oldangle[1])

  def join(self, length, face, fromface=None, angle = 0, flip = True):
    # angle : angle between face normals

    if not self.matchesLength(length):
      raise ValueError("Face %s of length %f cannot join edge %s of length %f." % (face.name, length, self.name, self.length))
    
    baseangle = 0
    if fromface in self.faces:
      baseangle = self.faces[fromface][0]
    newangle = (baseangle+angle) % 360

    self.faces[face] = (newangle, flip)

  TOL = 5e-2
  def matchesLength(self, length):
    try:
        # XXX: Hack to force type error testing here
        if np.simplify(self.length - length) < self.TOL:
            return True
        else:
            return False
    except TypeError:
        #print 'Sympyicized variable detected in matchesLength, ignoring for now, returning true'
        #print self.length, length
        return True

  def mergeWith(self, other, angle=0, flip=False, tabWidth=None):
    # Takes all of the faces in other into self
    if other is None:
      return self
    self.tabWidth = tabWidth
    other.tabWidth = tabWidth

    if not self.matchesLength(other.length):
      raise ValueError("Edge %s of length %f cannot merge with edge %s of length %f." %
                                (other.name, other.length, self.name, self.length))

    for face in other.faces.keys():
      oldangle = other.faces[face]
      face.replaceEdge(other, self, angle = (angle+oldangle[0]), flip = (flip ^ oldangle[1]))
    return self

  def place(self, pts2D, pts3D):
    #try:
    #  if self.pts2D is not None:
    #    if np.differenceExceeds(self.pts2D, pts2D, self.TOL):
    #      print
    #      print "~~~", self.name
    #      print self.pts2D
    #      print pts2D
    #      print np.difference(self.pts2D, pts2D)
    #      print "~~~"
    #      # raise ValueError( "Mismatched 2D transforms for edge %s " % self.name )
    #  if self.pts3D is not None:
    #    if np.differenceExceeds(self.pts3D, pts3D, self.TOL):
    #      print
    #      print "$$$", self.name
    #      print self.pts3D
    #      print
    #      print pts3D
    #      print
    #      print np.difference(self.pts3D, pts3D)
    #      print "$$$"
          # raise ValueError( "Mismatched 3D transforms for edge %s " % self.name )
    #except TypeError:
    #  raise

    self.pts2D = pts2D
    self.pts3D = pts3D
    
  def get3DCOM(self):
    return (self.pts3D[0] + self.pts3D[1])/2

  def setType(self, edgeType):
    if edgeType is None:
        return # do nothing
    if edgeType not in self.edgeTypes:
        raise Exception("Invalid edge type!")
    self.edgeType = edgeType
    
  def addJoint(self, joint):
    if not self.edgeType is "JOINT":
        raise Exception("Trying to add joints to a non-joint edge")
    if not isinstance(joint, Joint):
        raise Exception("Not a joint!")
    self.joints.append(joint)

  def __eq__(self, other):
    return self.name == other.name

  def __str__(self):
    return self.name + ": " + repr(self.faces)

  def __repr__(self):
    # return self.name + " [ # faces : %d, len : %d ]" % (len(self.faces), self.length)
    ret = "%s#%d" % (self.name, len(self.faces))
    if len(self.faces) > 1:
      return ret + repr(self.faces.values())
    else:
      return ret

