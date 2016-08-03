__author__ = 'Joseph'

from svggen.api.component import Component

c = Component()

# Add LED and Toggle switch
c.addSubcomponent('led', 'LED')
c.addSubcomponent('toggle', 'UIToggle')

# Deal with parameters
c.addParameter('label')
c.addParameter('controller')
c.addParameter('controllerPin')
c.addParameter('led.autoPoll')
c.addParameter('toggle.autoPoll')
c.addParameter('type')

c.addConstraint(('toggle', 'label'), 'label')
c.addConstraint(('led', 'controller'), 'controller')
c.addConstraint(('toggle', 'controller'), 'controller')
c.addConstraint(('led', 'controllerPin'), 'controllerPin')
c.addConstraint(('led', 'autoPoll'), 'led.autoPoll')
c.addConstraint(('toggle', 'newState.autoPoll'), 'toggle.autoPoll')
c.addConstraint(('led', 'type'), 'type')

# Deal with ports
c.addConnection(('led', 'control'), ('toggle', 'curState'))

c.inheritInterface("signal", ("led", "signal"))
c.inheritInterface("ground", ("led", "ground"))
c.inheritInterface("newToggleState", ("toggle", "newState"))

c.toYaml('library/ControlledLED.yaml')