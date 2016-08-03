from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini
from svggen.utils.dimensions import tgy1370a


def test_make_ant(display=False):
    f = getComponent("Ant", length=48, height=25)

    f.setParameter("servo", tgy1370a)
    f.setParameter('controller', ArduinoProMini())

    f.setParameter("leg.beamwidth", 7)

    f.makeOutput("output/ant", tree=True, display=display)


if __name__ == '__main__':
    test_make_ant(display=True)

