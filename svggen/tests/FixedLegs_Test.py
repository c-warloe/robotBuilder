from svggen.library import getComponent
from svggen.utils.tabs import *
import svggen.utils.mymath as math


def test_make_fixed_legs(display=False):
    '''
    def tabFace(length):
      f = Rectangle("tab", length, 10)
      f.renameEdges(edgeNames = ("tabedge", "e1", "slotedge", "e3"))
      return f

    d, h, l, bw = 9, 50, 28+19, 10

    '''
    # Load new component object from yaml definition
    # f = Component("FixedLegs.yaml")
    f = getComponent("FixedLegs")
    f.setParameter("depth", 10)
    f.setParameter("height", 50)
    f.setParameter("length", 47)
    f.setParameter("legwidth", 8)

    print "~~~ Parameters:"
    for p, n in sorted(f.allParameters.iteritems(), key = lambda x: x[1]):
      print p, n
    print
    print "~~~ Equations:"
    for c in f.getRelations():
      print c
    print
    print math.solve(f.getRelations())
    '''
    print "~~~ Outputs:"
    with math.assuming(*f.getRelations()):
      print math.N(f.getInterface("foot1").getParameter("pt"))
      print math.N(f.getInterface("foot2").getParameter("pt"))
    print f.getInterface("foot1").getParameter("pt")[0]
    from svggen.utils.utils import schemeList
    print repr(schemeList(f.getInterface("foot1").getParameter("pt")[0].subs(f.getSubs())))

    print
    print
    for p in f.parameters:
      print p, f.getSolution(p)
    '''
      

    '''
    # Define free parameters
    f.setParameter("depth", d)
    f.setParameter("height", h)
    f.setParameter("length", l)
    f.setParameter("leg.beamwidth", bw)

    f.makeOutput("output/fixedlegs", tabFace = BeamTabs, slotDecoration=BeamSlotDecoration, display=display)
    '''


if __name__ == '__main__':
    test_make_fixed_legs(display=True)

