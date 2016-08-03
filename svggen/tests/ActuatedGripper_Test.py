from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini
from svggen.utils.dimensions import tgy1370a, proMini


def test_make_actuated_gripper(display=False):
    f = getComponent("ActuatedGripper")
    f.setParameter("servo", tgy1370a)
    f.setParameter("fingerlength", 40)
    f.setParameter("fingerwidth", 5)
    f.setParameter("width", 14)
    f.setParameter("depth", 9)
    f.setParameter("length", 50)

    f.setParameter('controller', ArduinoProMini())

    f.makeOutput("output/actuatedGripper", display=display)


if __name__ == '__main__':
    test_make_actuated_gripper(display=True)

