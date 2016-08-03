from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini
from svggen.utils.dimensions import tgy1370a

def test_make_ant(display=False):
  f = getComponent("SmallAnt", length=55, height=30, depth=7)

  f.setParameter("servo", tgy1370a)
  f.setParameter('microcontroller', ArduinoProMini())

  f.setParameter("leg.beamwidth", 5)

  f.makeOutput("output/ant", display=display, tree=False)


if __name__ == '__main__':
    test_make_ant(display=True)

