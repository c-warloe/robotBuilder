from svggen.api.component import Component

c = Component()

c.addSubcomponent("l0", "Link")
c.addSubcomponent("l1", "Link")
c.addSubcomponent("l2", "Link")

c.addConnection(('l0', 'p1'),
                ('l1', 'p0'))
c.addConnection(('l1', 'p1'),
                ('l2', 'p0'), angle=0)

c.toYaml("library/FourBarLinkage.yaml")
