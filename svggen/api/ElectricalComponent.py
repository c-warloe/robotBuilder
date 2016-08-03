__author__ = 'Joseph'

from svggen.api.component import Component
from svggen.api.composables.ElectricalComposable import ElectricalComposable

class ElectricalComponent(Component):
  def define(self):
    self.addParameter('controller')

  def addInterface(self, name, val):
    self.addParameter(name + '.controllerPin')
    Component.addInterface(self, name, val)

  def assemble(self):
    electrical = ElectricalComposable()
    self.composables['electrical'] = electrical

  def setControllerPins(self):
    # Assign port parameters to our known parameters
    # TODO be able to constrain interface parameters to component parameters?
    for (name, val) in self.interfaces.iteritems():
      try:
        if isinstance(val, dict):
          self.getInterfaces(val['subcomponent'], val['interface']).setParameter('controllerPin', self.getParameter(name + '.controllerPin'))
        else:
          val.setParameter('controllerPin', self.getParameter(name + '.controllerPin'))
      except KeyError:
        pass

