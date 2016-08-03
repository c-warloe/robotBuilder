from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini
from svggen.utils.dimensions import tgy1370a


def test_make_arm(display=False):
    f = getComponent("Arm")

    f.setParameter("servo", tgy1370a)
    f.setParameter('controller', ArduinoProMini())

    f.makeOutput("output/arm", display=display, tree=True)

if __name__ == '__main__':
    test_make_arm(display=True)
