from svggen.api.component import Component
from svggen.utils.utils import printEquations, printParameters


def connect(a, b, **kwargs):
  c.addConnection(('l%d' % a, 'p1'),
                  ('l%d' % b, 'p0'), **kwargs)

'''
Pantograph:

       /\ 
   l2 /  \ l4
     /    \
    X      X
l1 / \    / \ l6
  /   \  /   \ 
 /  l3 \/ l5  \

'''

c = Component()

for i in range(1,7):
  c.addSubcomponent("l%d" % i, "Link")

connect(1, 2, angle=0)
connect(1, 3)
connect(2, 4)
connect(3, 5)
connect(4, 5, angle=0)
connect(5, 6)

c.make()

print "Parameters: "
printParameters(c)
print
print "Equations: "
printEquations(c)
