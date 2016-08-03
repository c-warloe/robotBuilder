from svggen.api.component import Component

self = Component()

self.addSubcomponent("servo","Servo", inherit="servo length width depth controller".split(), prefix=None)
self.addSubcomponent("gripper","Gripper", inherit="fingerlength fingerwidth width depth ratio".split(), prefix=None)

self.addConstConstraint(("servo","phase"), 1)
self.addConstConstraint(("servo","center"), False)

angles=[35.25, -35.25, 35.25, -35.25]
for i in range(3):
  self.addConnection(("servo", "topedge%d" % i),
                     ("gripper","botedge%d" % (i+1)),
                     angle=angles[i])
  self.inheritInterface("botedge%d" % i,("servo","botedge%d" % i))
self.inheritInterface("botedge3",("servo","botedge3"))

self.inheritInterface("botface",("servo","botface"))

self.toYaml("library/ActuatedGripper.yaml")
