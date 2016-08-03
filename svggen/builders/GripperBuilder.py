from svggen.api.component import Component

c = Component()

c.addSubcomponent("lfinger","Finger")
c.addSubcomponent("rfinger","Finger")
c.addSubcomponent("base","Tetrahedron")

c.addParameter("ratio", 1.5)
c.addParameter("fingerlength")
c.addParameter("fingerwidth")
c.addParameter("width")
c.addParameter("depth")

c.addConstConstraint(("lfinger","shape"), 3)
c.addConstraint(("lfinger","beamwidth"), "fingerwidth")
c.addConstraint(("lfinger","length"), "fingerlength")
c.addConstraint(("lfinger","ratio"), "ratio")
c.addConstConstraint(("lfinger","phase"), 1)

c.addConstConstraint(("rfinger","shape"), 3)
c.addConstraint(("rfinger","beamwidth"), "fingerwidth")
c.addConstraint(("rfinger","length"), "fingerlength")
c.addConstraint(("rfinger","ratio"), "ratio")
c.addConstConstraint(("rfinger","phase"), -3)

c.addConstraint(("base","perimeter"), ("depth", "width"), "sum(x)*2")
c.addConstraint(("base","end"), ("depth", "width"), "(x[1]-x[0]) * 1.0 / sum(x)")
c.addConstraint(("base","start"), ("depth", "width", "fingerwidth"), "(2*x[2]-x[1]-x[0]) * 1.0 / (x[0]+x[1])")

c.addConnection(("lfinger", "botedge"), ("base","startedge2"),angle=0)
c.addConnection(("rfinger", "botedge"), ("base","startedge4"),angle=0)

for i in range(4):
  c.inheritInterface("botedge%d" % i, ("base","endedge%d" % i))

c.toYaml("library/Gripper.yaml")
