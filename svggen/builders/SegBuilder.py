from svggen.api.component import Component

c = Component()

#c.addParameter("faces", range(4))
c.addParameter("phase", 1)
c.addParameter("center", False)
c.addParameter("tailservo")
c.addParameter("driveservo")

c.addSubcomponent("brain", "Brains", inherit=("length"), prefix=None)
c.addSubcomponent("right", "Servo", inherit=True, prefix=None)
c.addSubcomponent("left", "Servo", inherit=True, prefix=None)
c.addSubcomponent("tail", "SegTail", inherit=('controller', 'height'), prefix=None)

c.addConstraint(("brain","depth"), ("controller", "driveservo"), "max(x[0].getDimension('height'), x[1].getParameter('motorwidth'))")
c.addConstraint(("right","depth"), ("controller", "driveservo"), "max(x[0].getDimension('height'), x[1].getParameter('motorwidth'))")
c.addConstraint(("left","depth"), ("controller", "driveservo"), "max(x[0].getDimension('height'), x[1].getParameter('motorwidth'))")

c.addConstraint(("right","servo"), "driveservo")
c.addConstraint(("left","servo"), "driveservo")
c.addConstraint(("tail","servo"), "tailservo")
c.addConstraint(("tail","edgelen"), "driveservo", "x.getParameter('motorwidth')")
c.addConstraint(("tail", "length"), ("controller", "driveservo"), "x[0].getDimension('width') + " +
                "x[1].getParameter('motorheight') * 2")

c.addConstConstraint(('tail', 'motionType'), 'angle')
c.addConstConstraint(('right', 'motionType'), 'continuous')
c.addConstConstraint(('left', 'motionType'), 'continuous')

c.addConstConstraint(('tail', 'label'), 'Tail Servo')
c.addConstConstraint(('right', 'label'), 'Right Wheel')
c.addConstConstraint(('left', 'label'), 'Left Wheel')

c.addConstConstraint(('tail', 'min'), 0)
c.addConstConstraint(('tail', 'default'), 90)
c.addConstConstraint(('tail', 'max'), 180)
c.addConstConstraint(('right', 'min'), -50)
c.addConstConstraint(('right', 'default'), 0)
c.addConstConstraint(('right', 'max'), 50)
c.addConstConstraint(('left', 'min'), -50)
c.addConstConstraint(('left', 'default'), 0)
c.addConstConstraint(('left', 'max'), 50)
c.addConstConstraint(('left', 'flip'), True)
c.addConstConstraint(('left', 'servoFunction'), 'input*-1')

# Add new UI control#
c.addSubcomponent('slider', 'UISlider', inherit="controller", prefix=None)
c.addConnection(('slider', 'curPosition'),
                ('right', 'servoControl'))
c.addConnection(('slider', 'curPosition'),
                ('left', 'servoControl'))
c.addConstConstraint(('slider', 'min'), -50)
c.addConstConstraint(('slider', 'default'), 0)
c.addConstConstraint(('slider', 'max'), 50)
c.addConstConstraint(('slider', 'label'), 'Both Wheels')

# Add bluetooth module
c.addSubcomponent('bluetooth', 'BluetoothModule', inherit="controller", prefix=None)
c.addConstConstraint(("bluetooth", 'RX.controllerPin'), 10) # optional, will auto-connect if omitted
c.addConstConstraint(("bluetooth", 'TX.controllerPin'), 11) # optional, will auto-connect if omitted

# Set microcontroller
c.addConstraint(("brain", "brain"), "controller")

# Set servo pins
c.addConstConstraint(("right","controllerPin"), 3)
c.addConstConstraint(("left","controllerPin"), 9)
c.addConstConstraint(("tail","controllerPin"), 5)

c.addConnection(("brain", "topedge2"),
                ("right", "topedge0"),
                angle=-180)
'''
c.addConnection(("right", "botedge0"),
                ("brain", "topedge0"),
                angle=-180, tabWidth=10)
'''

c.addConnection(("brain", "botedge0"),
                ("left", "topedge0"),
                angle=-180)
c.addConnection(("left", "botedge0"),
                ("brain", "topedge0"),
                angle=-180, tabWidth=10)

c.addConnection(("right", "botedge2"),
                ("tail", "rightedge"),
                angle=90)
c.addConnection(("tail", "leftedge"),
                ("left", "topedge2"),
                angle=90, tabWidth=10)

c.toYaml("library/Seg.yaml")
