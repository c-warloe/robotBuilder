from svggen.api.component import Component


self = Component()

self.addSubcomponent("base", "TwoMovingLegs", inherit=True, prefix=None)
self.addSubcomponent("leg1", "PointedLeg")
self.addSubcomponent("leg2", "PointedLeg")
self.addSubcomponent("leg3", "PointedLeg")
self.addSubcomponent("leg4", "PointedLeg")

self.addConstraint(("leg1", "length"), "height")
self.addConstraint(("leg1", "top"), "depth")
self.addConstraint(("leg1", "beamwidth"), "leg.beamwidth")

self.addConstraint(("leg2", "length"), "height")
self.addConstraint(("leg2", "top"), "depth")
self.addConstraint(("leg2", "beamwidth"), "leg.beamwidth")
self.addConstConstraint(("leg2", "phase"), "True")

self.addConstraint(("leg3", "length"), "height")
self.addConstraint(("leg3", "top"), "depth")
self.addConstraint(("leg3", "beamwidth"), "leg.beamwidth")

self.addConstraint(("leg4", "length"), "height")
self.addConstraint(("leg4", "top"), "depth")
self.addConstraint(("leg4", "beamwidth"), "leg.beamwidth")
self.addConstConstraint(("leg4", "phase"), "True")

self.inheritInterface("slotedge", ("base", "slotedge"))

self.addConnection(("base", "topedge1"),
                   ("leg1", "top"),
                   angle=0)
self.addConnection(("base", "topedge3"),
                   ("leg2", "top"),
                   angle=0)
self.addConnection(("base", "botedge3"),
                   ("leg3", "top"),
                   angle=0)
self.addConnection(("base", "botedge1"),
                   ("leg4", "top"),
                   angle=0)

self.toYaml("library/SmallAntLegs.yaml")

'''
f = SmallAntLegs()

from svggen.utils.dimensions import tgy1370a

f.setParameter("servo", tgy1370a)
f.setParameter("height", 20)
f.setParameter("length", 55)
f.setParameter("leg.beamwidth", 5)

f.setParameter("depth", tgy1370a.getParameter('motorwidth'))
f.setParameter("width", tgy1370a.getParameter('motorheight') + 5)

f.makeOutput("output/smalllegs", protobuf=False, display=True)
'''
