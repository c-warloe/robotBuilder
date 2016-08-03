
from svggen.api.component import Component

###################
# Component builder
###################

c = Component()

### Subcomponents used in this assembly
c.addSubcomponent("device", "LEDDevice", inherit=False)
c.addSubcomponent("driver", "LEDDriver", inherit=False)
c.addConstConstraint(('driver', 'drivenComponent'), 'device')

c.addParameter('controller')
c.addParameter('controllerPin')
c.addParameter('type')
c.addParameter('autoPoll')

c.addConstraint(('device', 'type'), 'type')
c.addConstraint(('driver', 'type'), 'type')
c.addConstraint(('device', 'signal.controllerPin'), 'controllerPin')
c.addConstraint(('device', 'controller'), 'controller')
c.addConstraint(('driver', 'control.autoPoll'), 'autoPoll')
c.addConstraint(('driver', 'controller'), 'controller')

### Exposed interfaces
c.inheritInterface("signal", ("device", "signal"))
c.inheritInterface("ground", ("device", "ground"))
c.inheritInterface("control", ("driver", "control"))

c.toYaml("library/LED.yaml")

