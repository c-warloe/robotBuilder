from svggen.api.component import Component
from svggen.api.ports.EdgePort import EdgePort
from svggen.utils import tabs
from svggen.utils.dimensions import tgy1370a
from svggen.library.Arduino import ArduinoProMini

class TwoMovingLegs(Component):
  _test_params = {
    "servo" : tgy1370a,
    "height" : 20,
    "length" : 55,
    "leg.beamwidth" : 5,
    "depth" : tgy1370a.getParameter('motorwidth'),
    "width" : tgy1370a.getParameter('motorheight') + 5,
  }

  def __init__(self):
    # XXX Check for yaml definition by default?
    Component.__init__(self, "TwoMovingLegs.yaml")
    self.addInterface("slotedge", EdgePort(self, None))

  def assemble(self):
    ### XXX hack to get 3 faces along an edge
    graph = self.composables["graph"]

    tabWidth = self.getParameter("width")
    tab = tabs.BeamTabs(self.getParameter("length"), tabWidth, frac=0.25)

    graph.attachFace(self.getInterfaces("servo", "tabedge").getEdges()[0],
                     tab, "tabedge", prefix="movingLegBeam", angle=90)
    tabs.BeamSlotDecoration(graph.getFace("servo.beam.r0"),
                            "move1.topsplit.e0", tabWidth, frac=0.25)

    tab = tabs.BeamSlots(self.getParameter("length"), tabWidth, frac=0.25)
    graph.attachFace(self.getInterfaces("move2", "topedge").getEdges()[0],
                     tab, "oppedge", prefix="movingLegFlexure", angle=0)

    tabs.BeamSlotDecoration(graph.getFace("servo.beam.r2"),
                            "servo.beam.r3.e3", tabWidth, frac=0.25)
    tabs.BeamTabDecoration(graph.getFace("panel.r"),
                            "panel.e2", tabWidth, frac=0.25)

    self.setInterface("slotedge", EdgePort(self, "movingLegFlexure.slotedge"))

if __name__ == "__main__":
  f = TwoMovingLegs()
  f._make_test()
