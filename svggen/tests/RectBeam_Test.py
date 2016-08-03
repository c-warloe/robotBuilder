from svggen.library.RectBeam import RectBeam

def test_make(display=False):
    component = RectBeam()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

