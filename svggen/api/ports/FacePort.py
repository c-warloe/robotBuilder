from SixDOFPort import SixDOFPort

class FacePort(SixDOFPort):
  def __init__(self, parent, face):
    self.face = parent.getGraph().getFace(face)
    SixDOFPort.__init__(self, parent, self.face)

  def getFaceName(self):
    return self.face.name

  def getPts(self):
    pts = self.face.get3DCoords()
    return [pts[:,x] for x in range(len(pts[0,:]))]

  def toString(self):
    return str(self.face.name)

  def canMate(self, otherPort):
    try:
      return (otherPort.getDecoration() is not None)
    except AttributeError:
      return False
