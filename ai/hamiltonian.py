class Hamiltonian:
    def __init__(self, grid_size=20):
        self.grid_size = grid_size
        self.path = self._generate_cycle()

    def _generate_cycle(self):
        path = []

        for y in range(self.grid_size):
            row = []
            for x in range(self.grid_size):
                row.append((x, y))

            if y % 2 == 0:
                path.extend(row)
            else:
                path.extend(row[::-1])

        return path

    def get_path(self, head, food, body, grid_size):
        if head not in self.path:
            return [], []

        idx = self.path.index(head)
        next_idx = (idx + 1) % len(self.path)

        next_pos = self.path[next_idx]

        return [next_pos], []