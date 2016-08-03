from svggen.api.component import Component

c = Component()

c.addSubcomponent("beam", "RectBeam")
c.addSubcomponent("tail", "Rectangle") 
c.addSubcomponent("leftmotor", "ServoDevice", continuous=True)
c.addSubcomponent("leftwheel", "Wheel", n=6)
c.addSubcomponent("rightmotor", "ServoDevice", continuous=True)
c.addSubcomponent("rightwheel", "Wheel", n=6)

c.addConnection(('beam', 'face0'),
                ('rightmotor', 'mount'))
c.addConnection(('rightmotor', 'shaft'),
                ('rightwheel', 'origin'))
c.addConnection(('beam', 'face2'),
                ('leftmotor', 'mount'))
c.addConnection(('leftmotor', 'shaft'),
                ('leftwheel', 'origin'))
c.addConnection(("beam", "botedge1"),
                ("tail", "t"), angle=-90)


c.addSubcomponent("sim", "Simulation")
c.addConnection(("sim", "sim"),
                ("leftmotor", "input"), input=True)
c.addConnection(("sim", "sim"),
                ("rightmotor", "input"), input=True)
c.addConnection(("sim", "sim"),
                ("tail", "b"), ground=True)
c.addConnection(("sim", "sim"),
                ("leftwheel", "wheel"), ground=True, noslip=True)
c.addConnection(("sim", "sim"),
                ("rightwheel", "wheel"), ground=True, noslip=True)

c.toYaml("library/ReducedSeg.yaml")
