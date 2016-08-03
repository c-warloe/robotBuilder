from Port import Port
from svggen.utils.utils import prefix as prefixString

class PointPort(Port):
  def __init__(self, parent, graph=None, face=None, edge=None, cross=None):

    if graph is not None:
      _, pt = graph.get3DCOM()
    elif face is not None:
      pt = face.get3DCOM()
    elif edge is not None:
      if cross is None:
        pt = edge.get3DCOM()
      else:
        from itertools import product
        for (p1, p2) in product(edge.pts3D, cross.pts3D):
          if p1 == p2:
            pt = p1
            break
        else:
          raise ValueError("Can't find edge intersection")
    else:
      raise ValueError("No geometry specified for PointPort")

    params = {'dx': pt[0], 'dy': pt[1], 'dz': pt[2]}
    Port.__init__(self, parent, params)
