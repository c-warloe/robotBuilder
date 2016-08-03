from svggen.api.CodeComponent import CodeComponent

class UIComponent(CodeComponent):
  def define(self):
    CodeComponent.define(self)
    self.addParameter('protocol', 'bluetooth')
    self.addParameter('label', 'generic')

  def setInterface(self, n, v):
    try:
      v.setParameter('protocol', self.getParameter('protocol'))
    except KeyError:
      pass
    CodeComponent.setInterface(self, n, v)

  def assemble(self):
    CodeComponent.assemble(self)
    if self.getParameter('protocol') == 'bluetooth':
      self.addCodeFile('code/protocol_bluetooth.cpp')

  def getTypeName(self):
    typeName = str(self.__class__)
    return typeName[typeName.rfind('.')+1:typeName.rfind('\'')]

  def getOptionStr(self):
    return ''

  def getLabel(self):
    return self.getParameter('label')

if __name__ == '__main__':
  UIComponent()
