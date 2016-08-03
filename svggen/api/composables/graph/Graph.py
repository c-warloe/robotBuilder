from svggen.api.composables.graph.HyperEdge import HyperEdge
from svggen.utils import mymath as np
from svggen.utils.utils import prefix as prefixString


def inflate(face, thickness=.1, edges=False):
  dt = np.array([[0],[0],[thickness/2.],[0]])
  nf = face-dt
  pf = face+dt

  faces = []

  if edges:
    faces.append(np.transpose(np.array((pf[:,0], nf[:,0], pf[:,1]))))
    faces.append(np.transpose(np.array((nf[:,0], nf[:,1], pf[:,1]))))
  else:
    faces.append(pf)          # top face
    faces.append(nf[:,::-1])  # bottom face

  return faces

def STLWrite(faces, filename, thickness=0):
  import triangle

  shape = None
  shells = []
  triangles = []
  for f in faces:
    r = f[0]
    A = f[1]

    facets = []
    B = triangle.triangulate(A, opts='p')
    if not 'triangles' in B:
      print "No triangles in " + f[2]
      continue

    if thickness:
      for t in [np.transpose(np.array([list(B['vertices'][x]) + [0,1] for x in (face[0], face[1], face[2])])) for face in B['triangles']]:
        facets.extend([np.dot(r, x) for x in inflate(t, thickness=thickness)])
      for t in [np.transpose(np.array([list(A['vertices'][x]) + [0,1] for x in (edge[0], edge[1])])) for edge in A['segments']]:
        facets.extend([np.dot(r, x) for x in inflate(t, thickness=thickness, edges=True)])
    else:
      for t in [np.transpose(np.array([list(B['vertices'][x]) + [0,1] for x in (face[0], face[1], face[2])])) for face in B['triangles']]:
        facets.append(np.dot(r, t))

    triangles.extend(facets)

    if thickness:
      FREECADPATH = '/usr/lib64/freecad/lib'
      import sys
      sys.path.append(FREECADPATH)
      import Part
      meshes = []
      for f in (np.transpose(t[0:3,:]) for t in facets):
        try:
          meshes.append(Part.Face(Part.Wire([Part.makeLine(tuple(f[x]), tuple(f[x-1])) for x in range(3)])))
        except RuntimeError:
          print "Skipping face: " + repr(f)
      shell = Part.makeShell(meshes)
      shells.append(shell)
      if shape is None:
        shape = shell
      else:
        shape = shape.fuse(shell)

  if shape:
    with open("freecad" + filename, 'wb') as fp:
      shape.exportStl("freecad" + filename)

  from stlwriter import Binary_STL_Writer
  faces = triangles

  with open(filename, 'wb') as fp:
    writer = Binary_STL_Writer(fp)
    writer.add_faces(faces)
    writer.close()

def DXFWrite(edges, filename):
  from dxfwrite import DXFEngine as dxf
  dwg = dxf.drawing(filename)
  for e in edges:
    if e[2] is None:
      kwargs = {"layer": "Cut"}
    else:
      kwargs = {"layer": repr(e[2])}
    dwg.add(dxf.line((e[0][0], e[0][1]), (e[1][0], e[1][1]), **kwargs))
  dwg.save()

class Graph():
  def __init__(self, transform=None):
    self.faces = []
    self.edges = []
    self.transform3D = transform or np.eye(4)

  def addFace(self, f, prefix=None, faceEdges=None, faceAngles=None, faceFlips=None):
    if prefix:
      f.prefix(prefix)
    if f in self.faces:
      raise ValueError("Face %s already in graph" % f.name)
    self.faces.append(f)

    if faceEdges is not None:
      f.renameEdges(faceEdges, faceAngles, faceFlips, self.edges)
      if prefix:
        f.prefixEdges(prefix)

    self.rebuildEdges()
    return self

  def attachFace(self, fromEdge, newFace, newEdge, prefix=None, angle=0, edgeType=None, joints=None):
    # XXX should set angle from a face, not absolute angle of the face
    self.addFace(newFace, prefix)

    if fromEdge is not None:
      newEdge = prefixString(prefix, newEdge)
      self.mergeEdge(fromEdge, newEdge, angle=angle, edgeType=edgeType, joints=joints)

  def delFace(self, facename):
    for (i, f) in enumerate(self.faces):
      if f.name == facename:
        f.disconnectAll()
        self.faces.pop(i)
        self.rebuildEdges()
        return self

    return self

  def getFace(self, name):
    for f in self.faces:
      if f.name == name:
        return f
    return None

  def getEdge(self, name):
    for e in self.edges:
      if e.name == name:
        return e
    return None

  def prefix(self, prefix):
    for e in self.edges:
      e.rename(prefixString(prefix, e.name))
    for f in self.faces:
      f.rename(prefixString(prefix, f.name))

  def renameEdge(self, fromname, toname):
    e = self.getEdge(fromname)
    if e:
      e.rename(toname)

  def rebuildEdges(self):
    self.edges = []
    for f in self.faces:
      for e in f.edges:
        if e not in self.edges:
          self.edges.append(e)

  def invertEdges(self):
    # swap mountain and valley folds
    for e in self.edges:
      for f in e.faces:
        e.faces[f] = (-e.faces[f][0], e.faces[f][1])

  def addTab(self, edge1, edge2, angle=0, width=10):
    self.mergeEdge(edge1, edge2, angle=angle, tabWidth=width)

  def mergeEdge(self, edge1, edge2, angle=0, tabWidth=None, edgeType=None, joints=None):
    e1 = self.getEdge(edge1)
    e2 = self.getEdge(edge2)
    if e1 is None:
      raise AttributeError("Edge not found: " + edge1)
    if e2 is None:
      raise AttributeError("Edge not found: " + edge2)

    if len(e2.faces) > 1:
      #print "Adding third edge"
      e2.mergeWith(e1, angle=angle, flip=False, tabWidth=tabWidth)
    else:
      e2.mergeWith(e1, angle=angle, flip=True, tabWidth=tabWidth)
    self.edges.remove(e1)
    
    e2.setType(edgeType)
    if joints:
        for joint in joints.joints:
            e2.addJoint(joint)

    return self

  def splitEdge(self, edge):
    old_edge = edge
    old_edge_name = edge.name
    new_edges_and_faces = []

    for i, face in enumerate(list(old_edge.faces)):
        length = old_edge.length
        angle = old_edge.faces[face][0]
        flip = old_edge.faces[face][1]

        new_edge_name = old_edge_name + '.se' + str(i)
        new_edge = HyperEdge(new_edge_name, length)
        face.replaceEdge(old_edge, new_edge, angle, flip=False )
        new_edges_and_faces.append((new_edge_name, face, length, angle, flip))

    self.rebuildEdges()
    return new_edges_and_faces

  def tabify(self, tabFace=None, tabDecoration=None, slotFace=None, slotDecoration=None):
    for e in self.edges:
      if e.isTab():
        #print "tabbing ", e.name
        for (edgename, face, length, angle, flip) in self.splitEdge(e):
          if flip:
            #print "-- tab on: ", edgename, face.name
            if tabFace is not None:
              self.attachFace(edgename, tabFace(length, e.tabWidth), "tabedge", prefix=edgename, angle=0)
            if tabDecoration is not None:
              tabDecoration(face, edgename, e.tabWidth)
          else:
            #print "-- slot on: ", edgename, face.name
            if slotFace is not None:
              # XXX TODO: set angle appropriately
              self.attachFace(edgename, slotFace(length, e.tabWidth), "slotedge", prefix=edgename, angle=0)
            if slotDecoration is not None:
              slotDecoration(face, edgename, e.tabWidth)

    #TODO: extend this to three+ edges
    #component.addConnectors((conn, cname), new_edges[0], new_edges[1], depth, tabattachment=None, angle=0)

  def flip(self):
    return
    for f in self.faces:
      f.flip()

  def transform(self, scale=1, angle=0, origin=(0,0)):
    pass

  def dotransform(self, scale=1, angle=0, origin=(0,0)):
    for f in self.faces:
      f.transform(scale, angle, origin)

  def mirrorY(self):
    return
    for f in self.faces:
      f.transform( mirrorY())

  def mirrorX(self):
    return
    for f in self.faces:
      f.transform( mirrorX())

  def printGraph(self):
    print
    for f in self.faces:
      print f.name + repr(f.edges)

  def graphObj(self):
    g = {}
    for f in self.faces:
      g[f.name] = dict([(e and e.name or "", e) for e in f.edges])
    return g

  def showGraph(self):
    import objgraph
    objgraph.show_refs(self.graphObj(), max_depth = 2, filter = lambda x : isinstance(x, (dict, HyperEdge)))

  def place(self, force=False, assembling = False):
    if force:
        self.unplace()
    transform2D = np.eye(4)
    transform3D = self.transform3D
    self.faces[0].place(None, transform2D, transform3D)
  
  def get3DCOM(self):
    mass = 0
    com = np.zeros(3,1)
    for f in self.faces:
      mass += f.area
      com += f.get3DCOM()
    return mass, com/mass

  def unplace(self):
    for f in self.faces:
        f.transform2D = None
        f.transform3D = None
        
    for e in self.edges:
        f.pts2D = None
        f.pts3D = None

  def toSTL(self, filename):
    self.place()
    stlFaces = []
    for face in self.faces:
      if face.area > 0:
        stlFaces.append([face.transform3D, face.getTriangleDict(), face.name])
      '''
      else:
        print "skipping face:", face.name
      '''
    STLWrite(stlFaces, filename)

  def toSVG(self, filename):
    # XXX TODO
    self.place()
    dxfEdges = [list(e.pts2D) + [e.getInteriorAngle()] for e in self.edges if e.pts2D is not None]
    DXFWrite(dxfEdges, filename)

  def toDXF(self, filename):
    self.place()
    dxfEdges = [list(e.pts2D) + [e.getInteriorAngle()] for e in self.edges if e.pts2D is not None]
    DXFWrite(dxfEdges, filename)

  '''
  @staticmethod
  def joinAlongEdge((g1, prefix1, edge1), (g2, prefix2, edge2), merge=True, useOrigEdge=False, angle=0):
    # TODO(mehtank): make sure that edges are congruent

    g = Graph()
    for f in g1.faces:
      g.addFace(f.copy(prefix(prefix1, f.name)), faceEdges = [prefix(prefix1, e.name) for e in f.edges])

    return g.attach(edge1, (g2, prefix2, edge2), merge=merge, useOrigEdge=useOrigEdge, angle=angle)

  @staticmethod
  def joinAlongFace((g1, prefix1, face1), (g2, prefix2, face2), toKeep=1):
    # TODO(mehtank): make sure that faces are congruent
    g = Graph()
    for f in g1.faces:
      g.addFace(f.copy(prefix1 + "." + f.name), faceEdges = [prefix1 + "." + e.name for e in f.edges])
    for f in g2.faces:
      g.addFace(f.copy(prefix2 + "." + f.name), faceEdges = [prefix2 + "." + e.name for e in f.edges])
    f1 = g.getFace(prefix1 + "." + face1)
    f2 = g.getFace(prefix2 + "." + face2)
    for (e1, e2) in zip(f1.edges, f2.edges):
      e1.mergeWith(e2)
    if toKeep < 2:
      g.delFace(f2.name)
    if toKeep < 1:
      g.delFace(f1.name)
    return g
  '''
