from svggen.api.CodeComponent import CodeComponent
from svggen.api.ports.DataInputPort import DataInputPort
from svggen.api.ports.DataOutputPort import DataOutputPort


class DataFunction(CodeComponent):
  def define(self):
    CodeComponent.define(self)
    self.addParameter('function', '')

    # TODO allow specifying number of inputs and outputs
    self.addInterface('input', DataInputPort(parent=self, name='input'))
    self.addInterface('output', DataOutputPort(parent=self, name='output'))

  def assemble(self):
    CodeComponent.assemble(self)
    #print 'see parameters ', self.parameters
    #print 'see connections ', self.connections

    self.setInterface('input', DataInputPort(parent=self, name='input'))
    self.setInterface('output', DataOutputPort(parent=self, name='output'))

    function = self.getParameter('function')
    function = 'input' if (function is None or len(function) == 0) else function
    self.setParameter('function', function)

    self.addCodeFile('code/data_function.cpp')
