from svggen.library.Tetrahedron import Tetrahedron

def test_make(display=False):
    component = Tetrahedron()
    component._make_test(display=display)


if __name__ == '__main__':
    test_make(display=True)

