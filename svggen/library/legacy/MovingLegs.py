from svggen.api.component import Component
from svggen.utils import tabs
from svggen.utils.dimensions import tgy1370a
from svggen.library.Arduino import ArduinoProMini

class MovingLegs(Component):
  _test_params = {
    'controller' : ArduinoProMini(),
    "servo" : tgy1370a,
    "height" : 30,
    "length" : 48,
    "flip" : True,
    "leg.beamwidth" : 10,
    "depth" : tgy1370a.getParameter('motorwidth'),
    "width" : tgy1370a.getParameter('motorheight'),
    "controllerPin" : 8,
    "label" : "Moving Leg",
  }

  def __init__(self):
    # XXX Check for yaml definition by default?
    Component.__init__(self, "MovingLegs.yaml")

  def assemble(self):
    ### XXX hack to get 3 faces along an edge
    graph = self.composables["graph"]

    tabWidth = self.getParameter("servo").getParameter("motorheight")
    tabWidth = 10
    tab = tabs.BeamTabs(self.getParameter("length"), tabWidth, noflap=True)

    graph.attachFace(self.getInterfaces("servo", "tabedge").getEdges()[0],
                     tab, "tabedge", prefix="movingLegBeam", angle=90)
    tabs.BeamSlotDecoration(graph.getFace("servo.mount.beam.r0"),
                            "move.topsplit.e0", tabWidth, noflap=True)

    tab = tabs.BeamTabs(self.getParameter("length"), tabWidth, noflap=True)
    graph.attachFace(self.getInterfaces("move", "botedge").getEdges()[0],
                     tab, "tabedge", prefix="movingLegFlexure", angle=0)
    tabs.BeamSlotDecoration(graph.getFace("servo.mount.beam.r2"),
                            "servo.mount.beam.r3.e3", tabWidth, noflap=True)

if __name__ == "__main__":
  f = MovingLegs()
  f._make_test()
