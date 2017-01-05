from svggen.api.UIComponent import UIComponent
from svggen.api.ports.DataOutputPort import DataOutputPort
from svggen.api.ports.DataInputPort import DataInputPort

class UIToggle(UIComponent):
  def define(self):
    UIComponent.define(self)
    self.addParameter('default', False)

    self.addInterface('curState', DataOutputPort(parent=self, name='curState'))
    self.addInterface('newState', DataInputPort(parent=self, name='newState'))

  def assemble(self):
    UIComponent.assemble(self)
    self.setAutoPolls()

  def getOptionStr(self):
    try:
      default = bool(self.getParameter('default'))
    except:
      default = False
    return str(int(default))
