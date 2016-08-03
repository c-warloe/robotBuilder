from svggen.api.component import Component

###################
# Component builder
###################

c = Component()

### Subcomponents used in this assembly
c.addSubcomponent("device", "BluetoothModuleDevice")
c.addSubcomponent("driver", "BluetoothModuleDriver")
c.addConstConstraint(('driver', 'drivenComponent'), 'device')

c.addParameter('controller')
c.addParameter('TX.controllerPin')
c.addParameter('RX.controllerPin')

c.addConstraint(('device', 'TX.controllerPin'), 'TX.controllerPin')
c.addConstraint(('device', 'RX.controllerPin'), 'RX.controllerPin')
c.addConstraint(('device', 'controller'), 'controller')
c.addConstraint(('driver', 'controller'), 'controller')

### Exposed interfaces
c.inheritInterface("TX", ("device", "TX"))
c.inheritInterface("RX", ("device", "RX"))
c.inheritInterface("VCC", ("device", "VCC"))
c.inheritInterface("ground", ("device", "ground"))

c.toYaml("library/BluetoothModule.yaml")

