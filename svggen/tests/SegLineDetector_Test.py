from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini
from svggen.utils.dimensions import tgy1370a, fs90r


def test_make_seg_lineDetector(display=False):
    f = getComponent("SegLineDetector", length=49, height=28)

    f.setParameter("driveservo", fs90r)
    f.setParameter("tailservo", tgy1370a)
    f.setParameter('controller', ArduinoProMini())

    f.makeOutput("output/SegLineDetector", tree=True, display=display)


if __name__ == '__main__':
    test_make_seg_lineDetector(display=True)

