__author__ = 'Joseph'

from svggen.api.CodeComponent import CodeComponent

class Driver(CodeComponent):
  def define(self):
    CodeComponent.define(self)
    self.addParameter('drivenComponent')

  def assemble(self):
    CodeComponent.assemble(self)
