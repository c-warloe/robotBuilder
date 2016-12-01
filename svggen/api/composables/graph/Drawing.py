from math import pi

from DrawingEdge import *
from svggen.utils.utils import prefix as prefixString
from svggen.utils.transforms import *
from svggen.utils import mymath as np
from shapely import geometry


def diffEdge(pts1, pts2, dimension, tolerance = 0.01):
  if tolerance < 0:
    tolerance = -tolerance
  for i in range(2):
    for j in range(dimension):
      diff1 = pts1[i][j] - pts2[i][j]
      diff2 = pts1[1-i][j] - pts2[i][j]
      if (tolerance < diff1 or diff1 < -tolerance) and (tolerance < diff2 or diff2 < -tolerance): #Allow for some difference due to double precision
        return True
  return False

def intersectsEdge(edge1, edge2, tolerance = 0.01):
  a = edge1[0]
  b = edge1[1]
  c = edge2[0]
  d = edge2[1]
  rot1 = crossProdSign(a,b,d)
  rot2 = crossProdSign(a,b,c)
  rot3 = crossProdSign(a,c,d)
  rot4 = crossProdSign(b,c,d)
  if (rot1 != rot2 and rot1 != 0 and rot2 != 0) and (rot3 != rot4 and rot3 != 0 and rot4 != 0): #Signs are different
    return True
  return False

def intersectsFace(edge, faceedges):
  for e in faceedges:
    if intersectsEdge(edge, e):
      return True
  return False

def crossProdSign(a, b, c):
  if round((((c[1] - a[1]) * (b[0] - a[0])) - ((b[1] - a[1]) * (c[0] - a[0]))),3) > 0: #Cross product is positive
    return 1
  elif round((((c[1] - a[1]) * (b[0] - a[0])) - ((b[1] - a[1]) * (c[0] - a[0]))),3) == 0: #Cross product is zero
    return 0
  return -1 #Cross product is negative

def boundingBox(coords):
  try:
    coords[0][0]
  except TypeError:
    coords = coords.tolist()
  minX = coords[0][0]
  maxX = coords[0][0]
  minY = coords[1][0]
  maxY = coords[1][0]
  for p in coords[0][1:]:
    if p > maxX:
      maxX = p
    if p < minX:
      minX = p
  for p in coords[1][1:]:
    if p > maxY:
      maxY = p
    if p < minY:
      minY = p
  return ((minX,maxX),(minY,maxY))

def intersectsBoundingBox(box1, box2):
  if box1[0][0] > box2[0][1] or box2[0][0] > box1[0][1]:
    return False
  if box1[1][0] > box2[1][1] or box2[1][0] > box1[1][1]:
    return False
  return True

def centroid(pts):
  sumX = 0.0
  sumY = 0.0
  for i in range(len(pts)):
    sumX += pts[i][0]
    sumY += pts[i][1]
  return (sumX/len(pts),sumY/len(pts))

def interiorPoint(coords):
  '''pts = [[x1,x2,etc.],[y1,y2,etc.]] and pts are in CCW order'''
  try:
    coords[0][0]
  except TypeError:
    coords = coords.tolist()
  coordsTwice = []
  for i in range(len(coords[0])):
    coordsTwice.append([coords[0][i],coords[1][i]])
  for i in range(len(coordsTwice)):
    print [coordsTwice[i],coordsTwice[(i+1)%len(coordsTwice)],coordsTwice[(i+2)%len(coordsTwice)]]
    if crossProdSign(coordsTwice[i],coordsTwice[(i+1)%len(coordsTwice)],coordsTwice[(i+2)%len(coordsTwice)]) > 0:
      return centroid([coordsTwice[i],coordsTwice[(i+1)%len(coordsTwice)],coordsTwice[(i+2)%len(coordsTwice)]])
  return None
def updateDimensions(dimensions, point):
  if dimensions[0][0] is None:
    return [[point[0],point[1]],[point[0],point[1]]]
  if point[0] < dimensions[0][0]:
    dimensions[0][0] = point[0]
  if point[1] < dimensions[0][1]:
    dimensions[0][1] = point[1]
  if point[0] > dimensions[1][0]:
    dimensions[1][0] = point[0]
  if point[1] > dimensions[1][1]:
    dimensions[1][1] = point[1]
  return dimensions




class Drawing:
  def __init__(self):
    """
    Initializes an empty dictionary to contain Edge instances.

    Keys will be Edge labels as strings. Key values will be Edge instances.
    """
    self.edges = {}
    self.faces = []
    self.dimensions = [[None,None],[None,None]]

  def fromGraph(self, g, component=None):
    self.component = component
    '''for e in g.edges:
      if e.pts2D is None:
        pass
        #print "No coordinates for edge: " + e.name
      else:
        if len(e.faces) == 1:
          edge = Cut()
        elif len(e.faces) == 2:
          angles = e.faces.values()
          if angles[0][1]:
            angle = angles[0][0] - angles[1][0]
          else:
            angle = angles[1][0] - angles[0][0]
          if angle == 0:
            edge = Flat()
          else:
            edge = Fold(angle=angle)
        else:
          print "Don't know how to handle edge with %d faces" % len(e.faces)
          edge = None
        self.edges[e.name] = Edge(e.name, e.pts2D[0], e.pts2D[1], edge)
    for f in g.faces:
      for e in f.get2DDecorations():
        self.edges[e[0]] = Edge(e[0], e[1], e[2], EdgeType(e[3]))'''
    self.place(g.faces[0], None, np.eye(4), np.eye(4))

  def placeFace(self, edges, edgepts, coords2D, collisionCheck=True):
    try:
      coords2D[0][0]
    except TypeError:
      coords2D = coords2D.tolist()
    vertices = []
    v1 = (round(coords2D[0][0],3),round(coords2D[1][0],3))
    for i in range(len(coords2D[0])):
      #print coords2D[0][i],coords2D[1][i],"-----"
      vertex = (round(coords2D[0][i],3),round(coords2D[1][i],3))
      self.dimensions = updateDimensions(self.dimensions,vertex)
      vertices.append(vertex)
    vertices.append(v1)
    face = geometry.Polygon(vertices)
    #print len(self.faces)
    if collisionCheck:
      for f in self.faces:
        if face.crosses(f):  # or face.within(f) or face.contains(f) or f.equals(f):
          #print "cross", list(face.exterior.coords), list(f.exterior.coords)
          return False
        if face.within(f):
          #print "within", list(face.exterior.coords), list(f.exterior.coords)
          return False
        if face.contains(f):
          #print "contains", list(face.exterior.coords), list(f.exterior.coords)
          return False
        if face.equals((f)):
          #print "equals", list(face.exterior.coords), list(f.exterior.coords)
          return False
        if face.overlaps(f):
          return False

    self.faces.append(face)
    return True



  def place(self, face, edgeFrom, edgeFromPts, transform2D, placed=None):
    checkForOverlap = False
    if placed is not None and face in placed['faces']:
      # TODO : verify that it connects appropriately along alternate path
      # print "Repeated face : " + self.name
      return
    if placed is None:  # Replacing the entire component
      placed = {'faces': [], 'edges': {}, 'overlapping': []}
      checkForOverlap = True



    if edgeFrom is not None:
      r = face.preTransform(edgeFrom)  # Get Rotation angle of previous edge
    else:
      r = np.eye(4)  # Place edge as is

    # Rotate face to new direction
    facetransform2D = np.dot(transform2D, r)


    pts2d = np.dot(r, face.pts4d)[0:2, :]

    #print self.component.evalEquation(np.dot(facetransform2D, face.pts4d))
    pts2dMatrix = np.dot(r, face.pts4d)
    coords2DMatrix = np.dot(facetransform2D, face.pts4d)

    coords2D = np.dot(facetransform2D, face.pts4d)[0:2,:]

    facepts2d = []
    faceedges = []

    coords2D = self.component.evalEquation(coords2D)
    #print self.component.evalEquation(pts2d), self.component.evalEquation(face.pts4d), self.component.evalEquation(coords2D)
    for (i, e) in enumerate(face.edges):
      if e is None:
        continue

      if e.name[:4] == 'temp':
        continue

      try:
        da = e.faces[face]
      except KeyError:
        # Edge was added as a cut
        continue
      facepts2d.append((coords2D[:, i - 1], coords2D[:, i]))
      faceedges.append(e)
      '''if da[1]:
        facepts2d.append((coords2D[:, i - 1], coords2D[:, i]))
      else:
        facepts2d.append((coords2D[:, i], coords2D[:, i - 1]))


    if not self.placeFace(faceedges,facepts2d):
      raise Exception("Attemping to place overlapping faces")'''

    if not self.placeFace(faceedges,facepts2d,coords2D):
      try:
        edgeFrom = self.component.evalEquation(edgeFrom)
      except:
        pass

      reflection = ReflectAcross2Dpts(edgeFromPts)
      reflectionX = np.array([[1,  0, 0, 0],
                             [0, -1, 0, 0],
                             [0,  0, 1, 0],
                             [0,  0, 0, 1]])

      if edgeFrom is not None:
        r = face.preTransform(edgeFrom)  # Get Rotation angle of previous edge
      else:
        r = np.eye(4)  # Place edge as is
      r = np.dot(reflectionX,r)


      pts2d = np.dot(r, face.pts4d)[0:2, :]
      #print self.component.evalEquation(reflection)
      coords2D = np.dot(reflection, coords2DMatrix)[0:2, :]
      #print self.component.evalEquation(pts2d), self.component.evalEquation(face.pts4d), self.component.evalEquation(coords2D)

      facepts2d = []
      faceedges = []
      coords2D = self.component.evalEquation(coords2D)


      for (i, e) in enumerate(face.edges):
        if e is None:
          continue

        if e.name[:4] == 'temp':
          continue

        try:
          da = e.faces[face]
        except KeyError:
          # Edge was added as a cut
          continue
        facepts2d.append((coords2D[:, i - 1], coords2D[:, i]))
        faceedges.append(e)
      if not self.placeFace(faceedges, facepts2d, coords2D):
        placed['overlapping'].append(face)
        return

    # Face is being placed
    placed['faces'].append(face)
    if face in placed['overlapping']:
      placed['overlapping'].remove(face)

    for i in range(len(faceedges)):
      # Don't 2d place edges that are tabbed
      e = faceedges[i]
      if e.isTab():
        edgepts2d = None
      #Evaluate the edge coordinates
      edgepts2d = (self.component.evalEquation(facepts2d[i][0]),self.component.evalEquation(facepts2d[i][1]))

      '''for ple in placed['edges'].keys():
        if intersects(edgepts2d,placed['edges'][ple]):
          print 'Error: Edge Intersects', edgepts2d, placed['edges'][ple]
          continue'''
      # Deal with edges that are connected in 3D, but not in 2D
      if e.name in placed['edges'].keys() and diffEdge(placed['edges'][e.name],edgepts2d,2):  # If edges has already been placed, it must be cut
        #Create a new edge
        self.edges['temp'+e.name] = Edge('temp'+e.name, edgepts2d[0], edgepts2d[1], Cut())
        #Make old edge into a cut
        self.edges[e.name] = Edge(e.name, placed['edges'][e.name][0], placed['edges'][e.name][1], Cut())

      else:
        if len(e.faces) == 1:
          edge = Cut()
        else:
          edge = Fold()
        self.edges[e.name] = Edge(e.name, edgepts2d[0], edgepts2d[1], edge)
        placed['edges'][e.name] = edgepts2d

      if len(e.faces) <= 1:
        # No other faces to be found, move on to next edge.
        continue
      if e.isTab():
        # Don't follow faces off of a Tab
        continue

      # XXX hack: don't follow small edges
      el = face.edgeLength(i)
      try:
        if el <= 0.01:
          continue
      except TypeError:
        pass  # print 'sympyicized variable detected - ignoring edge length check'

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


        self.place(f, e, edgepts2d, np.dot(transform2D, r2d), placed)
    if checkForOverlap and len(placed['overlapping']):
      raise Exception('One or more faces could not be placed without overlap!')

  def toDXF(self, filename, labels=False, mode="dxf"):
    from dxfwrite import DXFEngine as dxf
    '''
    if mode == "silhouette":
      self.append(Rectangle(12*25.4, 12*25.4, edgetype=Reg()), "outline")
    '''

    dwg = dxf.drawing(filename)
    for e in self.edges.items():
      e[1].toDrawing(dwg, e[0] if labels else "", mode=mode, engine=dxf)
    dwg.save()

    '''
    if mode == "silhouette":
      self.edges.pop("outline.e0")
      self.edges.pop("outline.e1")
      self.edges.pop("outline.e2")
      self.edges.pop("outline.e3")
    '''

  def toSVG(self, filename, labels=False, mode=None, toFile=True):
    """
    Writes all Edge instances to a SVG file.

    @type svg:
    @param svg:
    @type label: tuple
    @param label: location of point two in the form (x2,y2).
    @type mode:
    @param mode:
    """
    import svgwrite

    svg = svgwrite.Drawing(filename)
    for e in self.edges.items():
      e[1].toDrawing(svg, e[0] if labels else "", mode)
    if toFile:
      svg.save()
    else:
      return svg.tostring()

  def getDimensions(self):
    return self.dimensions

  def points(self):
    """
    @return: a non-redundant list of all endpoints in tuples
    """
    points = []
    for e in self.edges.itervalues():
      coords = e.coords()
      p1 = tuple(coords[0])
      p2 = tuple(coords[1])
      points.append(p1)
      points.append(p2)
    return list(set(points))

  def edgeCoords(self):
    """
    @return: a list of all Edge instance endpoints in Drawing (can include redundant points and edges)
    """
    edges = []
    for e in self.edges.items():
      edges.append(e[1].coords())
    return edges

  def renameedge(self, fromname, toname):
    """
    Renames an Edge instance's Key

    @param fromname: string of the original Edge instance name
    @param toname: string of the new Edge instance name
    """
    self.edges[toname] = self.edges.pop(fromname)
    self.edges[toname].name = toname

    return self

  def invertEdges(self):
    """
    Swaps the mountain/valley folds on all Edge instances of Drawing
    @return: Drawing with the new Edge instances.
    """
    for e in self.edges.values():
      e.invert()
    return self

  def transform(self, scale=1, angle=0, origin=(0,0), relative=None):
    """
    Scales, rotates, and translates the Edge instances in Drawing

    @type scale: float
    @param scale: scaling factor
    @type angle: float
    @param angle: angle to rotate in radians
    @type origin: tuple
    @param origin: origin
    @return: Drawing with the new Edge instances.
    """
    if relative is not None:
      pts = [x[0] for x in self.edgeCoords()] + [x[1] for x in self.edgeCoords()]
      xs = [x[0] for x in pts]
      ys = [x[1] for x in pts]
      minx = min(xs)
      maxx = max(xs)
      miny = min(ys)
      maxy = max(ys)
      midx = minx + relative[0]*(maxx + minx)
      midy = miny + relative[1]*(maxy + miny)
      origin=(origin[0] - midx, origin[1] - midy)

    for e in self.edges.values():
      e.transform(scale=scale, angle=angle, origin=origin)

    return self

  def mirrorY(self):
    """
    Changes the coordinates of Edge instances in Drawing so that they are symmetric about the X axis.
    @return: Drawing with the new Edge instances.
    """
    for e in self.edges.values():
      e.mirrorY()
    return self

  def mirrorX(self):
    """
    Changes the coordinates of Edge instances in Drawing so that they are symmetric about the Y axis.
    @return: Drawing with the new Edge instances.
    """
    for e in self.edges.values():
      e.mirrorX()
    return self

  def flip(self):
    """
    Flips the directionality of Edge instances om Drawing around.
    @return: Drawing with the new Edge instances.
    """
    for e in self.edges.values():
      e.flip()
    return self

  def append(self, dwg, prefix = '', noGraph=False, **kwargs):
    for e in dwg.edges.items():
      self.edges[prefixString(prefix, e[0])] = e[1].copy()
      self.edges[prefixString(prefix, e[0])].transform(**kwargs)
    return self

  def duplicate(self, prefix = ''):
    #Creates a duplicate copy of self.
    c = Drawing()
    for e in self.edges.items():
      c.edges[prefixString(prefix, e[0])] = e[1].copy()
    return c

  def attach(self, label1, dwg, label2, prefix, edgetype, useOrigName = False):
    # XXX TODO(mehtank): check to see if attachment edges match?
    # XXX TOTO(mehtank): make prefix optional?

    if isinstance(label1, (list, tuple)):
      l1 = label1[0]
    else:
      l1 = label1
      label1 = [label1]

    if isinstance(label2, (list, tuple)):
      l2 = label2[0]
    else:
      l2 = label2
      label2 = [label2]

    if isinstance(edgetype, (list, tuple)):
      e12 = edgetype[0]
    else:
      e12 = edgetype
      edgetype = [edgetype] * len(label1)

    #create a copy of the new drawing to be attached
    d = dwg.duplicate()

    #move the edge of the new drawing to be attached to the origin
    d.transform(origin=(-d.edges[l2].x2, -d.edges[l2].y2))

    #don't rescale
    scale = 1

    #find angle to rotate new drawing to align with old drawing edge
    phi   = self.edges[l1].angle()
    angle = phi - d.edges[l2].angle() + pi

    #align edges offset by a separation of distance between the start points
    d.transform(scale=scale, angle=angle, origin=(self.edges[l1].coords()[0][0], self.edges[l1].coords()[0][1]))

    for e in d.edges.items():
      try:
        i = label2.index(e[0])
        e[1].edgetype = edgetype[i]
        if useOrigName:
          e[1].name = label1[label2.index(e[0])]
          self.edges[label1[label2.index(e[0])]] = e[1]
        else:
          self.edges.pop(label1[label2.index(e[0])])
          e[1].name = prefix + '.' + e[0]
          self.edges[prefix + '.' + e[0]] = e[1]
      except ValueError:
        e[1].name = prefix + '.' + e[0]
        self.edges[prefix + '.' + e[0]] = e[1]

  def times(self, n, fromedge, toedge, label, mode):
    d = Drawing()
    d.append(self, label+'0')
    for i in range(1, n):
      d.attach(label+repr(i-1)+'.'+toedge, self, fromedge, label+repr(i), mode)
    return d

class Face(Drawing):
  def __init__(self, pts, edgetype = None, origin = True):
    Drawing.__init__(self)
    if origin:
      pts = list(pts) + [(0,0)]
    else:
      pts = list(pts)

    lastpt = pts[-1]
    edgenum = 0
    edgenames = []
    for pt in pts:
      name = 'e%d' % edgenum
      self.edges[name] = Edge(name, lastpt, pt, edgetype)
      edgenames.append(name)
      lastpt = pt
      edgenum += 1

class Rectangle(Face):
  def __init__(self, l, w, edgetype = None, origin = True):
    Face.__init__(self, ((l, 0), (l, w), (0, w), (0,0)), edgetype, origin)
