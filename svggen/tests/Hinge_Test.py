from svggen.api.component import Component

def test_make(display=False):
    h = Component("Hinge.yaml")

    h.setParameter("perimeter", 400)
    h.setParameter("tetherwidth", 10)
    h.setParameter("tetheroffset", 20)
    h.setParameter("top", -.25)
    h.setParameter("bot", .25)
    h.setParameter("angle", 45)

    h.makeOutput("output/hinge", display=display)


if __name__ == '__main__':
    test_make(display=True)

