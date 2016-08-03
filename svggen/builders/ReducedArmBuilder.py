from svggen.api.component import Component

c = Component()

c.addSubcomponent("l0", "ArmLink")
c.addSubcomponent("l1", "ArmLink")
c.addSubcomponent("l2", "ArmLink")

c.addConnection(('l0', 'servo'),
                ('l1', 'horn'))
c.addConnection(('l1', 'servo'),
                ('l2', 'horn'))

c.addSubcomponent("sim", "Simulation")
c.addConnection(("sim", "sim"),
                ("l0", "input"), input=True)
c.addConnection(("sim", "sim"),
                ("l1", "input"), input=True)

c.toYaml("library/ReducedArm.yaml")
