from math import sqrt

from svggen.api.component import Component
from svggen.utils.utils import decorateGraph


class FourBarLegs(Component):

  _test_params = {
    'flexlengthx': 20,
    'flexwidth': 5,
    'depth': 9,
    'height': 25,
    'length': 40,
    'leg.beamwidth': 5,
  }

  def define(self):
    self.addSubcomponent("spacer1", "Rectangle")
    self.addSubcomponent("spacer2", "Rectangle")
    self.addSubcomponent("fakeleg", "Rectangle")

    self.addSubcomponent("linkage1", "FourBar")
    self.addSubcomponent("linkage2", "FourBar")
    self.addSubcomponent("leg", "PointedLeg")
    self.addSubcomponent("hole", "Cutout")
    self.addSubcomponent("topsplit", "SplitEdge")
    self.addSubcomponent("botsplit", "SplitEdge")

    self.addParameter("height")
    self.addParameter("length")
    self.addParameter("dl", 0)
    self.addParameter("depth")

    self.addParameter("flexlengthx")
    self.addParameter("flexwidth", 5)
    self.addParameter("leg.beamwidth", 7)

    ### Set specific relationships between parameters
    self.addConstraint(("leg", "length"), "height")
    self.addConstraint(("leg", "beamwidth"), "leg.beamwidth")

    self.addConstraint(("linkage1", "depth"), "depth")
    self.addConstraint(("linkage1", "flexwidth"), "flexwidth")
    self.addConstraint(("linkage1", "flexlengthx"), "flexlengthx")
    self.addConstraint(("linkage1", "flexlengthy"), 
        ("length", "leg.beamwidth", "dl"), " (x[0] - %f * x[1]) / 2. + x[2]" % sqrt(2))

    self.addConstraint(("linkage2", "depth"), "depth")
    self.addConstraint(("linkage2", "flexwidth"), "flexwidth")
    self.addConstraint(("linkage2", "flexlengthx"), "flexlengthx")
    self.addConstraint(("linkage2", "flexlengthy"), 
        ("length", "leg.beamwidth", "dl"), " (x[0] - %f * x[1]) / 2. - x[2]" % sqrt(2))

    self.addConstConstraint(("hole", "d"), 1.5)

    self.addConstraint(("spacer1", "l"), "depth")
    self.addConstraint(("spacer1", "w"), "leg.beamwidth", " %f * x" % sqrt(2))

    self.addConstraint(("spacer2", "l"), "depth")
    self.addConstraint(("spacer2", "w"), "leg.beamwidth", " %f * x" % sqrt(2))

    self.addConstraint(("fakeleg", "l"), "height")
    self.addConstraint(("fakeleg", "w"), "leg.beamwidth", " %f * x" % sqrt(2))

    self.addConstraint(("topsplit", "botlength"), ("flexwidth", "length"), " (x[1],)")
    self.addConstraint(("topsplit", "toplength"), ("flexwidth", "length"), " (x[0], x[1]-2*x[0], x[0])")

    self.addConstraint(("botsplit", "botlength"), ("flexwidth", "length"), " (x[1],)")
    self.addConstraint(("botsplit", "toplength"), ("flexwidth", "length"), " (x[0], x[1]-2*x[0], x[0])")

    self.addConnection(("topsplit", "topedge0"),
                       ("linkage1", "topedge"),
                       angle=0)
    self.addConnection(("topsplit", "topedge2"),
                       ("linkage2", "botedge"),
                       angle=0)

    self.addConnection(("linkage1", "botedge"),
                       ("botsplit", "topedge2"),
                       angle=0)
    self.addConnection(("linkage2", "topedge"),
                       ("botsplit", "topedge0"),
                       angle=0)

    self.addConnection(("linkage2", "output"),
                       ("spacer2", "b"),
                       angle=0)
    self.addConnection(("spacer2", "r"),
                       ("leg", "diag"),
                       angle=0)

    self.addConnection(("linkage1", "output"),
                       ("spacer1", "t"),
                       angle=0)
    self.addConnection(("spacer1", "r"),
                       ("fakeleg", "r"),
                       angle=0)
    self.addConnection(("fakeleg", "t"),
                       ("leg", "slots"),
                       angle=0, tabWidth=5)

    self.inheritInterface("topedge", ("topsplit", "botedge0"))
    self.inheritInterface("botedge", ("botsplit", "botedge0"))
    self.inheritInterface("topinneredge", ("topsplit", "topedge1"))
    self.inheritInterface("botinneredge", ("botsplit", "topedge1"))

  def assemble(self):
    ### Assemble the object
    decorateGraph(self, "spacer1.r", "hole", mode="hole")
    decorateGraph(self, "spacer2.r", "hole", mode="hole")

    '''
    self.addTabs((Tab(), "tab1", min(10, sqrt(2) * self.getParameter("leg.beamwidth"))), 
                 None,
                 ("fakeleg", "leg2", "t"),
                 (Flat(), Cut()))
    '''


if __name__ == "__main__":

  f = FourBarLegs()
  f._make_test()

