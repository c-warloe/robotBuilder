from svggen.api.component import Component
from svggen.api.ports.EdgePort import EdgePort
from svggen.utils.dimensions import tgy1370a
from svggen.utils.utils import decorateGraph


class ServoMount(Component):

  _test_params = {
    'servo': tgy1370a,
    'flip': True,
  }

  def define(self):
    self.addSubcomponent("beam", "RectBeam")
    self.addSubcomponent("hole", "Cutout")

    self.addParameter("length")
    self.addParameter("servo")
    self.addParameter("flip", False)
    self.addParameter("depth")
    self.addParameter("width")
    self.addParameter("phase", 0)
    self.addParameter("center", True)
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

    self.addConstraint(("hole", "dx"), "servo", 'x.getParameter("motorwidth") * 0.99')
    self.addConstraint(("hole", "dy"), "servo", 'x.getParameter("motorlength")')

    self.inheritAllInterfaces("beam", prefix=None)

  def modifyParameters(self):
    try:
      self.getParameter("width")
    except KeyError:
      self.setParameter("width", self.getParameter("servo").getParameter("motorheight"))

    try:
      self.getParameter("depth")
    except KeyError:
      self.setParameter("depth", self.getParameter("servo").getParameter("motorwidth"))

    try:
      self.getParameter("length")
    except KeyError:
      self.setParameter("length", self.getParameter("servo").getParameter("motorlength")
                                  + self.getParameter("servo").getParameter("shoulderlength") * 2)

  def assemble(self):
    # XXX TODO: Make sure servo can fit
    l = self.getParameter("length")
    p = self.getParameter("phase")

    ml = self.getParameter("servo").getParameter("motorlength")
    sl = self.getParameter("servo").getParameter("shoulderlength")
    ho = self.getParameter("servo").getParameter("hornoffset")

    dy = l/2. - ml/2. - sl
    if self.getParameter("center"):
      dy = min(dy, ml/2. - ho)
    if self.getParameter("flip"):
      dy = -dy

    decorateGraph(self, "beam.r%d" % ((3-p)%4), "hole", offset=(0, dy), mode="hole")

if __name__ == "__main__":
  f = ServoMount()
  f._make_test()

