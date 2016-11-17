class SetPackage:
  useNumpy = False

def useNumpy():
  SetPackage.useNumpy = True
def useSympy():
  SetPackage.useNumpy = False

def sum(a):
  from operator import add
  return reduce(add, a)

def cumsum(iterable):
  arr = [iterable[0]]
  for c in iterable[1:]:
    arr.append(arr[-1] + c)
  return arr

def differenceExceeds(pts1, pts2, tol):
  return difference(pts1, pts2) > tol

if SetPackage.useNumpy:
  from numpy import dot, array, linalg, transpose, cos, sin, tan, eye, diag, deg2rad, rad2deg, arctan2, arccos, pi, sqrt, round

  from numpy.linalg import norm

  def rows(x):
    return x.shape[0]
  
  def simplify(x):
    return x
  def N(x):
    return x

  def difference(pts1, pts2):
    return norm(array(pts1) - array(pts2))

else:
  from sympy import transpose, cos, sin, tan, eye, pi, sqrt, zeros, N
  from sympy import diag as sdiag
  from sympy import Matrix as array
  from sympy import atan2 as arctan2
  from sympy import acos as arccos
  from sympy import pprint
  from sympy import Symbol as sympySymbol
  from sympy import Dummy as sympyDummy
  from sympy.core.relational import Relational
  from sympy import *

  D = Function('D')

  class Symbol(sympySymbol):
    def __new__(cls, name, default=-1, commutative=True,**assumptions):
      obj = sympySymbol.__new__(cls,name,commutative=commutative,**assumptions)
      obj.default = default
      obj.isSolved = False
      obj.solvedValue = -1
      return obj

    def solved(self):
      return self.isSolved

    def setSolved(self, val):
      self.solvedValue = val
      self.isSolved = True

    def getValue(self):
      if self.solved():
        return self.solvedValue
      return self.default

    def __getstate__(self):
      state = sympySymbol.__getstate__(self)
      state['isSolved'] = self.isSolved
      state['default'] = self.default
      state['solvedValue'] = self.solvedValue
      return state

    def __setstate__(self, state):
      sympySymbol.__setstate__(self, state)
      self.isSolved = state['isSolved']
      self.default = state['default']
      self.solvedValue = state['solvedValue']

  class Dummy(sympyDummy,Symbol):
    def __new__(cls, name=None, default=-1, commutative=True, **assumptions):
      obj = sympyDummy.__new__(cls,name,commutative=commutative,**assumptions)
      obj.default = default
      obj.isSolved = False
      obj.solvedValue = -1
      return obj

    def solved(self):
      return self.isSolved

    def setSolved(self, val):
      self.solvedValue = val
      self.isSolved = True

    def getValue(self):
      if self.solved():
        return self.solvedValue
      return self.default

    def __getstate__(self):
      state = sympyDummy.__getstate__(self)
      state['isSolved'] = self.isSolved
      state['default'] = self.default
      state['solvedValue'] = self.solvedValue
      return state

    def __setstate__(self, state):
      sympyDummy.__setstate__(self, state)
      self.isSolved = state['isSolved']
      self.default = state['default']
      self.solvedValue = state['solvedValue']

  def deg2rad(x):
    return x * (pi / 180)

  def rad2deg(x):
    return x / (pi / 180)

  def dot(a, b):
    return a * b

  def norm(x):
    return array(x).norm()

  def diag(x):
    return sdiag(*x)

  def rows(x):
    return [x.row(i) for i in range(x.rows)]

  def round(x):
    return x.round()

  def difference(pts1, pts2):
    #XXX Hack to overcome precision errors
    from random import random
    pts1 = array(pts1)
    pts2 = array(pts2)

    syms = pts1.atoms(sympySymbol) | pts2.atoms(sympySymbol)
    subs = [(x, 100 + 100*random()) for x in syms]
    return norm(pts1 - pts2).subs(subs)
    
  array = Matrix
    
  def norm(x):
    if type(x) is tuple:
      x = Matrix(x)
    return x.norm()
        
  def rows(x):
    return x.rows
