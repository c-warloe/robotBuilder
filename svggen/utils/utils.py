import collections
import functools

class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache:
         return self.cache[args]
      else:
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)

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
    try:
      mod = __import__("svggen.library." + module, fromlist=[attribute])
      obj = getattr(mod, attribute)
      return obj
    except ImportError:
      mod = __import__("svggen.api." + module, fromlist=[attribute])
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

@memoized
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

