from svggen.utils.mymath import sqrt

from svggen.api.component import Component
from svggen.utils.utils import decorateGraph


class FourBarDoubleLeg(Component):
  _test_params = {
    "flexlengthx" : 20, 
    "flexwidth" : 5, 
    "depth" : 9, 
    "phase" : False, 
    "height" : 25, 
    "length" : 40, 
    "dl" : 10, 
    "leg.beamwidth" : 5, 
  }

  def define(self):
    self.addSubcomponent("fakelegmount", "Rectangle")
    self.addSubcomponent("fakeleg", "Rectangle")
    self.addSubcomponent("spacer", "Rectangle")

    self.addSubcomponent("linkage", "FourBar", inherit=("depth", "flexwidth", "flexlengthx"), prefix=None)
    self.addSubcomponent("leg", "PointedLeg", inherit=("phase",), prefix=None)
    self.addSubcomponent("hole1", "Cutout")
    self.addSubcomponent("hole2", "Cutout")

    self.addParameter("length")
    self.addParameter("height")
    self.addParameter("dl", 0)

    self.addParameter("leg.beamwidth", 7)

    ### Set specific relationships between parameters
    self.addConstraint(("leg", "length"), "height")
    self.addConstraint(("leg", "beamwidth"), "leg.beamwidth")
    self.addConstraint(("leg", "top"), "depth")

    self.addConstraint(("linkage", "flexlengthy"),
                       ("length", "leg.beamwidth", "dl"), " (x[0] - %f * x[1]) / 2. - x[2]" % sqrt(2))

    self.addConstConstraint(("hole1", "d"), 1.5)
    self.addConstConstraint(("hole2", "d"), 1.5)

    self.addConstraint(("fakelegmount", "l"), "depth")
    self.addConstraint(("fakelegmount", "w"), "leg.beamwidth", " %f * x" % sqrt(2))

    self.addConstraint(("spacer", "l"), "depth")
    self.addConstraint(("spacer", "w"),
                       ("leg.beamwidth", "dl"), "2 * x[1] - %f * x[0]" % sqrt(2))

    self.addConstraint(("fakeleg", "l"), "height")
    self.addConstraint(("fakeleg", "w"), "leg.beamwidth", " %f * x" % sqrt(2))

    self.addConnection(("linkage", "output"),
                       ("fakelegmount", "t"),
                       angle=0)
    '''
    self.addConnection(("fakelegmount", "l"),
                       ("fakeleg", "r"),
                       angle=0)
    '''
    self.addConnection(("fakelegmount", "b"),
                       ("spacer", "t"),
                       angle=0)
    self.addConnection(("spacer", "b"),
                       ("leg", "top"),
                       angle=0)
    # XXX not really, but it puts the extra slots in the right place
    self.addConnection(("fakeleg", "t"),
                       ("leg", "slots"),
                       angle=0, tabWidth=5)

    self.inheritInterface("topedge", ("linkage", "topedge"))
    self.inheritInterface("botedge", ("linkage", "botedge"))

  def assemble(self):
    ### Assemble the object
    decorateGraph(self, "fakelegmount.r", "hole1", mode="hole")
    decorateGraph(self, "leg.t0", "hole2", mode="hole")

    if self.getParameter("phase"):
      spacerEdge = "r"
      first = 1
    else:
      spacerEdge = "l"
      first = 2

    self.attach(("fakelegmount", spacerEdge),
                ("fakeleg", "r"), {"angle":0})

if __name__ == "__main__":
  f = FourBarDoubleLeg()
  f._make_test()
