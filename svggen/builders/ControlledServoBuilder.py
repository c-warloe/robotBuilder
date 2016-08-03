from svggen.api.component import Component

###################
# Component builder
###################

c = Component()

### Subcomponents used in this assembly
c.addSubcomponent("servo", "EServo", inherit=True, prefix=None)
c.addSubcomponent("slider", "UISlider", inherit=True, prefix=None)
c.addSubcomponent('dataFunction', 'DataFunction', inherit="controller", prefix=None)

c.addParameter('servoFunction')
c.addConstraint(('dataFunction', 'function'), 'servoFunction')

c.addConnection(('servo', 'control'),
                ('dataFunction', 'output'))
c.addConnection(('dataFunction', 'input'),
                ('slider', 'curPosition'))

c.inheritInterface('servoControl', ('dataFunction', 'input'))
c.inheritInterface('signal', ('servo', 'power'))
c.inheritInterface('power', ('servo', 'power'))
c.inheritInterface('ground', ('servo', 'ground'))
c.toYaml("library/ControlledServo.yaml")

c = Component()

c.addSubcomponent("servo", "ControlledServo", inherit=True, prefix=None)
c.addSubcomponent("mount", "ServoMount", inherit=True, prefix=None)

c.inheritAllInterfaces("mount", prefix=None)
c.inheritAllInterfaces("servo", prefix=None)

c.toYaml("library/Servo.yaml")
