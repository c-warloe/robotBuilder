from svggen.api.component import Component

c = Component()

c.addSubcomponent("left", "RectBeam")
c.addSubcomponent("right", "RectBeam")
c.addSubcomponent("tail", "Bumper") # invert?

c.addConnection(("left", "topedge2"),
                ("right", "topedge0"))
c.addConnection(("right", "botedge0"),
                ("left", "botedge2"),
                tabWidth=10)

c.addConnection(("right", "botedge2"),
                ("tail", "topedge1"))
c.addConnection(("tail", "botedge1"),
                ("left", "topedge2"),
                tabWidth=10)

'''
c.addSubcomponent("sim", "Simulation")
c.addConnection(("sim", "sim"),
                ("left", "input"), input=True)
c.addConnection(("sim", "sim"),
                ("right", "input"), input=True)
c.addConnection(("sim", "sim"),
                ("tail", "tail"), output=True, ground=True, slide=True)
c.addConnection(("sim", "sim"),
                ("left", "wheel"), output=True, ground=True, roll=True)
c.addConnection(("sim", "sim"),
                ("right", "wheel"), output=True, ground=True, roll=True)
'''

c.toYaml("library/SegBase.yaml")
