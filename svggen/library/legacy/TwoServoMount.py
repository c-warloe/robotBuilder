from svggen.api.component import Component
from svggen.api.ports.EdgePort import EdgePort
from svggen.utils.utils import decorateGraph
from svggen.utils.dimensions import tgy1370a

class TwoServoMount(Component):

  _test_params = {
    'servo': tgy1370a,
    'length': 70,
  }

  def define(self):
    self.addSubcomponent("beam", "RectBeam")
    self.addSubcomponent("hole1", "Cutout")
    self.addSubcomponent("hole2", "Cutout")

    self.addParameter("length")
    self.addParameter("servo")
    self.addParameter("depth")
    self.addParameter("width")
    self.addParameter("phase", 0)
    self.addParameter("faces", None)

    ### Set specific relationships between parameters
    # self.addConstraint(("beam", "width"), "servo", 'x.getParameter("motorheight")')
    # self.addConstraint(("beam", "depth"), "servo", 'x.getParameter("motorwidth")')
    self.addConstraint(("beam", "length"), "length")
    self.addConstraint(("beam", "width"), "width")
    self.addConstraint(("beam", "depth"), "depth")
    self.addConstraint(("beam", "phase"), "phase")
    self.addConstraint(("beam", "faces"), "faces")
    self.addConstConstraint(("beam", "noflap"), True)

    self.addConstraint(("hole1", "dx"), "servo", 'x.getParameter("motorwidth") * 0.99')
    self.addConstraint(("hole1", "dy"), "servo", 'x.getParameter("motorlength")')
    self.addConstraint(("hole2", "dx"), "servo", 'x.getParameter("motorwidth") * 0.99')
    self.addConstraint(("hole2", "dy"), "servo", 'x.getParameter("motorlength")')

    self.inheritAllInterfaces("beam", prefix=None)

  def modifyParameters(self):
    try:
      self.getParameter("width")
    except KeyError:
      # XXX hack : 1 mm extra for overlapping shoulders
      self.setParameter("width", self.getParameter("servo").getParameter("motorheight") + 1)

    try:
      self.getParameter("depth")
    except KeyError:
      self.setParameter("depth", self.getParameter("servo").getParameter("motorwidth"))

    try:
      self.getParameter("length")
    except KeyError:
      self.setParameter("length", self.getParameter("servo").getParameter("motorlength") * 2
                        + self.getParameter("servo").getParameter("shoulderlength") * 2)

  def assemble(self):
    # XXX TODO: Make sure servo can fit
    l = self.getParameter("length")
    p = self.getParameter("phase")

    ml = self.getParameter("servo").getParameter("motorlength")
    sl = self.getParameter("servo").getParameter("shoulderlength")
    ho = self.getParameter("servo").getParameter("hornoffset")

    dy = l/2. - ml/2. - sl

    decorateGraph(self, "beam.r%d" % ((3-p)%4), "hole1", offset=(0, dy), mode="hole")
    decorateGraph(self, "beam.r%d" % ((1-p)%4), "hole2", offset=(0, dy), mode="hole")


if __name__ == "__main__":
  f = TwoServoMount()
  f._make_test()

