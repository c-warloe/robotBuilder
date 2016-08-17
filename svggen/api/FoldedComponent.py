from MechanicalComponent import MechanicalComponent
from svggen.api.composables.GraphComposable import Graph


class FoldedComponent(MechanicalComponent):
  def __init__(self, *args, **kwargs):
    self.GRAPH = 'graph'
    self.drawing = None
    MechanicalComponent.__init__(self, *args, **kwargs)

  def define(self, origin=True, euler=None, quat=True, **kwargs):
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

  def getGraph(self):
    return self.composables[self.GRAPH]

