from svggen.api.component import Component
import svggen.utils.mymath as np
from svggen.utils.transforms import Roll, Pitch, Yaw, quat2DCM, get6DOF, InverseQuat, MultiplyQuat, NormalizeQuat


class MechanicalComponent(Component):
  def define(self, origin=True, euler=None, quat=True, **kwargs):
    Component.define(self, **kwargs)

    if origin:
      x = self.addParameter("dx", 0, dynamic=True)
      y = self.addParameter("dy", 0, dynamic=True)
      z = self.addParameter("dz", 0, dynamic=True)
      origin = [x, y, z]
      self.transform3D = np.Matrix(4, 4, lambda i, j: i == j and 1 or j == 3  and origin[i] or 0)
    else:
      self.transform3D = np.eye(4)

    if euler:
      r = self.addParameter("roll", 0, dynamic=True)
      p = self.addParameter("pitch", 0, dynamic=True)
      y = self.addParameter("yaw", 0, dynamic=True)
      euler = [r, p, y]
      self.transform3D = np.dot(self.transform3D, Yaw(euler[2]))
      self.transform3D = np.dot(self.transform3D, Pitch(euler[1]))
      self.transform3D = np.dot(self.transform3D, Roll(euler[0]))
    elif quat:
      a = self.addParameter("q_a", 1, dynamic=True)
      b = self.addParameter("q_i", 0, dynamic=True)
      c = self.addParameter("q_j", 0, dynamic=True)
      d = self.addParameter("q_k", 0, dynamic=True)
      self.addConstraint(np.Eq(a*a + b*b + c*c + d*d, 1))
      quat = [a, b, c, d]
      self.transform3D = np.dot(self.transform3D, quat2DCM(quat))

  def getSolvingBounds(self):
    lb = {}
    ub = {}
    defs = self.getAllDefaults()
    for n in defs:
      if "dx" not in n and "dy" not in n and "dz" not in n and "q_a" not in n and "q_i" not in n and "q_k" not in n and "q_j" not in n:
        lb[n] = defs[n] * 0.1;
        ub[n] = "realmax";
      else:
        lb[n] = "-realmax";
        ub[n] = "realmax";
    return (lb,ub)

  def solve(self):
    solved = Component.solve(self)
    if len(self.subcomponents) == 0:
      return solved
    ref = self.subcomponents.keys()[0] + "_"
    dx = solved[ref + "dx"]
    dy = solved[ref + "dy"]
    dz = solved[ref + "dz"]
    quat = (solved[ref + "q_a"],solved[ref + "q_i"],solved[ref + "q_j"],solved[ref + "q_k"])
    invQuat = InverseQuat(quat)
    transformed = []
    for k,v in solved.iteritems():
        if "dx" in k:
            solved[k] -= dx
        elif "dy" in k:
            solved[k] -= dy
        elif "dz" in k:
            solved[k] -= dz
    for k,v in solved.iteritems():
        if "q_" in k:
            pref = k[:k.index("q_")]
            if pref in transformed:
              continue
            q = (solved[pref+"q_a"],solved[pref+"q_i"],solved[pref+"q_j"],solved[pref+"q_k"])
            p = (0,solved[pref+"dx"],solved[pref+"dy"],solved[pref+"dz"])
            newQ = MultiplyQuat(invQuat,q)
            newP = MultiplyQuat(p,quat)
            newP = MultiplyQuat(invQuat,newP)
            solved[pref+"q_a"],solved[pref+"q_i"],solved[pref+"q_j"],solved[pref+"q_k"] = newQ
            z,solved[pref+"dx"],solved[pref+"dy"],solved[pref+"dz"] = newP
            transformed.append(pref)
    solved["dx"],solved["dy"],solved["dz"] = 0,0,0
    solved["q_a"],solved["q_i"],solved["q_j"],solved["q_k"] = 1,0,0,0
    for s,v in solved.iteritems():
        self.setVariableSolved(s,v)
    return solved


  def get6DOF(self):
    if self.transform3D is not None:
      return get6DOF(self.transform3D)

