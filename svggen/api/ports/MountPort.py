from Port import  Port

class MountPort(Port):
  def __init__(self, parent, decoration):
    Port.__init__(self, parent, {})
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

