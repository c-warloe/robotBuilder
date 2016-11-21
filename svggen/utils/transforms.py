from svggen.utils import mymath as np


def MirrorX():
  return np.diag([-1, 1, 1, 1])

def MirrorY():
  return np.diag([1, -1, 1, 1])

def Scale(scale):
  return np.diag([scale, scale, scale, 1])

def RotateX(angle):
  r = np.array([[1, 0, 0, 0],
                [0, np.cos(angle), -np.sin(angle), 0],
                [0, np.sin(angle),  np.cos(angle), 0],
                [0, 0, 0, 1]])
  return r
Roll = RotateX

def RotateY(angle):
  r = np.array([[np.cos(angle), 0, np.sin(angle), 0],
                [0, 1, 0, 0],
                [-np.sin(angle), 0,  np.cos(angle), 0],
                [0, 0, 0, 1]])
  return r
Pitch = RotateY

def RotateZ(angle):
  r = np.array([[np.cos(angle), -np.sin(angle), 0, 0],
                [np.sin(angle),  np.cos(angle), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]])
  return r
Yaw = RotateZ

def NormalizeQuat(quat):
  w,x,y,z = quat
  mag = (w**2+x**2+y**2+z**2)**(0.5)
  return (w/mag,x/mag,y/mag,z/mag)

def MultiplyQuat(quaternion1, quaternion0):
  w0, x0, y0, z0 = quaternion0
  w1, x1, y1, z1 = quaternion1
  return np.array([-x1*x0 - y1*y0 - z1*z0 + w1*w0,
                       x1*w0 + y1*z0 - z1*y0 + w1*x0,
                      -x1*z0 + y1*w0 + z1*x0 + w1*y0,
                       x1*y0 - y1*x0 + z1*w0 + w1*z0])

def InverseQuat(quat):
  w,x,y,z = quat
#  mag = (w**2+x**2+y**2+z**2)**(0.5)
  mag = 1
  return (w/mag,-x/mag,-y/mag,-z/mag)

def quat2DCM(quat):
  (a, b, c, d) = quat
  r = np.array([[a**2 + b**2 - c**2 - d**2, 2*b*c - 2*a*d, 2*b*d + 2*a*c, 0],
                [2*b*c + 2*a*d, a**2 - b**2 + c**2 - d**2, 2*c*d - 2*a*b, 0],
                [2*b*d - 2*a*c, 2*c*d + 2*a*b, a**2 - b**2 - c**2 + d**2, 0],
                [0, 0, 0, 1]])
  return r

def MoveToOrigin(pt):
  return Translate([-pt[0], -pt[1], 0])

def RotateOntoX(pt, pt2=(0,0)):
  print pt[0]
  print type(pt[0])
  print pt2[1]
  dx = pt[0] - pt2[0]
  dy = pt[1] - pt2[1]
  l = np.sqrt(dx * dx + dy * dy)
  dx = dx / l
  dy = dy / l
  r = np.array([[ dx,  dy, 0, 0],
                [-dy,  dx, 0, 0],
                [  0,   0, 1, 0],
                [  0,   0, 0, 1]])
  return r

def RotateXTo(pt, pt2=(0,0)):
  dx = pt[0] - pt2[0]
  dy = pt[1] - pt2[1]
  l = np.sqrt(dx * dx + dy * dy)
  dx = dx / l
  dy = dy / l
  r = np.array([[ dx, -dy, 0, 0],
                [ dy,  dx, 0, 0],
                [  0,   0, 1, 0],
                [  0,   0, 0, 1]])
  return r


def ReflectAcross2D(edge):
    x1 = edge.pts2D[0][0]
    y1 = edge.pts2D[0][1]
    x2 = edge.pts2D[1][0]
    y2 = edge.pts2D[1][1]
    dx = (x1-x2)
    if dx == 0: #Edge is a vertical line
        shift = np.array([[ 1, 0, 0, -x1],
                          [ 0, 1, 0,   0],
                          [ 0, 0, 1,   0],
                          [ 0, 0, 0,   1]])
        shift2 = np.array([[1, 0, 0, x1],
                           [0, 1, 0,  0],
                           [0, 0, 1,  0],
                           [0, 0, 0,  1]])
        reflect = np.array([[-1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])
        r = np.dot(shift2,np.dot(reflect,shift))
        return r
    m = (y1-y2)/dx
    b = (m*x1)+y1
    d = 1 + (m*m)
    #Product of two opposite shifts of b in the y direction and a reflection across y = mx
    r = np.array([[(2-d)/d,  2*m/d,-2*m*b/d, 0],
                  [  2*m/d,(d-2)/d,   2*b/d, 0],
                  [      0,      0,       1, 0],
                  [      0,      0,       0, 1]])
    return r

def MoveOriginTo(pt):
  return Translate([pt[0], pt[1], 0])

def Translate(origin):
  r = np.array([[1, 0, 0, origin[0]],
                [0, 1, 0, origin[1]],
                [0, 0, 1, origin[2]],
                [0, 0, 0, 1]])
  return r

def get6DOF(dcm):
  sixdof = {}
  sixdof["dx"] = dcm[0,3]
  sixdof["dy"] = dcm[1,3]
  sixdof["dz"] = dcm[2,3]
  for row in range(3):
    for col in range(3):
      sixdof["dcm%d%d" % (row, col)] = dcm[row,col]
  return sixdof

def DCM2quat(dcm):
  den = np.array([ 1.0 + dcm[0,0] + dcm[1,1] + dcm[2,2],
                   1.0 + dcm[0,0] - dcm[1,1] - dcm[2,2],
                   1.0 - dcm[0,0] + dcm[1,1] - dcm[2,2],
                   1.0 - dcm[0,0] - dcm[1,1] + dcm[2,2] ])
  #max_index = [x[0] for x in enumerate(list(den)) if x[1] == max(den)][0]
  max_index = 0 # XXX Can't find symbolically?

  q = [0]*4
  q[max_index] = 0.5 * np.sqrt(den[max_index])
  denom = 4.0 * q[max_index]

  if (max_index == 0):
     q[1] = -(dcm[1,2] - dcm[2,1]) / denom
     q[2] = -(dcm[2,0] - dcm[0,2]) / denom
     q[3] = -(dcm[0,1] - dcm[1,0]) / denom
  if (max_index == 1):
     q[0] = -(dcm[1,2] - dcm[2,1]) / denom
     q[2] =  (dcm[0,1] + dcm[1,0]) / denom
     q[3] =  (dcm[0,2] + dcm[2,0]) / denom
  if (max_index == 2):
     q[0] = -(dcm[2,0] - dcm[0,2]) / denom
     q[1] =  (dcm[0,1] + dcm[1,0]) / denom
     q[3] =  (dcm[1,2] + dcm[2,1]) / denom
  if (max_index == 3):
     q[0] = -(dcm[0,1] - dcm[1,0]) / denom
     q[1] =  (dcm[0,2] + dcm[2,0]) / denom
     q[2] =  (dcm[1,2] + dcm[2,1]) / denom

  return q
