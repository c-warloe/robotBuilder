from svggen.api.component import Component
from svggen.api.Function import Function

self = Component()

self.addSubcomponent("bot", "Tetrahedron")
self.addSubcomponent("top", "Tetrahedron")

self.addParameter("angle", 0)
self.addParameter("top", 0)
self.addParameter("bot", 0)
self.addParameter("tetherwidth", 0)
self.addParameter("tetheroffset", 0)
self.addParameter("perimeter")

self.addConstraint(("top", "perimeter"), "perimeter")
self.addConstraint(("top", "start"), "top")
self.addConstConstraint(("top", "end"), 1)
self.addConstConstraint(("bot", "start"), 1)
self.addConstraint(("bot", "end"), "bot")
self.addConstraint(("bot", "perimeter"), "perimeter")

self.addConstraint(("top", "tetherwidth"), "tetherwidth")
self.addConstraint(("bot", "tetherwidth"), "tetherwidth")
self.addConstraint(("top", "tetheroffset"), "tetheroffset")
self.addConstraint(("bot", "tetheroffset"), "tetheroffset")

# XXX Hack : makes things awkward with different fractions in and out
self.addConstraint(("top", "min"), ("top", "bot"), "min(x)")
self.addConstraint(("bot", "min"), ("top", "bot"), "min(x)")

angles = ["-70.5+x", "70.5", "-70.5-x", "70.5", "-70.5+x"]
for i in range(5):
  self.addConnection(("top", "endedge%d" % i),
                     ("bot", "startedge%d" % i),
                     angle=Function(params="angle", fnstring=angles[i]))
  self.inheritInterface("topedge%d" % i, ("top", "startedge%d" % i))
  self.inheritInterface("botedge%d" % i, ("bot", "endedge%d" % i))

self.toYaml("library/Hinge.yaml")
