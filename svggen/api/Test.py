import svggen.api.FoldedComponent as fc

if __name__ == '__main__':
    f = fc.FoldedComponent()
    connectedEdges = ['r1tr2b',
                      'r2tr3b',
                      'r3tr4b',
                      'r4tr1b',
                      'r1rr5l',
                      'r1lr6r',
                      'r2rr5t',
                      'r2lr6t',
                      'r3rr5r',
                      'r3lr6l',
                      'r4rr5b',
                      'r4lr6b',
                      ]
    for i in range(3):
        r = f.addSubcomponent('r%d' % (i + 1), 'Rectangle')

    for c in connectedEdges[:2]:
        f.addConnection((c[0:2], c[2]), (c[3:5], c[5]))
    f.make()
    f.makeOutput()
