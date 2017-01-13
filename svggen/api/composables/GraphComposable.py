from graph.Graph import Graph as BaseGraph
from Composable import Composable
from svggen.utils.utils import tryImport, decorateGraph


class Decoration(Composable, BaseGraph):
  def __init__(self):
    BaseGraph.__init__(self)
  def append(self, newComposable, newPrefix):
    pass
  def attach(self, fromInterface, toInterface, kwargs):
    pass
  def makeOutput(self, filedir, **kwargs):
    pass

class Graph(Composable, BaseGraph):
  def __init__(self, transform=None, component = None):
    self.component = component
    BaseGraph.__init__(self, transform=transform, component=component)

  def append(self, g2, prefix2):
    if not g2.placed:
      if not g2.prefixed:
        g2.prefix(prefix2)
      self.faces.extend(g2.faces)
      self.edges.extend(g2.edges)
      g2.placed = True
      g2.prefixed = True


  def attach(self, port1, port2, **kwargs):
    # Test whether ports are of right type --
    # Attach if both ports contain edges to attach along
    try:
      label1 = port1.getEdges()
      label2 = port2.getEdges()
    except AttributeError:
      pass
    else:
      # XXX associate ports with specific composables so this isn't necessary
      for i in range(len(label1)):
        if label1[i] not in (e.name for e in self.edges):
          return
        if label2[i] not in (e.name for e in self.edges):
          return

      for i in range(len(label1)):
        newargs = {}
        for key, value in kwargs.iteritems():
          if key is 'tab':
            continue
          if isinstance(value, (list, tuple)):
            newargs[key] = value[i]
          else:
            newargs[key] = value
        try:
          if kwargs['tab'] is True:
            self.addTab(label1[i], label2[i], **newargs)
            continue
        except:
          pass
        self.mergeEdge(label1[i], label2[i], **newargs)
    # Attach if one port contains a Face and the other contains a Decoration
    try:
      face = self.getFace(port1.getFaceName())
      deco = port2.getDecoration()
    except AttributeError:
      try:
        face = self.getFace(port2.getFaceName())
        deco = port1.getDecoration()
      except AttributeError:
        return
    if face is None:
      # XXX associate ports with specific composables so this isn't necessary
      return
    decorateGraph(face, decoration=deco, **kwargs)

  def makeOutput(self, filedir, **kwargs):
    import sys
    if "displayOnly" in kwargs:
      kwDefault = not kwargs["displayOnly"]
      kwargs["display"] = kwargs["displayOnly"]
    else:
      kwDefault = True

    def kw(arg, default=kwDefault):
      if arg in kwargs:
        return kwargs[arg]
      return default

    from svggen.utils.tabs import BeamTabs, BeamSlotDecoration
    self.tabify(kw("tabFace", BeamTabs), kw("tabDecoration", None),
                kw("slotFace", None), kw("slotDecoration", BeamSlotDecoration))
    self.place(assembling=True)

    if kw("placeOnly", False):
      return
    '''
    print
    for f in self.faces:
      if f.transform2D is None:
        print "No 2D transform for face" , f.name
      if f.transform3D is None:
        print "No 3D transform for face" , f.name
    '''

    #if kw("placeOnly", False):
    #  return

    if kw("display") or kw("unfolding") or kw("autofolding") or kw("silhouette"):
      from graph.Drawing import Drawing
      d = Drawing()
      d.fromGraph(self, self.component)
      d.transform(relative=(0,0))

    if kw("svgString", False):
      self.component.drawing = d
      d.toDXF(filedir + "/silhouette.dxf", mode="silhouette")
      return d.toSVG('nofile', toFile=False)

    if kw("display"):
      from svggen.utils.display import displayTkinter
      displayTkinter(d)

    if kw("unfolding"):
      print "Generating cut-and-fold pattern... ",
      sys.stdout.flush()
      d.toSVG(filedir + "/lasercutter.svg", mode="Corel")
      print "done."

    if kw("unfolding"):
      print "Generating printer pattern... ",
      sys.stdout.flush()
      d.toSVG(filedir + "/print.svg", mode="print")
      print "done."

    if kw("silhouette"):
      print "Generating cut-and-fold pattern for Silhouette papercutter... ",
      sys.stdout.flush()
      d.toDXF(filedir + "/silhouette.dxf", mode="silhouette")
      print "done."

    #3D representation cannot be created without evaluating variables
    '''if kw("autofolding"):
      print "Generating autofolding pattern... ",
      sys.stdout.flush()
      d.toDXF(filedir + "/autofold-default.dxf", mode="autofold")
      print "(graph) ... ",
      sys.stdout.flush()
      self.toDXF(filedir + "/autofold-graph.dxf")
      print "done."'''

    if kw("stl"):
      print "Generating 3D model... ",
      sys.stdout.flush()
      self.toSTL(filedir + "/model.stl")
      print "done."
