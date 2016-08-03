from svggen.library.FourBarLegs import FourBarLegs

def test_make(display=False):
    component = FourBarLegs()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

