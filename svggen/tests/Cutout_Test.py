from svggen.library.Cutout import Cutout

def test_make(display=False):
    component = Cutout()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

