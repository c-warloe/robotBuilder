from svggen.api.component import Component


self = Component()

_test_params = {
  'thickness': 10,
  'stemwidth': 50,
  'crosswidth': 30,
  'stemlength': 150,
  'leftlength': 50,
  'rightlength': 100,
}

# Subcomponents used in this assembly
self.addSubcomponent("stem", "RectBeam")
self.addSubcomponent("left", "RectBeam")
self.addSubcomponent("right", "RectBeam")
self.addSubcomponent("t", "TJoint")

# New free parameters specific to this assembly are added
self.addParameter("stemlength")
self.addParameter("leftlength")
self.addParameter("rightlength")
self.addParameter("thickness")
self.addParameter("stemwidth")
self.addParameter("crosswidth")

### Set specific relationships between parameters
self.addConstraint(("stem", "depth"), "thickness")
self.addConstraint(("stem", "width"), "stemwidth")
self.addConstraint(("stem", "length"), "stemlength")

self.addConstraint(("left", "depth"), "thickness")
self.addConstraint(("left", "width"), "crosswidth")
self.addConstraint(("left", "length"), "leftlength")

self.addConstraint(("right", "depth"), "thickness")
self.addConstraint(("right", "width"), "crosswidth")
self.addConstraint(("right", "length"), "rightlength")

self.addConstraint(("t", "thickness"), "thickness")
self.addConstraint(("t", "crosswidth"), "crosswidth")
self.addConstraint(("t", "stemwidth"), "stemwidth")

for i in range(3):
  self.addConnection(("t", "leftedge%d" % i),
                     ("left", "botedge%d" % i), angle=0)
  self.addConnection(("t", "rightedge%d" % i),
                     ("right", "topedge%d" % i), angle=0)
self.addConnection(("t", "stemedge"),
                   ("stem", "topedge0"), angle=0)
self.addConnection(("t", "stemtab"),
                   ("stem", "topedge2"),
                   angle=0, tabWidth=10)

self.inheritInterface("stemface", ("stem", "botface"))
self.inheritInterface("leftface", ("left", "topface"))
self.inheritInterface("rightface", ("right", "botface"))

self.toYaml("library/TBar.yaml")
