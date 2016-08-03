from svggen.api.component import Component

###################
# Component builder
###################

c = Component()

### Subcomponents used in this assembly
c.addSubcomponent("servo", "ServoDevice", continuous = True)
c.addSubcomponent("mount", "RectBeam")

c.addConnection(('servo', 'mount'),
                ('mount', 'face2'))

c.inheritAllInterfaces("servo", prefix=None)
c.delInterface("mount")
c.inheritAllInterfaces("mount", prefix=None)
c.toYaml("library/Servo.yaml")
