from svggen.api.component import Component

self = Component()

self.addSubcomponent("servo","Servo", inherit="servo length width depth controller".split(), prefix=None)
self.addSubcomponent("hinge","Hinge")

self.addConstConstraint(("servo","phase"), 1)
self.addConstConstraint(("servo","center"), False)
self.addConstraint(("hinge","perimeter"), ("width", "depth"), "sum(x)*2")
self.addConstraint(("hinge","bot"), ("depth", "width"), "(x[1]-x[0]) * 1.0 / sum(x)")
self.addConstraint(("hinge","top"), ("depth", "width"), "(x[1]-x[0]) * 1.0 / sum(x)")

angles=[-35.25, 35.25, -35.25, 35.25]
for i in range(4):
  self.addConnection(("servo", "topedge%d" % i),
                     ("hinge","botedge%d" % (i+1)),
                     angle=angles[i])
  self.inheritInterface("botedge%d" % i, ("servo","botedge%d" % i))
  self.inheritInterface("topedge%d" % i, ("hinge","topedge%d" % (i+1)))

self.inheritInterface("botface",("servo","botface"))

self.toYaml("library/ActuatedHinge.yaml")
