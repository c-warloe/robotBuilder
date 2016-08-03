from svggen.library.LegPair import LegPair

def test_make(display=False):
    component = LegPair()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

