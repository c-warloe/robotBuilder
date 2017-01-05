from MechanicalComponent import MechanicalComponent
from sets import Set
from svggen.api.composables.GraphComposable import Graph
from svggen.api.ports.EdgePort import EdgePort

import svggen.utils.mymath as math


class FoldedComponent(MechanicalComponent):
  def __init__(self, yamlFile=None, *args, **kwargs):
    self.GRAPH = 'graph'
    self.drawing = None
    MechanicalComponent.__init__(self, yamlFile, **kwargs)

  def addFoldedSubcomponent(self, name, obj, **kwargs):
    '''
    :param name: unique identifier to refer to this component by
    :type  name: str or unicode
    :param obj: code name of the subcomponent
                should be python file/class or yaml name
    :type  obj: str or unicode
    '''
    # XXX will silently fail if subcomponent name is already taken?
    sc = {"class": obj, "parameters": {}, "constants": kwargs, "baseclass": "FoldedComponent", "component": None}
    self.subcomponents.setdefault(name, sc)
    self.resolveSubcomponent(name)

  def define(self, origin=False, euler=None, quat=False, **kwargs):
    MechanicalComponent.define(self, origin, euler, quat, **kwargs)
    g = Graph(transform = self.transform3D,component=self)
    self.composables[self.GRAPH] = g

    self.place = self.getGraph().place
    self.mergeEdge = self.getGraph().mergeEdge
    self.addTab = self.getGraph().addTab
    self.getEdge = self.getGraph().getEdge
    self.attachFace = self.getGraph().attachFace
    self.addFace = self.getGraph().addFace

  '''
  def attachFace(self, fromEdge, newFace, newEdge, **kwargs):
    self.getGraph().attachFace(fromEdge, newFace, newEdge, **kwargs)
    port = FacePort(self, newFace)
    self.addInterface(newFace.name, port)
    
  def addFace(self, face, **kwargs):
    self.getGraph().addFace(face, **kwargs)
    port = FacePort(self, face)
    self.addInterface(face.name, port)
  '''

  def fixEdgeInterface(self, name, interface, val):
    ep = self.getInterfaces(name, interface)
    if isinstance(ep, EdgePort):
      self.fixVariable(self.getVariableSub(ep.getParameter("length")).name, val)


  def getGraph(self):
    return self.composables[self.GRAPH]

  def solve(self):
    # first create equivalence classes
    equivClasses = []
    classesMap = {}
    classnum = 0
    for i in range(len(self.semanticConstraints)):
      constraint = self.semanticConstraints[i]
      if not isinstance(constraint.lhs, math.Symbol) or not isinstance(constraint.rhs, math.Symbol):
        raise Exception("Constraints are not simple parameters.")
      lhsSub = self.getVariableSub(constraint.lhs)
      rhsSub = self.getVariableSub(constraint.rhs)
      if lhsSub in classesMap and rhsSub not in classesMap:
        equivClasses[classesMap[lhsSub]].add(rhsSub)
        classesMap[rhsSub] = classesMap[lhsSub]
      elif lhsSub not in classesMap and rhsSub in classesMap:
        equivClasses[classesMap[rhsSub]].add(lhsSub)
        classesMap[lhsSub] = classesMap[rhsSub]
      elif lhsSub not in classesMap and rhsSub not in classesMap:
        equivClasses.append(Set([lhsSub, rhsSub]))
        classesMap[lhsSub] = classesMap[rhsSub] = classnum
        classnum += 1
      else:
        equivClasses[classesMap[lhsSub]].update(equivClasses[classesMap[rhsSub]])
        equivClasses[classesMap[rhsSub]] = equivClasses[classesMap[lhsSub]]

    # set values of all variables in a single equivalence class to the default
    # of one of them
    for eClass in equivClasses:
      fixed = next(iter(eClass))
      for var in eClass:
        if var.fixed():
          if fixed.fixed() and fixed.getValue() != var.getValue():
            raise Exception("Multiple variables are fixed with different values in the same equivalence class.")
          else:
            fixed = var
      for var in eClass:
        self.setVariableSolved(var.name, fixed.getValue())
        #print "SOLVE: " + var.name + ": " + str(var.getValue())

#      if(constraint.lhs.solved()):
#        self.setVariableSolved(self.getVariableSub(constraint.rhs).name,
#                              self.getVariableSub(constraint.lhs).getValue())
#      else:
#        self.setVariableSolved(self.getVariableSub(constraint.lhs).name,
#                               self.getVariableSub(constraint.rhs).getValue())
#    pass
