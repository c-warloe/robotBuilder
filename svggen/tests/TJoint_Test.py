from svggen.library.TJoint import TJoint

def test_make(display=False):
    component = TJoint()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

