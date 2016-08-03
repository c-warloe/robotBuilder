from svggen.api.component import Component

c = Component()

c.addSubcomponent("base","Brains")
c.addSubcomponent("joint1","ActuatedHinge", inherit=("servo, controller"), prefix=None)
c.addSubcomponent("joint2","ActuatedHinge", inherit=("servo, controller"), prefix=None)
c.addSubcomponent("tool","ActuatedGripper", inherit=("servo, controller"), prefix=None)

c.addConstraint(("base","brain"), "controller")
c.addConstraint(("base","length"), "controller", "x.getDimension('length')")

c.addConstraint(("joint1","length"), "controller", "75-x.getDimension('length')")
c.addConstraint(("joint1","width"), "controller", "x.getDimension('width')")
c.addConstraint(("joint1","depth"), "controller", "x.getDimension('height')")

c.addConstConstraint(("joint2","length"), 75)
c.addConstraint(("joint2","width"), "controller", "x.getDimension('width')")
c.addConstraint(("joint2","depth"), "controller", "x.getDimension('height')")

c.addConstConstraint(("tool","length"), 75)
c.addConstraint(("tool","width"), "controller", "x.getDimension('width')")
c.addConstraint(("tool","depth"), "controller", "x.getDimension('height')")
c.addConstConstraint(("tool","fingerlength"), 40)
c.addConstConstraint(("tool","fingerwidth"), 5)

for i in range(3):
  c.addConnection(("base", "topedge%d" % i), ("joint1","botedge%d" % i))

angles=[-35.25, 35.25, -35.25, 35.25]
for i in range(4):
  c.addConnection(("joint1", "topedge%d" % i), ("joint2","botedge%d" % i), angle=angles[i])
  c.addConnection(("joint2", "topedge%d" % i), ("tool","botedge%d" % i),angle=angles[i])

c.inheritInterface("botface",("base","topface"))

c.toYaml("library/Arm.yaml")
