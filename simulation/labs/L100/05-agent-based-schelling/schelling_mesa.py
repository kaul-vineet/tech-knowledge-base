"""Same Schelling model written with Mesa 3.5.1 (pending-ci: Mesa is not installed in the sandbox).

Mesa supplies the grid, agent bookkeeping and random activation order; we write only the agent rule.
python schelling_mesa.py
"""
import mesa
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid

SIZE, EMPTY_FRAC, WANT = 30, 0.10, 0.30


class Resident(CellAgent):
    def __init__(self, model, cell, kind):
        super().__init__(model)
        self.cell, self.kind = cell, kind

    def similar_fraction(self):
        neighbours = list(self.cell.get_neighborhood(radius=1).agents)
        if not neighbours:
            return 1.0
        return sum(n.kind == self.kind for n in neighbours) / len(neighbours)

    def step(self):
        if self.similar_fraction() < WANT:  # same agent rule as schelling.py
            self.cell = self.model.grid.select_random_empty_cell()


class Schelling(mesa.Model):
    def __init__(self, seed=42):
        super().__init__(seed=seed)
        self.grid = OrthogonalMooreGrid((SIZE, SIZE), torus=True, capacity=1, random=self.random)
        cells = list(self.grid.all_cells)
        self.random.shuffle(cells)
        n_agents = len(cells) - int(len(cells) * EMPTY_FRAC)
        for i, cell in enumerate(cells[:n_agents]):
            Resident(self, cell, 1 + i % 2)

    def pct_similar(self):
        return 100 * sum(a.similar_fraction() for a in self.agents) / len(self.agents)

    def pct_unhappy(self):
        return 100 * sum(a.similar_fraction() < WANT for a in self.agents) / len(self.agents)

    def step(self):
        self.agents.shuffle_do("step")  # random activation order each tick


if __name__ == "__main__":
    model = Schelling()
    print(f"Mesa start: % similar {model.pct_similar():.1f}")
    for i in range(50):
        model.step()
        if model.pct_unhappy() == 0:
            break
    print(f"Mesa end after {i + 1} steps: % similar {model.pct_similar():.1f}, % unhappy {model.pct_unhappy():.1f}")
