
from svggen.api.component import Component

###################
# Component builder
###################

c = Component()

### Subcomponents used in this assembly
c.addSubcomponent("device", "EServoDevice", inherit=False)
c.addSubcomponent("driver", "EServoDriver", inherit=False)
c.addConstConstraint(('driver', 'drivenComponent'), 'device')

c.addParameter('controller')
c.addParameter('controllerPin')
c.addParameter('motionType')
c.addParameter('autoPoll')

c.addConstraint(('device', 'signal.controllerPin'), 'controllerPin')
c.addConstraint(('device', 'controller'), 'controller')
c.addConstraint(('driver', 'controller'), 'controller')
c.addConstraint(('driver', 'motionType'), 'motionType')
c.addConstraint(('driver', 'control.autoPoll'), 'autoPoll')


### Exposed interfaces
c.inheritInterface("signal", ("device", "signal"))
c.inheritInterface("power", ("device", "power"))
c.inheritInterface("ground", ("device", "ground"))
c.inheritInterface("control", ("driver", "control"))

c.toYaml("library/EServo.yaml")

