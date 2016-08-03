from svggen.api.component import Component
from svggen.library import getComponent

self = Component()

# TODO(mehtank): Allow constants to be inherited too?
self.addSubcomponent("top","Rectangle")
self.addSubcomponent("bot","Rectangle")

l = self.addParameter("length", 100)

#self.addSemanticConstraint(self.getParameter("top.l"), '==', l/2)
#self.addSemanticConstraint(self.getParameter("bot.l"), '==', l/2)
self.setSubParameter(("top", "l"), l/2)
self.setSubParameter(("bot", "l"), l/2)

self.addConnection(("top", "b"), ("bot","t"),angle=-180)

self.inheritInterface("topedge",("top","t"))
self.inheritInterface("botedge",("bot","b"))

'''
print "** Pre-make"
for i,r in enumerate(self.getRelations()):
  print i, ":", r

self.make()

print
print "** post-make"
for i,r in enumerate(self.getRelations()):
  print i, ":", r

'''
self.toYaml("library/Extension.yaml")

print "** from YAML"
c = getComponent("Extension")

c.setParameter("bot.q_a", 1)
c.setParameter("bot.q_i", 0)
c.setParameter("bot.q_j", 0)
c.setParameter("bot.q_k", 0)
c.setParameter("bot.dx", 0)
c.setParameter("bot.dy", 0)
c.setParameter("bot.dz", 0)
c.setParameter("bot.w", 10)
c.setParameter("length", 33)

import sympy
eqns = []
for i,r in enumerate(c.getRelations()):
  if type(r) is sympy.Equality:
    print i, ":", r
    eqns.append(r)

print
import sympy
sol = sympy.solve(eqns)

for s in sol:
  print s
