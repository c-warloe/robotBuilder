from svggen.library import getComponent


def test_make_finger(display=False):

    f = getComponent("Finger")
    f.composables['graph'].place()
    '''
    f.setParameter("beamwidth",8)
    f.setParameter("length",100)
    f.setParameter("ratio",2)

    f.makeOutput("output/finger", display=display)
    '''

if __name__ == '__main__':
    test_make_finger(display=True)

