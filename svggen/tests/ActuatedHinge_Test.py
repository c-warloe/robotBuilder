from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini
from svggen.utils.dimensions import tgy1370a, proMini


def test_make_actuated_hinge(display=False):
    f = getComponent("ActuatedHinge")

    f.setParameter("servo", tgy1370a)
    f.setParameter("length", 90)
    f.setParameter("width", 14)
    f.setParameter("depth", 9)

    f.setParameter('controller', ArduinoProMini())

    f.makeOutput("output/actuatedHinge", display=display)


if __name__ == '__main__':
    test_make_actuated_hinge(display=True)

