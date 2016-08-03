from svggen.library.PointedLeg import PointedLeg

def test_make(display=False):
    component = PointedLeg()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

