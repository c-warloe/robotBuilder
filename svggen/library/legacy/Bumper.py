from svggen.api.component import Component
from svggen.utils import tabs


class Bumper(Component):
  def define(self):
    self.addSubcomponent("beam", "RectBeam", faces=range(4))
    self.addSubcomponent("tail", "Rectangle")

    self.inheritAllInterfaces("beam", prefix=None)

    self.addConnection(("beam", "slotedge"),
                       ("tail", "t"),
                       angle=0)

    self.inheritInterface("tail", ("tail", "b"))

  '''
  def assemble(self):
    ### XXX hack to get 3 faces along an edge
    graph = self.composables["graph"]

    tabWidth = self.getParameter("width")
    tab = tabs.BeamTabs(self.getParameter("length"), tabWidth)

    graph.attachFace(self.getInterfaces("beam", "tabedge").getEdges()[0],
                     tab, "tabedge", prefix="beamtab", angle=90)
    tabs.BeamSlotDecoration(graph.getFace("beam.r0"),
                                "tail.e2", tabWidth)
  '''


if __name__ == "__main__":
  f = Bumper()
  print f.getInterface("tail").getPts()
