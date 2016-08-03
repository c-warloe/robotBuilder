from svggen.api.MechanicalComponent import MechanicalComponent

###################
# Component builder
###################

c = MechanicalComponent()

### Subcomponents used in this assembly
#What pieces do we need in our object?
# faces parameter: effectively don't add tabs to beam
c.addSubcomponent("bar", "RectBeam", faces=range(4)) 
c.addSubcomponent("leg1", "PointedLeg")
c.addSubcomponent("leg2", "PointedLeg")
c.addSubcomponent("legsplit", "SplitEdge", splits=(3,1))
c.addSubcomponent("barsplit", "SplitEdge", splits=(3,1))

### New free parameters specific to this assembly
#Make parameters for composite object
c.addParameter("depth", 9)
c.addParameter("height", 50)
c.addParameter("length", 47)
c.addParameter("legwidth", 10)

### Subcomponent parameter inheritance
#Define parameters of subcomponents in terms of super parameters

# Constrain one length of the RectBeam object based on new FixedLegs parameter
c.addConstraint(("bar", "length"), "length")
# Constrain one parameter of the RectBeam object based on PointedLeg parameter
c.addConstraint(("bar", "depth"), "depth")
# Constrain other parameter of the RectBeam object based on new FixedLegs parameter
# c.addConstraint(("bar", "width"), "legwidth")

# Constrain one parameter of the PointedLeg object based on new FixedLegs parameter
c.addConstraint(("leg1", "length"), "height")
# Constrain one parameter of the RectBeam object based on PointedLeg parameter
c.addConstraint(("leg1", "frontwidth"), "legwidth")
c.addConstraint(("leg1", "rightwidth"), "legwidth")

# Constrain one parameter of the PointedLeg object based on new FixedLegs parameter
c.addConstraint(("leg2", "length"), "height")
# Constrain one parameter of the RectBeam object based on PointedLeg parameter
c.addConstraint(("leg2", "frontwidth"), "legwidth")
c.addConstraint(("leg2", "rightwidth"), "legwidth")

'''
# Break apart the edge where the two PointedLegs will connect
c.addConstraint(("legsplit", "botlength"), ("length", "leg.beamwidth"), "(x[0],)")
c.addConstraint(("legsplit", "toplength"), ("length", "leg.beamwidth"), "(x[1], x[0] - 2*x[1], x[1])")

# Break apart the edge where the two PointedLegs will connect
c.addConstraint(("barsplit", "botlength"), ("length", "leg.beamwidth"), "(x[0],)")
c.addConstraint(("barsplit", "toplength"), ("length", "leg.beamwidth"), "(x[1], x[0] - 2*x[1], x[1])")
'''

### Exoposed interfaces
# Locations on FixedLegs component that higher order components can use for assembly
# Supercomponent can only use subcomponent interfaces
# Start out by inheriting all of them from RectBeam
c.inheritAllInterfaces("bar", prefix=None)
c.inheritInterface("foot1", ("leg1", "foot"))
c.inheritInterface("foot2", ("leg2", "foot"))

### Subcomponents connections
# SplitEdge component to define multiple attachment points
#Connections are only on interfaces - interfaces MUST be defined in subcomponents
c.addConnection(("bar", "slotedge"),
                ("barsplit", "botedge0"),
                angle=0)
# Remove consumed interface 
# XXX should automatically do this
c.interfaces.pop("slotedge")
c.addConnection(("bar", "tabedge"),
                ("legsplit", "botedge0"),
                angle=0)
c.interfaces.pop("tabedge")
# Attach one leg
c.addConnection(("legsplit", "topedge2"),
                ("leg1", "front"),
                angle=0)
# Attach other leg
c.addConnection(("legsplit", "topedge0"),
                ("leg2", "right"),
                angle=0)

# Add tabs for rigid attachment
c.addConnection(("leg1", "right"),
                ("bar", "botedge0"),
                angle=90, tabWidth=6)
c.interfaces.pop("botedge0")

c.addConnection(("leg2", "front"),
                ("bar", "topedge0"),
                angle=90, tabWidth=6)
c.interfaces.pop("topedge0")

c.addConnection(("barsplit", "topedge1"),
                ("legsplit", "topedge1"),
                angle=90, tabWidth=9)

c.toYaml("library/FixedLegs.yaml")

