from svggen.api.component import Component
from svggen.utils import tabs
from svggen.utils.dimensions import tgy1370a
from svggen.library.Arduino import ArduinoProMini


class SegTail(Component):

  _test_params = {
    'servo': tgy1370a,
    'controller': ArduinoProMini(),
    'height': 50
  }

  def define(self):
    self.addSubcomponent("beam", "Servo", inherit=True, prefix=None)
    self.addSubcomponent("leftsplit", "SplitEdge")
    self.addSubcomponent("rightsplit", "SplitEdge")
    self.addSubcomponent("tail", "Rectangle")

    self.addParameter("edgelen")
    self.addParameter("height")

    ### Set specific relationships between parameters
    self.addConstConstraint(("beam", "phase"), 1)
    self.addConstConstraint(("beam", "faces"), range(4))

    self.addConstraint(("leftsplit", "toplength"), "width", "(x,)")
    self.addConstraint(("leftsplit", "botlength"), ("width", "edgelen"), "(x[1], x[0]-x[1])")
    self.addConstraint(("rightsplit", "toplength"), "width", "(x,)")
    self.addConstraint(("rightsplit", "botlength"), ("width", "edgelen"), "(x[0]-x[1], x[1])")
    self.addConstraint(("tail", "l"), "length")
    self.addConstraint(("tail", "w"), ("height", "width", "edgelen"), "x[0] - x[1] - x[2]/2.")

    self.inheritAllInterfaces("beam", prefix=None)

    self.addConnection(("beam", "topedge1"),
                       ("leftsplit", "topedge0"),
                       angle=0)
    self.addConnection(("beam", "botedge1"),
                       ("rightsplit", "topedge0"),
                       angle=0)
    self.addConnection(("beam", "tabedge"),
                       ("tail", "t"),
                       angle=0)

    self.inheritInterface("leftedge", ("leftsplit", "botedge0"))
    self.inheritInterface("rightedge", ("rightsplit", "botedge1"))

  def modifyParameters(self):
    try:
      self.getParameter("width")
    except KeyError:
      self.setParameter("width", self.getParameter("servo").getParameter("motorheight"))

    try:
      self.getParameter("length")
    except KeyError:
      self.setParameter("length", self.getParameter("servo").getParameter("motorlength")
                                  + self.getParameter("servo").getParameter("shoulderlength") * 2)

    try:
      self.getParameter("edgelen")
    except KeyError:
      self.setParameter("edgelen", self.getParameter("servo").getParameter("motorwidth"))

  def assemble(self):
    ### Assemble the object
    self.getComponent("beam").composables["graph"].invertEdges()

    ### XXX hack to get 3 faces along an edge
    graph = self.composables["graph"]

    tabWidth = 10
    tab = tabs.BeamTabs(self.getParameter("length"), tabWidth)

    graph.attachFace(self.getInterfaces("beam", "slotedge").getEdges()[0],
                     tab, "tabedge", prefix="beamtab", angle=-90)
    tabs.BeamSlotDecoration(graph.getFace("beam.mount.beam.r3"),
                            "tail.e2", tabWidth)


if __name__ == "__main__":
  f = SegTail()
  f._make_test()

