from svggen.api.component import Component


_test_params = {
  'thickness': 10,
  'stemwidth': 20,
  'crosswidth': 30,
  'leftlength': 50,
  'rightlength': 100,
}

self = Component()

# Subcomponents used in this assembly
self.addSubcomponent("stem", "Hinge")
self.addSubcomponent("left", "RectBeam")
self.addSubcomponent("right", "RectBeam")
self.addSubcomponent("t", "TJoint")

# New free parameters specific to this assembly are added
self.addParameter("leftlength")
self.addParameter("rightlength")

self.addParameter("stemwidth")
self.addParameter("crosswidth")
self.addParameter("thickness")

### Set specific relationships between parameters
self.addConstraint(("stem", "perimeter"), ("stemwidth", "thickness"), "2 * sum(x)")
self.addConstraint(("stem", "top"), ("stemwidth", "thickness"), "(x[1]-x[0]) * 1.0 / sum(x)")
self.addConstraint(("stem", "bot"), ("stemwidth", "thickness"), "(x[1]-x[0]) * 1.0 / sum(x)")

self.addConstraint(("left", "depth"), ("thickness"))
self.addConstraint(("left", "width"), ("crosswidth"))
self.addConstraint(("left", "length"), ("leftlength"))

self.addConstraint(("right", "depth"), ("thickness"))
self.addConstraint(("right", "width"), ("crosswidth"))
self.addConstraint(("right", "length"), ("rightlength"))

self.addConstraint(("t", "thickness"), "thickness")
self.addConstraint(("t", "crosswidth"), "crosswidth")
self.addConstraint(("t", "stemwidth"), "stemwidth")

for i in range(3): 
  self.addConnection(("t", "leftedge%d" % i),
                     ("left", "botedge%d" % i), angle=0)
  self.addConnection(("t", "rightedge%d" % i),
                     ("right", "topedge%d" % i), angle=0)
self.addConnection(("t", "stemedge"),
                   ("stem", "topedge1"),
                   angle=(-70.5/2))
# XXX Not well shaped -- leaves overhang
self.addConnection(("t", "stemtab"),
                   ("stem", "topedge3"),
                   tabWidth=10, angle=(-70.5/2))

# Define interface locations in terms of subcomponent interfaces
for i in range(4):
  self.inheritInterface("stemedge%d" % i, ("stem", "botedge%d" % i))
self.inheritInterface("lefttab", ("left", "tabedge"))
self.inheritInterface("leftface", ("left", "topface"))
self.inheritInterface("rightface", ("right", "botface"))

self.toYaml("library/Fulcrum.yaml")
