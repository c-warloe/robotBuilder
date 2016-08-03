from svggen.api.Parameterized import Parameterized
from svggen.utils.mymath import Eq


class Port(Parameterized):
  """
  Abstract base class for a Port
  """
  def __init__(self, parent, params, name='', **kwargs):
    """
    :param parent: component that is holding this port
    :type parent: component
    :param params: parameters to initialize the Parameterized parameters with
    :type params: dict
    :param name: port name
    :type name: basestring
    :param kwargs: additional arguments to override params
    :type kwargs: dict
    """
    super(Port, self).__init__()

    # XXX TODO(mehtank): Figure out better default values
    self.isInput = False # True if self.valueFunction can be set via a connection from a port of a different component 
    self.isOutput = False # True if self.valueFunction can be completely determined by self.parent
    self.valueFunction = None 
    # self.inputFunction = None
    # self.outputFunction = None

    self.parent = parent
    self._allowableMates = []
    self._recommendedMates = []

    # By default these aren't symbolicized, because they will be set to symbolic expressions from their parent component
    for key, value in params.iteritems():
      self.addParameter(key, value, isSymbol=False)

    for key, value in kwargs.iteritems():
      self.setParameter(key, value)


  def prefix(self, prefix=""):
    # Override to handle prefixing
    pass

  def setInputValue(self, value):
    self.isInput = True
    self.isOutput = False
    self.valueFunction = lambda : value

  def setOutputFunction(self, fn):
    self.isInput = False
    self.isOutput = True
    self.valueFunction = fn

  def setDrivenFunction(self, fn):
    self.isInput = False
    self.isOutput = False
    self.valueFunction = fn

  def getValue(self, default=None):
    if self.valueFunction is None:
      return default
    return self.valueFunction()

  def canMate(self, otherPort):
    """
    If _allowableMates is an empty list, then returns if self and otherPort
    are the same class.  Otherwise, return if otherPort is an instance of
    any of _allowableMates

    Override this method for better matching
    :returns: whether this port can mate with another port
    :rtype: boolean
    """
    if len(self._allowableMates) > 0:
      for nextType in self._allowableMates:
        if isinstance(otherPort, nextType):
          return True
      return False
    return self.__class__ == otherPort.__class__


  def shouldMate(self, otherPort):
    # Override for better matching
    if not self.canMate(otherPort):
      return False
    if len(self._recommendedMates) > 0:
      for nextType in self._recommendedMates:
        if isinstance(otherPort, nextType):
          return True
    return False


  def addAllowableMate(self, mateType):
    if not isinstance(mateType, (list, tuple)):
      mateType = [mateType]
    for newType in mateType:
      # XXX what exactly does this check?
      if not isinstance(newType, type(self.__class__)):
          continue
      # If already have one that is a subclass of the desired one, do nothing
      for mate in self._allowableMates:
        if issubclass(mate, newType):
          # XXX why do we return instead of breaking and checking the rest?
          return
      # Remove any that are a superclass of the new one
      for mate in self._allowableMates:
        if issubclass(newType, mate):
          self._allowableMates.remove(mate)
      self._allowableMates.append(newType)


  def addRecommendedMate(self, mateType):
    if not isinstance(mateType, (list, tuple)):
      mateType = [mateType]
    for newType in mateType:
      if not isinstance(newType, type(self.__class__)):
          continue
      # If already have one that is a subclass of the desired one, do nothing
      for mate in self._recommendedMates:
        if issubclass(mate, newType):
          return None
      # Remove any that are a superclass of the new one
      for mate in self._recommendedMates:
        if issubclass(newType, mate):
          self._recommendedMates.remove(mate)
      self._recommendedMates.append(newType)

  def constrain(self, parent, toPort, **kwargs):
    """
    Return a set of semantic constraints to be satisfied when connecting to toPort object
    By default, constrain same-named parameters to be equal

    Override this method for better matching
    :returns: list of semantic constraints 
    :rtype: list
    """
    constraints = []
    for p in self.parameters:
      if p in toPort.parameters:
        if "offset_"+p in kwargs:
          constraints.append(Eq(self.getParameter(p)+kwargs["offset_"+p], toPort.getParameter(p)))
        else:
          constraints.append(Eq(self.getParameter(p), toPort.getParameter(p)))
    return constraints


  def setParent(self, newParent):
    self.parent = newParent


  def getParent(self):
    return self.parent


  def toString(self):
    return str(self.parent) + '.' + self.getName()


  def getCompatiblePorts(self):
    from svggen.api.ports import all_ports
    compat_ports = []
    for port in all_ports:
        if self.canMate(port(None)):
            compat_ports.append(port)
    return compat_ports

