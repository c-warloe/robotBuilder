__author__ = 'Joseph'

from svggen.api.component import Component

# TODO use existing Seg in a better way / better way to inherit parameters (without getting the prefix)?

c = Component()
c.addSubcomponent('seg', 'Seg', inherit=False)
c.addParameter('length')
c.addParameter('height')
c.addParameter('driveservo')
c.addParameter('tailservo')
c.addParameter('controller')

c.addConstraint(('seg', 'length'), 'length')
c.addConstraint(('seg', 'height'), 'height')
c.addConstraint(('seg', 'driveservo'), 'driveservo')
c.addConstraint(('seg', 'tailservo'), 'tailservo')
c.addConstraint(('seg', 'controller'), 'controller')

c.addSubcomponent('distanceSensor', 'DistanceSensor', inherit=True)
c.addConstraint(('distanceSensor', 'controller'), 'controller')
c.addConstConstraint(('distanceSensor', 'controllerPin'), 'A0')

c.toYaml("library/SegDistanceSensor.yaml")