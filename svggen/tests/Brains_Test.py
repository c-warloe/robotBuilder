from svggen.library.Brains import Brains

def test_make(display=False):
    component = Brains()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

