from svggen.api.component import Component
from svggen.api.composables.graph.Face import Rectangle as Rect

class Cube(Component):

    _test_params = {
        'side': 100,
    }
    connectedEdges = ['r1tr2b',
                      'r2tr3b',
                      'r3tr4b',
                      #'r4tr1b',
                      #'r1rr5l',
                      #'r1lr6r'
                      ]

    def define(self):
        self.addParameter('side',100)
        for i in range(4):
            r = self.addSubcomponent('r%d' % (i+1), 'Rectangle')
            #self.addConstraint(('r%d' % (i + 1), 'l'), 'side', 'x')
            #self.addConstraint(('r%d' % (i + 1), 'w'), 'side', 'x')

        for c in self.connectedEdges:
            self.addConnection((c[0:2],c[2]),(c[3:5],c[5]))

if __name__ == '__main__':
    c = Cube()
    c.makeOutput()



