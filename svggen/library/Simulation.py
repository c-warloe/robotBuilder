from svggen.api.component import Component
from svggen.api.ports.SimulationPort import SimulationPort


class Simulation(Component):
  def assemble(self):
    self.addInterface("sim", SimulationPort(self))

if __name__ == "__main__":
    h = Simulation()
    #h._make_test()

