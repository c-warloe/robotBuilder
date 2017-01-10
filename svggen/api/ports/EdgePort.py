from Port import Port
from svggen.utils.utils import prefix as prefixString
from svggen.utils.mymath import cos, deg2rad, Eq

class EdgePort(Port):
  def __init__(self, parent, edgeName):

    graph = parent.getGraph()
    self.edge = graph.getEdge(edgeName)
    #self.placed = False
    params = {}
    try:
      params = {'length': self.edge.length}
      # params = {'pts3D': edge.pts3D}
      #for i in range(2):
        #for j, x in enumerate(["x", "y", "z"]):
          #params["pt%d%s" % (i, x)] = self.edge.pts3D[i][j]
    except AttributeError:
      raise AttributeError("Unplaced edge: " + edgeName)

    Port.__init__(self, parent, params)
    self.edgeName = edgeName

  def getEdges(self):
    return [self.edgeName]

  def getPts(self):
    return self.edge.pts3D

  def prefix(self, prefix=""):
    #if self.placed:
    #  return
    self.edgeName = prefixString(prefix, self.edgeName)
    #self.placed = True

  def toString(self):
    return str(self.getEdges())

  def update(self):
    try:
      self.parameters['length'] = self.edge.length
    except AttributeError:
      raise AttributeError("Unplaced edge: " + self.edge.name)

  def constrain(self, parent, toPort, **kwargs):
    """
    Return a set of semantic constraints to be satisfied when connecting to toPort object
    By default, constrain same-named parameters to be equal

    Override this method for better matching
    :returns: list of semantic constraints 
    :rtype: list
    """

    # Can't use default constrain function because pt1 connects to pt2 and vice versa
    constraints = []
    try:
      if(self.getParameter("length") != toPort.getParameter("length")):
        constraints.append((Eq(self.getParameter("length"), toPort.getParameter("length"))))
#      for i in range(2):
 #       for x in ["x", "y", "z"]:
 #         constraints.append(Eq(self.getParameter("pt%d%s" % (i, x)), toPort.getParameter("pt%d%s" % (1-i, x))))
    except AttributeError:
      raise AttributeError("Missing edge coordinates attaching EdgePorts")

    #try:
    #  angle = kwargs["angle"]
    #  if len(self.edge.faces) > 1:
    #    print "Too many faces on", self.edgeName, "-- using the first"
    #  if len(toPort.edge.faces) > 1:
    #    print "Too many faces on", toPort.edgeName, "-- using the first"
    #  myNormal = self.edge.faces.keys()[0].get3DNormal()
    #  toNormal = toPort.edge.faces.keys()[0].get3DNormal()
      #constraints.append(Eq(myNormal.dot(toNormal), cos(deg2rad(angle))))

    except KeyError:
      # no angle given
      pass

    return constraints
