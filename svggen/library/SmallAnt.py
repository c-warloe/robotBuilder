from svggen.api.component import Component
from svggen.utils import tabs
from svggen.utils.utils import decorateGraph


class SmallAnt(Component):
  def __init__(self):
    # XXX Check for yaml definition by default?
    Component.__init__(self, "SmallAnt.yaml")

  def assemble(self):
    decorateGraph(self, "brain.r2", "header", rotate=False, mode="hole")

    graph = self.composables["graph"]
    tabWidth = self.getComponent("brain").getParameter("width")

    tabs.BeamSlotDecoration(graph.getFace("brain.r0"),
                            "brain.r0.e3", tabWidth, frac=0.25)
