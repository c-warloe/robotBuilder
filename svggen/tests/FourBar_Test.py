from svggen.library.FourBar import FourBar

def test_make(display=False):
    component = FourBar()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

