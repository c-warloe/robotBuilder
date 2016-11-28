from HyperEdge import *
from svggen.utils.transforms import *
from svggen.utils.utils import prefix as prefixString
import svggen.utils.mymath as np
import svggen.api.composables.graph.DrawingEdge as DE
import sympy


class Face(object):
  allNames = []

  def __init__(self, name, pts, lens, edgeNames=True, edgeAngles=None, edgeFlips=None, allEdges=None, decorations=None, recenter=False):
    if name:
      self.name = name
    else:
      self.name = "" # "face%03d" % len(Face.allNames)
    Face.allNames.append(self.name)
    self.lens = lens
    self.recenter(list(pts), recenter=recenter)

    self.edges = [None] * len(pts)
    if edgeNames is True:
      edgeNames = ["e%d" % i for i in range(len(pts))]
    self.renameEdges(edgeNames, edgeAngles, edgeFlips, allEdges)

    if decorations:
      self.decorations = decorations
    else:
      self.decorations = []

    self.transform2D = None
    self.transform3D = None


  def recenter(self, pts, recenter=False):
    self.pts2d = [(p[0], p[1]) for p in pts]

    # Put centroid of polygon at origin
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]

    a, cx, cy = 0, 0, 0
    for i in range(len(pts)):
      a += (xs[i] * ys[i+1] - xs[i+1] * ys[i]) / 2
      cx += (xs[i] + xs[i+1]) * (xs[i] * ys[i+1] - xs[i+1] * ys[i]) / 6
      cy += (ys[i] + ys[i+1]) * (xs[i] * ys[i+1] - xs[i+1] * ys[i]) / 6

    self.area = a
    # XXX Hack -- what should we do if the area is 0?
    if a == 0:
      self.pts2d = [(p[0], p[1]) for p in pts]
      self.com2d = (0, 0)
    else: 
      if recenter:
        self.pts2d = [(p[0] - cx/a, p[1] - cy/a) for p in pts]
        self.com2d = (0, 0)
      else:
        self.pts2d = [(p[0], p[1]) for p in pts]
        self.com2d = (cx/a, cy/a)

    self.pts4d = np.transpose(np.array([list(x) + [0,1] for x in self.pts2d]))
    self.com4d = np.array(list(self.com2d) + [0,1])

  def rename(self, name):
    self.name = name

  def prefix(self, prefix):
    self.name = prefixString(prefix, self.name)
    self.prefixEdges(prefix)

  def prefixEdges(self, prefix):
    for e in self.edges:
      e.rename(prefixString(prefix, e.name))

  def renameEdges(self, edgeNames=None, edgeAngles=None, edgeFlips=None, allEdges=None):
    if edgeNames:
      if edgeAngles is None:
        edgeAngles = [0] * len(edgeNames)
      if edgeFlips is None:
        edgeFlips = [False] * len(edgeNames)
      for (index, name) in enumerate(edgeNames):
        self.setEdge(index, name, edgeAngles[index], edgeFlips[index], allEdges)
    return self

  def setEdge(self, index, name=None, angle=None, flip=False, allEdges=None):
    if name is None:
      return self
    try:
      if self.edges[index].name == name:
        if angle is not None:
          self.edges[index].setAngle(angle, flip)
        return self
    except:
      pass

    self.disconnect(index)

    e = HyperEdge.edge(allEdges, name, length=self.edgeLength(index), face=self, angle=angle, flip=flip)
    self.edges[index] = e

    return self

  def replaceEdge(self, oldEdge, newEdge, angle, flip):
    for (i, e) in enumerate(self.edges):
      if e is oldEdge:
        self.disconnect(i)
        self.edges[i] = newEdge
        newEdge.join(self.edgeLength(i), self, angle=angle, flip=flip)
    return self

  def edgeIndex(self, name):
    for (i, e) in enumerate(self.edges):
      if name == e.name:
        return i

  def edgeCoords(self, index):
    return (self.pts2d[index-1], self.pts2d[index])

  def edgeLength(self, edgeIndex):
    return self.lens[edgeIndex]
    #coords = self.edgeCoords(edgeIndex)
    #pt1 = np.array(coords[0])
    #pt2 = np.array(coords[1])

    #d = pt2 - pt1
    #return np.norm(d)

  def rotate(self, n=1):
    for i in range(n):
      self.edges.append(self.edges.pop(0))
      self.pts2d.append(self.pts2d.pop(0))

    return self

  def flip(self):
    newEdges = []
    newPts = []
    while self.edges:
      newEdges.append(self.edges.pop())
      newEdges[-1].flipConnection(self)
      newPts.append(self.pts2d.pop())
    newEdges.insert(0, newEdges.pop())
    self.edges = newEdges
    self.pts2d = newPts
    return self

  def transform(self, scale=1, angle=0, origin=(0,0)):
    r = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]]) * scale
    o = np.array([origin] * len(self.pts2d))

    pts = np.transpose(np.dot(r, np.transpose(np.array(self.pts2d)))) + o
    self.pts2d = [tuple(x) for x in np.rows(pts)]
    for (i, d) in enumerate(self.decorations):
      o = np.array([origin] * len(d[0]))
      pts = np.transpose(np.dot(r, np.transpose(np.array(d[0])))) + o
      self.decorations[i] = ([tuple(x) for x in np.rows(pts)], d[1])

  def disconnectFrom(self, edgename):
    for (i, e) in enumerate(self.edges):
      if edgename == e.name:
        return self.disconnect(i)
    return self

  def disconnectAll(self):
    for i in range(len(self.edges)):
      self.disconnect(i)
    return self

  def disconnect(self, index):
    e = self.edges[index]

    if e is None:
      return self

    self.edges[index] = None
    e.remove(self)
    return self

  def allNeighbors(self):
    n = []
    for es in self.neighbors():
      n.extend(es)
    return n

  def neighbors(self):
    n = []
    for e in self.edges:
      if e is None:
        n.append([])
      else:
        n.append([f.name for f in e.faces if f.name != self.name])
    return n

  def copy(self, name):
    return Face(name, self.pts2d, decorations=self.decorations, recenter=False)
    
  def matches(self, other):
    if len(self.pts2d) != len(other.pts2d):
      return False
    #XXX TODO: verify congruence
    bothpts = zip(self.pts2d, other.pts2d)
    return True

  def addDecoration(self, pts):
    self.decorations.append(pts)

  def preTransform(self, edge):
    index = self.edges.index(edge)
    print edge
    print self.edgeCoords(index)
    return np.dot(RotateOntoX(*self.edgeCoords(index)), MoveToOrigin(self.pts2d[index]))

  def place(self, edgeFrom, transform2D, transform3D, component=None, placed=None):
    if self.transform2D is not None and self.transform3D is not None and placed is not None and self in placed['faces']:
      # TODO : verify that it connects appropriately along alternate path
      # print "Repeated face : " + self.name
      return

    if placed is None:  # Replacing the entire component
      placed = {'faces': []}

    # Face is being placed
    placed['faces'].append(self)

    if edgeFrom is not None:
      r = self.preTransform(edgeFrom)
    else:
      r = np.eye(4)

    self.transform2D = np.dot(transform2D, r)
    self.transform3D = np.dot(transform3D, r)

    pts2d = np.dot(r, self.pts4d)[0:2, :]

    coords2D = self.get2DCoords()
    coords3D = self.get3DCoords()

 #   if component:
 #     coords2D = component.evalEquation(coords2D)
#      coords3D = component.evalEquation(coords3D)

    for (i, e) in enumerate(self.edges):
      # XXX hack: don't follow small edges
      if e is None or e.isTab():
        continue

      el = self.edgeLength(i)
      try:
        if el <= 0.01:
          continue
      except TypeError:
        print 'sympyicized variable detected - ignoring edge length check'

      da = e.faces[self]
      if da[1]:
        e.place((coords2D[:, i - 1], coords2D[:, i]), (coords3D[:, i - 1], coords3D[:, i]))
      else:
        e.place((coords2D[:, i], coords2D[:, i - 1]), (coords3D[:, i], coords3D[:, i - 1]))

      if len(e.faces) <= 1:
        # No other faces to be found, move on to next edge.
        continue

      pt1 = pts2d[:, i - 1]
      pt2 = pts2d[:, i]

      # TODO : Only skip self and the face that you came from to verify multi-connected edges
      # XXX : Assumes both faces have opposite edge orientation
      #       Only works for non-hyper edges -- need to store edge orientation info for a +/- da
      for (f, a) in e.faces.iteritems():
        if a[1] ^ da[1]:
          # opposite orientation
          pta, ptb = pt1, pt2
        else:
          # same orientation
          pta, ptb = pt2, pt1

        x = RotateXTo(ptb, pta)

        r2d = np.eye(4)
        r2d = np.dot(x, r2d)
        r2d = np.dot(MoveOriginTo(pta), r2d)

        r3d = RotateX(np.deg2rad(a[0] + da[0]))
        r3d = np.dot(x, r3d)
        r3d = np.dot(MoveOriginTo(pta), r3d)

        f.place(e, np.dot(transform2D, r2d), np.dot(transform3D, r3d), component=component, placed=placed)

  def getTriangleDict(self, component=None):
    print self.pts2d
    #if len(self.pts2d > 0):
    #  print type(self.pts2d[0])
    vertices = self.pts2d

    segments = [(i, (i+1) % len(vertices)) for i in range(len(vertices))]

    holes = []

    for d in ( x[0] for x in self.decorations if x[1] == "hole" ):
      lv = len(vertices)
      ld = len(d)
      vertices.extend( d )
      segments.extend( [(lv + ((i+1) % ld), lv+i) for i in range(ld)] )
      holes.append( tuple(np.sum([np.array(x) for x in d])/len(d) ))

    if holes:
      return dict(vertices=(vertices), segments=(segments), holes=(holes))
    else:
      return dict(vertices=(vertices), segments=(segments))

  def get2DCoords(self):
    if self.transform2D is not None:
      return np.dot(self.transform2D, self.pts4d)[0:2,:]

  def get2DCOM(self):
    if self.transform2D is not None:
      return np.dot(self.transform2D, self.com4d)[0:2,:]

  def get2DDecorations(self):
    if self.transform2D is not None:
      edges = []
      for i, e in enumerate(self.decorations):
        if e[1] == "hole":
          for j in range(len(e[0])):
            name = self.name + ".d%d.e%d" % (i,j)
            pt1 = np.dot(self.transform2D, np.array(list(e[0][j-1]) + [0,1]))[0:2]
            pt2 = np.dot(self.transform2D, np.array(list(e[0][j]) + [0,1]))[0:2]
            # XXX use EdgeType appropriately
            edges.append([name, pt1, pt2, 1])
        else:
          name = self.name + ".d%d" % i
          pt1 = np.dot(self.transform2D, np.array(list(e[0][0]) + [0,1]))[0:2]
          pt2 = np.dot(self.transform2D, np.array(list(e[0][1]) + [0,1]))[0:2]
          edges.append([name, pt1, pt2, e[1]])
      return edges
    return []

  def get3DCoords(self):
    if self.transform3D is not None:
      return np.dot(self.transform3D, self.pts4d)[0:3,:]

  def get3DCOM(self):
    if self.transform3D is not None:
      return np.dot(self.transform3D, self.com4d)[0:3,:]

  def get3DNormal(self):
    if self.transform3D is not None:
      o = np.dot(self.transform3D, np.array([0,0,0,1]))
      z = np.dot(self.transform3D, np.array([0,0,1,1]))
      return (z-o)[0:3,:]

  def __eq__(self, other):
    return self.name == other.name

  def get6DOF(self):
    if self.transform3D is not None:
      return get6DOF(self.transform3D)
    else:
      return get6DOF(np.eye(4))

class RegularNGon(Face):
  def __init__(self, name, n, length, edgeNames=True, allEdges=None):
    pts = []
    lens = []
    radius = (length / (2 * np.sin(np.pi / n)))
    dt = (2 * np.pi / n)
    for i in range(n):
      pts.append((radius*np.cos(i * dt), radius*np.sin(i * dt)))
      lens.append(length)

    Face.__init__(self, name, pts, lens, edgeNames=edgeNames, allEdges=allEdges)

class RegularNGon2(Face):
  def __init__(self, name, n, radius, edgeNames=True, allEdges=None):
    pts = []
    lens = []
    dt = (2 * np.pi / n)
    for i in range(n):
      pts.append((radius*np.cos(i * dt), radius*np.sin(i * dt)))
      lens.append(0)
    Face.__init__(self, name, pts, lens, edgeNames=edgeNames, allEdges=allEdges)

class Square(RegularNGon):
  def __init__(self, name, length, edgeNames=True, allEdges=None):
    RegularNGon.__init__(self, name, 4, length, edgeNames=edgeNames, allEdges=allEdges)

class Rectangle(Face):
  def __init__(self, name, l, w, edgeNames=True, allEdges=None, recenter=True):
    Face.__init__(self, name, ((l, 0), (l, w), (0, w), (0,0)), [l, w, l, w], edgeNames=edgeNames, allEdges=allEdges, recenter=recenter)
    #Face.__init__(self, name, ((l/2, -w/2), (l/2, w/2), (-l/2, w/2), (-l/2,-w/2)), edgeNames=edgeNames, allEdges=allEdges)

class RightTriangle(Face):
  def __init__(self, name, l, w, edgeNames=True, allEdges=None):
    Face.__init__(self, name, ((l, 0), (0, w), (0,0)), [l, sympy.sqrt(l**2 + w**2), w], edgeNames=edgeNames, allEdges=allEdges)

class Triangle(Face):
  def __init__(self, name, a,b,c, edgeNames=True, allEdges=None, recenter=True):
    isSympy = False
    try:
      if (a > (b + c)) or (b > (a + c)) or (c > (a + b)):
        raise ArithmeticError("Side lengths do not make a triangle")
    except TypeError:
      print 'Sympyicized variable detected - ignoring edge length check'
      isSympy = True

      pt1 = (0,0)
      pt2 = (a,0)
      cosC = ((a**2)+(b**2)-(c**2))/(2.0*a*b)
      pt3x = cosC*b
      if isSympy:
        pt3y = b *sympy.sqrt(1 - (cosC ** 2))
      else:
        pt3y = b*math.sqrt(1-(cosC**2))
      pt3 = (pt3x,pt3y)
      Face.__init__(self, name, (pt1,pt2,pt3), [b, a, c], edgeNames=edgeNames, allEdges=allEdges,
                      recenter=recenter)
