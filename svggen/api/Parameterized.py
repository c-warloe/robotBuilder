import svggen.utils.mymath as math
from svggen.utils.utils import prefix as prefixString
from sympy import Symbol


class Parameterized(object):
  """
  Like a dictionary k/v store, but we require special syntax constructs
  to set/update keys 

  Parameters are symbolic by default
  """
  def __init__(self):
    self._name = None
    self.parameters = {}
    self.allParameters = {}
    self.constraints = []
    self.semanticConstraints = []
    self.localSemanticConstraints = []
    self.subs = {}


  def getName(self):
    return self._name if self._name is not None else str(self.__class__)

  def setName(self, name):
    self._name = name

  def addParameter(self, name, value, isSymbol=True, **kwargs):
    """
    Adds a k/v pair to the internal store if the key has not been added before
    Raises KeyError if the key has been added before
    """
    if name in self.parameters:
      raise KeyError("Parameter %s already exists" % name)
    if "." in name:
      raise ValueError("Invalid character '.' in parameter name " + name)

    if isSymbol:
      p = math.Dummy(name, default=value, real=True, **kwargs)
      self.parameters.setdefault(name, p)
      self.allParameters[p] = (name, None)
    else:
      self.parameters.setdefault(name, value)

    return self.getParameter(name)

  def setParameter(self, n, v, forceConstant=False):
    """
    Sets a k/v pair to the internal store if the key has been added previously
    Raises KeyError if the key has not been added before
    """
    subs = {y.name: x for (x, y) in self.getVariableSubs().iteritems()}
    for s in v.atoms(Symbol):
      v = v.subs(s, subs[s.name])
    if n in self.parameters:
      if isinstance(self.parameters[n], math.Symbol):
        #self.addSemanticConstraint(self.parameters[n], "==", v)
        self.subs[n] = (self.parameters[n], v)
      else:
        if forceConstant:
          self.parameters[n] = v
        else:
          raise ValueError("Cannot set constant parameter: ", self.getName(), name)
    elif n in (x[0] for x in self.allParameters.values()):
        for p, (name, value) in self.allParameters.iteritems():
          if n == name:
            self.subs[n] = (p, v)
            #self.addSemanticConstraint(p, "==", v)
      
    else:
      raise KeyError("Parameter %s not initialized" % n)


  def getParameter(self, name, strict=True):
    """
    Retrieves the parameter value with the given name
    Raises KeyError if the key is not been set
    """
    try:
      if strict and self.parameters[name] is None:
        raise KeyError("Parameter %s not yet set" % name)
    except KeyError:
      if name in (x[0] for x in self.allParameters.values()):
        for p, (n, v) in self.allParameters.iteritems():
          if name == n:
            return p
      raise KeyError("Parameter %s does not exist" % name)
    return self.parameters[name]


  def hasParameter(self, name):
    return name in self.parameters

  def inheritParameters(self, other, prefix):
    for p, (n, v) in other.allParameters.iteritems():
      self.allParameters[p] = (prefixString(prefix, n), None)
    for n, (p, v) in other.subs.iteritems():
      self.subs[prefixString(prefix, n)] = (p, v)

  def delParameter(self, name):
    self.parameters.pop(name)

  def printAllSolutions(self):
    r = self.getRelations()
    print "repr(r) = ", repr(r)
    for p in self.parameters:
      if isinstance(self.getParameter(p), math.Symbol):
        print "math.solve(r, p = %s) = " % p, math.solve(self.getRelations(), self.getParameter(p))

  def getSolution(self, p):
    return math.solve(self.getRelations(), self.getParameter(p))

  def getVariableSub(self, p):
    (n, v) = self.allParameters[p]
    if not v:
      v = math.Symbol(n, default=p.default, **p.assumptions0)
      self.allParameters[p] = (n, v)
    return v

  def getVariableSubs(self):
    d = {}
    for p in self.allParameters:
      d[p] = self.getVariableSub(p)
    return d

  def getAllSubs(self):
    d = {}
    for p in self.allParameters:
      d[p] = self.getVariableSub(p)
    #for p in sorted(self.subs.iteritems(), reverse=True, key=lambda x : x[0].count('.')):
    #  d[p[1][0]] = p[1][1].subs(self.getVariableSubs())
    return d

  def getVariables(self):
    for p in self.allParameters:
      yield self.getVariableSub(p)

  def setVariableSolved(self, name, val):
    p = self.getParameter(name)
    if not isinstance(p,math.Symbol):
      return
    p.setSolved(val)
    pSub = self.allParameters[p][1]
    if pSub:
      pSub.setSolved(val)

  def getVariableValue(self, name):
    p = self.getParameter(name)
    if not isinstance(p,math.Symbol):
      return p
    return p.getValue()

  def fixVariable(self, name, val):
    p = self.getParameter(name)
    if not isinstance(p,math.Symbol):
      return
    p.fixValue(val)
    pSub = self.allParameters[p][1]
    if pSub:
      pSub.fixValue(val)
    self.setVariableSolved(name, val)

  def unfixVariable(self, name):
    p =self.getParameter(name)
    if not isinstance(p,math.Symbol):
      return
    p.unfix()
    pSub = self.allParameters[p][1]
    if pSub:
      pSub.unfix()

  def getAllConstraints(self):
    r = []

    for v in self.getVariables():
      # XXX Is this legit?
      known = "real complex hermitian imaginary commutative \
        positive negative zero nonnegative nonpositive nonzero"
      for name, assume in v.assumptions0.iteritems():
        if assume and name not in known.split():
          f = math.Function(name)
          #r.append(f(v))

      if v.assumptions0.get("positive", False):
        r.append(math.Relational(v, 0, ">",evaluate=False).subs(self.getAllSubs()))
      elif v.assumptions0.get("negative", False):
        r.append(math.Relational(v, 0, "<",evaluate=False).subs(self.getAllSubs()))
      elif v.assumptions0.get("zero", False):
        r.append(math.Eq(v, 0,evaluate=False).subs(self.getAllSubs()))
      elif v.assumptions0.get("nonnegative", False):
        r.append(math.Relational(v, 0, ">=",evaluate=False).subs(self.getAllSubs()))
      elif v.assumptions0.get("nonpositive", False):
        r.append(math.Relational(v, 0, "<=",evaluate=False).subs(self.getAllSubs()))
      elif v.assumptions0.get("nonzero", False):
        r.append(math.Relational(v, 0, "!=",evaluate=False).subs(self.getAllSubs()))
    
    for c in self.getConstraints():
      r.append(c.subs(self.getAllSubs()))

    return r


  def getRelations(self):
    r = []

    for c in self.getSemanticConstraints():
      r.append(c.subs(self.getAllSubs()))

    return r

  def getSemanticConstraints(self):
    return self.semanticConstraints
  
  def getConstraints(self):
    return self.constraints

  def addConstraint(self, exp):
    self.constraints.append(exp)

  def addSemanticConstraint(self, exp):
    self.localSemanticConstraints.append(exp) 
    self.semanticConstraints.append(exp)

  def extendConstraints(self, constraints):
    self.constraints.extend(constraints)

  def extendSemanticConstraints(self, constraints):
    self.semanticConstraints.extend(constraints)

