
from svggen.api.component import Component

###################
# Component builder
###################

c = Component()

### Subcomponents used in this assembly
c.addSubcomponent("device", "LineDetectorDevice", inherit=False)
c.addSubcomponent("driver", "LineDetectorDriver", inherit=False)
c.addConstConstraint(('driver', 'drivenComponent'), 'device')

c.addParameter('controller')
c.addParameter('ledControllerPin')
c.addParameter('sensorControllerPin')

c.addConstraint(('device', 'ledSignal.controllerPin'), 'ledControllerPin')
c.addConstraint(('device', 'sensorSignal.controllerPin'), 'sensorControllerPin')
#
c.addConstraint(('device', 'controller'), 'controller')
c.addConstraint(('driver', 'controller'), 'controller')
#
#
# ### Exposed interfaces
c.inheritInterface("ledSignal", ("device", "ledSignal"))
c.inheritInterface("sensorSignal", ("device", "sensorSignal"))
c.inheritInterface("ground", ("device", "ground"))
c.inheritInterface("curValue", ("driver", "curValue"))
c.inheritInterface("seeLine", ("driver", "seeLine"))

c.toYaml("library/LineDetector.yaml")

