from svggen.library.Beam import Beam

def test_make(display=False):
    component = Beam()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

