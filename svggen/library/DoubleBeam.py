from svggen.api.component import Component


class DoubleBeam(Component):

  _test_params = {
    'shape': 3,
    'tangle': 45,
    'bangle': 45,
    'phase': 2,
  }

  def define(self, **kwargs):
    self.addConstant("shape", 3, **kwargs)
    self.addConstant("phase", 0, **kwargs)
    a = self.addParameter("angle", 0)

    self.addSubcomponent("leg1", "Beam", shape=self.getParameter("shape"), phase=self.getParameter("phase"))
    self.addSubcomponent("leg2", "Beam", shape=self.getParameter("shape"), phase=self.getParameter("phase"))

    self.addConnection(("leg1", "topedge"),
                       ("leg2", "botedge"), angle=a)

    self.inheritInterface("input", ("leg2", "topedge"))
    self.inheritInterface("output", ("leg1", "botedge"))


if __name__ == "__main__":
  from svggen.utils.utils import printSummary

  f = DoubleBeam(shape=4)
  f.toYaml("DoubleBeam.yaml")
  printSummary(f)

  '''
  f.setParameter("leg1.q_a", 1)
  for x in "roll yaw".split():
    f.setParameter("leg2." + x, 0)
  for x in "dx dy dz roll pitch yaw".split():
    f.setParameter("leg1." + x, 0)
  '''
  #for x in "dx dy dz q_i q_j q_k".split():
    #f.setParameter("leg1." + x, 0)
  #f.setParameter("leg2.q_a", 0)

  #f.setParameter("leg1.length", 100)
  #f.setParameter("leg1.beamwidth", 10)
  #f.setParameter("leg2.length", 50)

  '''
  print "~~~ Parameters:"
  for p, (n, v) in sorted(f.allParameters.iteritems(), key = lambda x: x[1][0]):
    print p, f.getVariableSub(p), [(x, p.assumptions0[x]) for x in p.assumptions0 if x not in "real complex hermitian imaginary commutative".split()]
  for v in sorted(f.getVariables(), key = lambda x: repr(x)):
    print v, [(x, v.assumptions0[x]) for x in v.assumptions0 if x not in "real complex hermitian imaginary commutative".split()]
  print
  '''

  '''
  print "~~~ Equations:"
  from svggen.utils.utils import schemeRepr, schemeList
  for i,c in enumerate(f.getRelations()):
    #print i, ":", repr(schemeList(c))
    print schemeRepr(schemeList(c))
    print c
    #print c.subs(f.getSubs())
  print
  print
  '''

  '''
  print "~~~ Solutions:"
  solns = sympy.solve(f.getRelations())
  for s in solns:
    print s
  '''
  '''
  arr = [5, 2,0]
  print arr
  r = [f.getRelations()[x] for x in arr]
  print 
  for c in r:
    print c
  print
  print sympy.solve(r)
  '''


  '''
  f.make()

  print f.getInterface("output").getEdges()
  print f.getInterface("output").getValue()
  f.getInterface("input").setInputValue(-10)
  print f.getInterface("output").getValue()

  f._make_test(protobuf=True)

  print f.getInterface("output").getValue()
  f.getInterface("input").setInputValue(-10)
  print f.getInterface("output").getValue()
  print f.composables["function"].ports
  print f.getInterface.func_code.co_varnames
  '''

