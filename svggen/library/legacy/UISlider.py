from svggen.api.UIComponent import UIComponent
from svggen.api.ports.DataOutputPort import DataOutputPort
from svggen.api.ports.DataInputPort import DataInputPort

class UISlider(UIComponent):
  def define(self):
    UIComponent.define(self)
    self.addParameter('max', 100)
    self.addParameter('min', 0)
    self.addParameter('default', 50)
    
    self.addInterface('curPosition', DataOutputPort(parent=self, name='curPosition'))
    self.addInterface('newPosition', DataInputPort(parent=self, name='newPosition'))

  def assemble(self):
    UIComponent.assemble(self)

    self.setInterface('curPosition', DataOutputPort(parent=self, name='curPosition'))
    self.setInterface('newPosition', DataInputPort(parent=self, name='newPosition'))

  def getOptionStr(self):
    try:
      max = int(self.getParameter('max'))
    except ValueError:
      max = 100
    try:
      min = int(self.getParameter('min'))
    except ValueError:
      min = 0
    try:
      default = int(self.getParameter('default'))
    except ValueError:
      default = (max+min)/2
    return str(min) + ',' + str(max) + ',' + str(default)
