from svggen.library.ServoMount import ServoMount

def test_make(display=False):
    component = ServoMount()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

