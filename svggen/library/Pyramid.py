from svggen.api.FoldedComponent import FoldedComponent


class Pyramid(FoldedComponent):
    connectedEdges = ['t1at2b',
                      't2at3b',
                      't3at4b',
                      't4at1b',
                      'r1tt1c',
                      'r1rt2c',
                      'r1bt3c',
                      'r1lt4c'
                      ]
    def define(self):
        self.addSubcomponent('r1','Rectangle')
        for i in range(4):
            self.addSubcomponent('t%d' % (i+1), 'Triangle')
        for c in self.connectedEdges[:]:
            self.addConnection((c[0:2],c[2]),(c[3:5],c[5]))

if __name__ == '__main__':
    p = Pyramid()
    p.makeOutput()