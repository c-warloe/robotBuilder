import os
import glob

from svggen.api.component import Component


pyComponents = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py") if os.path.basename(f)[0] != "_"]
yamlComponents = [ os.path.basename(f)[:-5] for f in glob.glob(os.path.dirname(__file__)+"/*.yaml")]
allComponents = list(set(pyComponents + yamlComponents))

def getComponent(c, **kwargs):
  try:
    mod = __import__(c, fromlist=[c, "library." + c], globals=globals())
    obj = getattr(mod, c)()
  except ImportError:
    obj = Component(os.path.abspath(os.path.dirname(__file__)) + "/" + c + ".yaml")

  for k, v in kwargs.iteritems():
    if k == 'name':
      obj.setName(v)
    else:
      obj.setParameter(k, v)
  if 'name' not in kwargs:
    obj.setName(c)

  return obj

# tag : [[required ports], [forbidden ports]]                                                                                                                                       
tagDefinitions = {
  'sensor': [["DataOutputPort"],[]],
  'actuator': [["DataInputPort"],[]],
  'mechanical': [["EdgePort"],[]],
  'device': [["MountPort"],[]],
  'UI': [[],["MountPort", "EdgePort"]]
}

def tag(ports):
  tags = {}
  portset = set(ports.keys())
  for tag, (must, cant) in tagDefinitions.iteritems():
    if set(must).issubset(portset) and not len(set(cant).intersection(portset)):
      tags[tag] = [port for ptype in must for port in ports[ptype] ]
  return tags

_taggedComponents = {}
def getTags(x):
  if x in _taggedComponents:
    return _taggedComponents[x]

  try:
    c = getComponent(x)
  except:
    return None

  if isinstance(c, Component):
    interfaces = c.interfaces.keys()
    ports = {}
    for iname in interfaces:
      i = c.getInterface(iname)
      iclass = i.__class__.__name__
      try:
        ports[iclass].append(iname)
      except KeyError:
        ports[iclass] = [iname]
    _taggedComponents[x] = tag(ports)
    return tag(ports)
  return None

def taggedComponents(components = None):
  if components == None:
    components = allComponents
  for x in components:
    if getTags(x):
      yield x, getTags(x)

def filterComponents(tagList, components = None):
  for x, tags in taggedComponents(components):
    if set(tagList).issubset(set(tags.keys())):
      yield x, [port for tag in tagList for port in tags[tag] ]

