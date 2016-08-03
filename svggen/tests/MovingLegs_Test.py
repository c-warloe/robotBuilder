from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini
from svggen.utils.dimensions import tgy1370a


def test_make(display=False):
    f = getComponent("MovingLegs")
    f.setParameter("servo", tgy1370a)
    f.setParameter("height", 25)
    f.setParameter("length", 40)
    f.setParameter("depth", tgy1370a.getParameter("motorwidth"))
    f.setParameter("width", tgy1370a.getParameter("motorheight"))

    f.setParameter('controller', ArduinoProMini())
    f.setParameter('label', "test")

    f.makeOutput("output/movinglegs", display=display)

if __name__ == '__main__':
    test_make(display=True)

