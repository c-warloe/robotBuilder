from Port import Port
import svggen.utils.mymath as math

class SimulationPort(Port):
  numInputs = 0
  numOutputs = 0

  def __init__(self, parent):
    Port.__init__(self, parent, {})

  def constrain(self, parent, toPort, **kwargs):
    constraints = []
    for (k, p) in toPort.parameters.iteritems():
      if kwargs.get("input", False):
        name = "siminput%d_%s" % (SimulationPort.numInputs, k)
        i = parent.addParameter(name, p, input=True)
        constraints.append(math.Eq(i, p))
        SimulationPort.numInputs += 1

      if kwargs.get("output", False):
        name = "simoutput%d_%s" % (SimulationPort.numOutputs, k)
        i = parent.addParameter(name, p, output=True)
        constraints.append(math.Eq(i, p))
        SimulationPort.numOutputs += 1

    if kwargs.get("ground", False):
      pts = toPort.getPts()
      eqns2 = []
      for pt in pts:
        constraints.append(math.Relational(pt[2], 0, ">="))
        eq2 = math.Eq(pt[2], 0)

        if kwargs.get("noslip", False) or kwargs.get("noslip_x", False):
          eq2 = eq2 & math.Eq(math.D(pt[0]), 0)
        if kwargs.get("noslip", False) or kwargs.get("noslip_y", False):
          eq2 = eq2 & math.Eq(math.D(pt[1]), 0)

        eqns2.append(eq2)
      constraints.append(math.Or(*eqns2))

    return constraints
