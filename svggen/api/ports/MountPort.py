from SixDOFPort import SixDOFPort

class MountPort(SixDOFPort):
  def __init__(self, parent, decoration):
    SixDOFPort.__init__(self, parent, parent)
    self.decoration = decoration

  def getDecoration(self):
    return self.decoration

  def toString(self):
    print "decoration"

  def canMate(self, otherPort):
    try:
      return (otherPort.getFaceName() is not None)
    except AttributeError:
      return False

