from svggen.api.component import Component

class DataComponent(Component):
  def define(self):
    pass

  def addInterface(self, name, val):
    self.addParameter(name + '.autoPoll')
    Component.addInterface(self, name, val)

  def assemble(self):
    pass

  def setAutoPolls(self):
    # Assign port parameters to our known parameters
    # TODO be able to constrain interface parameters to component parameters?
    for (name, val) in self.interfaces.iteritems():
      try:
        if isinstance(val, dict):
          self.getInterfaces(val['subcomponent'], val['interface']).setParameter('autoPoll', self.getParameter(name + '.autoPoll'))
        else:
          val.setParameter('autoPoll', self.getParameter(name + '.autoPoll'))
      except KeyError:
        pass


