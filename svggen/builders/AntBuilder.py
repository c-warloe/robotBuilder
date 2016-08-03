from svggen.api.component import Component

c = Component()

c.addSubcomponent("brain", "Brains", inherit="length", prefix=None)
c.addSubcomponent("front", "LegPair", inherit=True, prefix=None)
c.addSubcomponent("back", "LegPair", inherit=True, prefix=None)

c.addConstConstraint(('front', 'flip'), True)
c.addConstConstraint(('front', 'label'), 'Front Leg')
c.addConstConstraint(('back', 'label'), 'Back Leg')

# Add new UI control for moving both legs at once#
c.addSubcomponent('slider', 'UISlider', inherit="controller", prefix=None)
c.addConnection(('slider', 'curPosition'),
                ('front', 'legControl'))
c.addConnection(('slider', 'curPosition'),
                ('back', 'legControl'))
c.addConstConstraint(('slider', 'min'), -50)
c.addConstConstraint(('slider', 'default'), 0)
c.addConstConstraint(('slider', 'max'), 50)
c.addConstConstraint(('slider', 'label'), 'Both Legs')

c.addSubcomponent('bluetooth', 'BluetoothModule', inherit="controller", prefix=None)
c.addConstConstraint(("bluetooth", 'RX.controllerPin'), 10) # optional, will auto-connect if omitted
c.addConstConstraint(("bluetooth", 'TX.controllerPin'), 11) # optional, will auto-connect if omitted

c.addConstraint(("brain", "brain"), "controller")
c.addConstraint(("bluetooth", "controller"), "controller")

c.addConstConstraint(("front","controllerPin"), 3)
c.addConstraint(("front", "width"), ("controller", "servo"), "x[0].getDimension('width') + " + 
                                                                         "x[1].getParameter('motorheight') * 2")
c.addConstConstraint(("back","controllerPin"), 9)
c.addConstraint(("back", "width"), ("controller", "servo"), "x[0].getDimension('width') + " + 
                                                                        "x[1].getParameter('motorheight') * 2")

c.addConnection(("brain", "botedge0"),
                ("front", "topedge1"),
                angle=-180)
c.addConnection(("brain", "topedge2"),
                ("back", "topedge1"),
                angle=-180)

c.addConnection(("front", "botedge1"),
                ("back", "topedge3"),
                angle=-180, tabWidth=6)
c.addConnection(("back", "botedge1"),
                ("front", "topedge3"),
                angle=-180, tabWidth=6)

c.toYaml("library/Ant.yaml")
