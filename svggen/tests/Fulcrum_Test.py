from svggen.library import getComponent

def test_make(display=False):
    component = getComponent("Fulcrum")
    component._test_params = {
      'thickness': 10,
      'stemwidth': 50,
      'crosswidth': 30,
      'leftlength': 50,
      'rightlength': 100,
    }
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

