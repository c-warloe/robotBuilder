from svggen.api.component import Component
from svggen.library import getComponent

self = Component()

# TODO(mehtank): Allow constants to be inherited too?
self.addSubcomponent("prox","Beam", shape=3, phase=2, tangle=45, bangle=-45)
self.addSubcomponent("dist","Beam", shape=3, phase=2, tangle=45, bangle=45)
self.addSubcomponent("ext","Extension")

r = self.addParameter("ratio", 0.5)
l = self.addParameter("length", 100)
a = self.addParameter("angle", 0)

self.setSubParameter(("prox","length"), l / (1+r))
self.setSubParameter(("dist","length"), l * r / (1+r))

self.addConnection(("ext", "topedge"), ("prox","botedge"),angle=180)
self.addConnection(("prox", "topedge"), ("dist","botedge"),angle=a)

self.inheritInterface("botedge",("ext","botedge"))

self.toYaml("library/Finger.yaml")

c = getComponent("Finger")
for edge in c.composables['graph'].edges[:1]:
  print [x.subs(c.getAllSubs()) for x in edge.pts3D]

print 
c.setParameter("length", 100)
c.setParameter("ratio", 1)
c.setParameter("prox.q_a", 1)
c.setParameter("prox.q_i", 0)
c.setParameter("prox.q_j", 0)
c.setParameter("prox.q_k", 0)

'''
for face in c.composables['graph'].faces:
  print [x.subs(c.getAllSubs()) for x in face.get3DNormal()]
'''
for i,r in enumerate(c.getRelations()):
  print i, ":", r

