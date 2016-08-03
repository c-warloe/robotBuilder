from svggen.api.component import Component
from svggen.library.Arduino import ArduinoProMini
from svggen.utils.utils import decorateGraph


class Brains(Component):

  _test_params = {
    'length': 139,
    'brain': ArduinoProMini(),
  }

  def define(self):
    self.addSubcomponent("beam", "RectBeam")
    self.addSubcomponent("slotsplit", "SplitEdge")
    self.addSubcomponent("tabsplit", "SplitEdge")
    self.addSubcomponent("progcover", "Rectangle")
    self.addSubcomponent("restcover", "Rectangle")
    self.addSubcomponent("header", "Header")

    self.addParameter("brain")
    self.addParameter("length")
    self.addParameter("width", 0)
    self.addParameter("depth", 0)

    ### Set specific relationships between parameters
    def getBrainParameter(p):
      return "brain", "x.getDimension('%s')" % p

    self.addConstraint(("beam", "width"), ("brain", "width"), "max(x[1], x[0].getDimension('width'))")
    self.addConstraint(("beam", "depth"), ("brain", "depth"), "max(x[1], x[0].getDimension('height'))")
    self.addConstraint(("beam", "length"), "length")
    self.addConstConstraint(("beam", "faces"), range(1,4))

    # XXX: doesn't check to see whether minimum length is satisfied
    proglength = 6
    maxbt = 10

    self.addConstraint(("tabsplit", "botlength"), "length", "(x,)")
    self.addConstraint(("tabsplit", "toplength"), ("brain", "length"),
                                 "(\
                                   %d, \
                                   x[0].getDimension('length') - %d,\
                                   min(x[1] - x[0].getDimension('length'), %d),\
                                   max(x[1] - x[0].getDimension('length') - %d, 0),\
                                  )" % (proglength, proglength, maxbt, maxbt))

    self.addConstraint(("slotsplit", "toplength"), "length", "(x,)")
    self.addConstraint(("slotsplit", "botlength"), ("brain", "length"),
                                 "(\
                                   %d, \
                                   x[0].getDimension('length') - %d,\
                                   min(x[1] - x[0].getDimension('length'), %d),\
                                   max(x[1] - x[0].getDimension('length') - %d, 0),\
                                  )" % (proglength, proglength, maxbt, maxbt))

    self.addConstraint(("progcover", "w"), *getBrainParameter("width"))
    self.addConstraint(("progcover", "l"), "brain", "x.getDimension('length') - %d" % proglength)

    self.addConstraint(("restcover", "w"), *getBrainParameter("width"))
    self.addConstraint(("restcover", "l"), ("brain", "length"),
                                           "max(x[1] - x[0].getDimension('length') - %d, 0)" % maxbt)

    self.addConstraint(("header", "nrows"), *getBrainParameter("nrows"))
    self.addConstraint(("header", "ncols"), *getBrainParameter("ncols"))
    self.addConstraint(("header", "rowsep"), *getBrainParameter("rowsep"))
    self.addConstraint(("header", "colsep"), *getBrainParameter("colsep"))

    '''
    if length < brainlength:
      raise ValueError("Brain module too short")
    '''

    self.addConnection(("beam", "tabedge"),
                       ("tabsplit", "botedge0"),
                       angle=0)

    self.addConnection(("beam", "slotedge"),
                       ("slotsplit", "topedge0"),
                       angle=0)

    self.addConnection(("tabsplit", "topedge1"),
                       ("progcover", "t"),
                       angle=90)
    self.addConnection(("tabsplit", "topedge3"),
                       ("restcover", "t"),
                       angle=90)

    self.addConnection(("slotsplit", "botedge1"),
                       ("progcover", "b"),
                       angle=90, tabWidth=10)
    self.addConnection(("slotsplit", "botedge3"),
                       ("restcover", "b"),
                       angle=90, tabWidth=10)

    self.inheritAllInterfaces("beam", prefix=None)
    # XXX: can't have multiple interfaces referring to the same port
    # XXX: Causes double prefixing when iterating over ports
    '''
    self.inheritInterface("topright", ("beam", "topedge0"))
    self.inheritInterface("topleft", ("beam", "topedge2"))
    self.inheritInterface("botright", ("beam", "botedge0"))
    self.inheritInterface("botleft", ("beam", "botedge2"))
    '''

  def assemble(self):
    ### Assemble the object
    l = self.getParameter("length") - self.getParameter("brain").getDimension("length")

    decorateGraph(self, "beam.r2", "header", mode="hole", offset=(0, -l/2.))

if __name__ == "__main__":
  f = Brains()
  f.toYaml("output/brains.yaml")
  f._make_test()

