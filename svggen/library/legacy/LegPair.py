from svggen.api.component import Component
from svggen.utils.dimensions import tgy1370a
from svggen.library.Arduino import ArduinoProMini

class LegPair(Component):

  _test_params = {
    'servo': tgy1370a,
    'height': 30,
    'length': 48,
    'width': 28+19,
    'leg.beamwidth': 10,
    'controller': ArduinoProMini(),
    'controllerPin': 9,
    'label': 'Leg Pair test'
  }

  def __init__(self):
    # XXX Check for yaml definition by default?
    Component.__init__(self, "LegPair.yaml")

  def assemble(self):
    ### Assemble the object
    self.getComponent("fixed").composables["graph"].invertEdges()

    self.attach(("move", "botedge3"),
                ("fixed", "topedge1"), {"angle":90})

if __name__ == "__main__":
  f = LegPair()
  f._make_test()

