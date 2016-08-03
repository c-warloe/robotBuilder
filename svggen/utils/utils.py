def prefix(s1, s2):
  if s1 and s2:
    return s1 + "_" + s2
  return s1 or s2

def tryImport(module, attribute):
  try:
    mod = __import__(module, fromlist=[attribute])
    obj = getattr(mod, attribute)
    return obj
  except ImportError:
    mod = __import__("svggen.library." + module, fromlist=[attribute])
    obj = getattr(mod, attribute)
    return obj

def decorateGraph(face, decoration, offset=(0, 0), offset_dx=None, offset_dy=None, rotate=False, mode=None):
  try:
    faces = decoration.faces
  except AttributeError:
    faces = [decoration]

  if mode is None:
    mode = "hole"

  if offset_dx is not None and offset_dy is not None:
    offset = (offset_dx, offset_dy)

  for f in faces:
    if rotate:
      face.addDecoration(([(p[1]+offset[0], p[0]+offset[1]) for p in f.pts2d], mode))
    else:
      face.addDecoration(([(p[0]+offset[0], p[1]+offset[1]) for p in f.pts2d], mode))

def schemeString(expr, prefix=""):
  if expr.is_Number or expr.is_Symbol or expr.is_NumberSymbol:
    print prefix, repr(expr)
    return
  elif expr.is_Add:
    print prefix, "( +"
  elif expr.is_Mul:
    print prefix, "( *"
  elif expr.is_Pow:
    print prefix, "( ^"
  else:
    print prefix, "(", type(expr)

  for a in expr.args:
    printPrefix(a, "  " + prefix)
  print prefix, ")"

def schemeList(expr):
  if expr.is_Rational and expr.q != 1:
    return ["/", repr(expr.p), repr(expr.q)]
  elif expr.is_Number or expr.is_Symbol or expr.is_NumberSymbol:
    return repr(expr)
    
  elif expr.is_Add:
    elist = ["+"]
  elif expr.is_Mul:
    elist = ["*"] 
  elif expr.is_Pow:
    elist = ["^"] 
  elif expr.is_Equality:
    elist = ["=="] 
  elif expr.is_Relational:
    elist = [expr.rel_op] 
  else:
    elist = [repr(type(expr))]
    
  for a in expr.args:
    elist.append(schemeList(a))
  
  return elist

def schemeRepr(elist):
  if isinstance(elist, (list, tuple)):
    string = "( "
    string += " ".join(map(schemeRepr, elist))
    string += " )"
  else:
    string = elist
  return string

def printSummary(f):
  print "~~~ Parameters:"
  for v in sorted(f.getVariables(), key = lambda x: repr(x)):
    print v#, [(x, v.assumptions0[x]) for x in v.assumptions0 if x not in "real complex hermitian commutative imaginary".split()]
  print

  print "~~~ Equations:"
  for i,c in enumerate(f.getRelations()):
    print schemeRepr(schemeList(c))
  print 
  '''
  for i,c in enumerate(f.getRelations()):
    print i, ":", c
  print
  '''
  print

def printParameters(f):
  for v in sorted(f.getVariables(), key = lambda x: repr(x)):
    print v

def printEquations(f):
  for i,c in enumerate(f.getRelations()):
    print c
  print

