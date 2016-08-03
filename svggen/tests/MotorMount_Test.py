from svggen.library.MotorMount import MotorMount

def test_make(display=False):
    component = MotorMount()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

