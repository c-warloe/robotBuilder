
from svggen.api.component import Component

###################
# Component builder
###################

c = Component()

### Subcomponents used in this assembly
c.addSubcomponent("device", "DistanceSensorDevice", inherit=False)
c.addSubcomponent("driver", "DistanceSensorDriver", inherit=False)
c.addConstConstraint(('driver', 'drivenComponent'), 'device')

c.addParameter('controller')
c.addParameter('controllerPin')

c.addConstraint(('device', 'signal.controllerPin'), 'controllerPin')
c.addConstraint(('device', 'controller'), 'controller')
c.addConstraint(('driver', 'controller'), 'controller')

### Exposed interfaces
c.inheritInterface("signal", ("device", "signal"))
c.inheritInterface("power", ("device", "power"))
c.inheritInterface("ground", ("device", "ground"))
c.inheritInterface("curValue", ("driver", "curValue"))

c.toYaml("library/DistanceSensor.yaml")

