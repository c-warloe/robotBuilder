from svggen.api.component import Component

c = Component()

c.addSubcomponent("servo", "Servo", inherit="length depth width servo flip controller controllerPin label autoPoll".split(), prefix=None)
c.addSubcomponent("move", "FourBarLegs", inherit="height depth length flexwidth leg.beamwidth".split(), prefix=None)

c.addConstraint(("move", "flexlengthx"), "servo", '2*x.getParameter("hornheight")')

c.addConstConstraint(("servo", "faces"), range(4))
c.addConstConstraint(('servo', 'motionType'), 'continuous')
c.addConstConstraint(('servo', 'min'), -50)
c.addConstConstraint(('servo', 'default'), 0)
c.addConstConstraint(('servo', 'max'), 50)
c.addConstraint(("servo", "servoFunction"), "flip", "'input' if x else 'input*-1'")

c.inheritAllInterfaces("servo", prefix=None)

c.inheritInterface('legControl', ('servo', 'servoControl'))
c.interfaces.pop('servoControl')

c.addConnection(("servo", "slotedge"),
                ("move", "topedge"),
                angle = 0)
c.interfaces.pop('slotedge')

c.toYaml("library/MovingLegs.yaml")
