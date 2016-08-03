from svggen.api.component import Component

c = Component()

c.addSubcomponent("fixed", "FixedLegs", inherit=("height", "leg.beamwidth"), prefix=None)
c.addSubcomponent("move", "MovingLegs", inherit=True, prefix=None)

c.addConstraint(("fixed", "depth"), "servo", "x.getParameter('motorwidth')")
c.addConstraint(("fixed", "length"), "width")

c.addConstraint(("move", "depth"), "servo", "x.getParameter('motorwidth')")
c.addConstraint(("move", "width"), "servo", "x.getParameter('motorheight')")

c.inheritInterface("botface", ("fixed", "botface"))
for i in range(1,4):
  c.inheritInterface("botedge%d" % i, ("fixed", "botedge%d" % i))

c.inheritInterface("topface", ("move", "topface"))
for i in range(4):
  c.inheritInterface("topedge%d" % i, ("move", "topedge%d" % i))

c.inheritInterface("legControl", ("move", "legControl"))
c.inheritInterface("signal", ("move", "signal"))
c.inheritInterface("power", ("move", "power"))
c.inheritInterface("ground", ("move", "ground"))

c.toYaml("library/LegPair.yaml")
