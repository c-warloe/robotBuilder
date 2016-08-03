from svggen.api.component import Component


self = Component()

self.addSubcomponent("leg1", "FourBarDoubleLeg", inherit=True, prefix=None)
self.addSubcomponent("leg2", "FourBarDoubleLeg", inherit=True, prefix=None)
self.addSubcomponent("topsplit", "SplitEdge")
self.addSubcomponent("botsplit", "SplitEdge")

self.delParameter("phase")

self.addConstConstraint(("leg1", "phase"), False)
self.addConstConstraint(("leg2", "phase"), True)

self.addConstraint(("topsplit", "botlength"), ("flexwidth", "length"), " (x[1],)")
self.addConstraint(("topsplit", "toplength"), ("flexwidth", "length"), " (x[0], x[1]-2*x[0], x[0])")

self.addConstraint(("botsplit", "botlength"), ("flexwidth", "length"), " (x[1],)")
self.addConstraint(("botsplit", "toplength"), ("flexwidth", "length"), " (x[0], x[1]-2*x[0], x[0])")

self.addConnection(("topsplit", "topedge0"),
                   ("leg1", "topedge"),
                   angle=0)
self.addConnection(("topsplit", "topedge2"),
                   ("leg2", "botedge"),
                   angle=0)

self.addConnection(("leg1", "botedge"),
                   ("botsplit", "topedge2"),
                   angle=0)
self.addConnection(("leg2", "topedge"),
                   ("botsplit", "topedge0"),
                   angle=0)

self.inheritInterface("topedge", ("topsplit", "botedge0"))
self.inheritInterface("botedge", ("botsplit", "botedge0"))

self.toYaml("library/TwoFourBarLegs.yaml")

'''
f = TwoFourBarLegs()

f.setParameter("flexlengthx", 20)
f.setParameter("flexwidth", 5)
f.setParameter("depth", 9)
f.setParameter("height", 25)
f.setParameter("length", 40)
f.setParameter("dl", 10)
f.setParameter("leg.beamwidth", 5)

f.makeOutput("output/fourbar", protobuf=False, display=True)
'''
