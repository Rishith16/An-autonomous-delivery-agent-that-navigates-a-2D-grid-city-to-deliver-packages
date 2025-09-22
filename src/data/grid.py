# src/data/grid.py

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.obstacles = set()
        self.costs = {}

    def in_bounds(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols

    def is_obstacle(self, x, y):
        return (x, y) in self.obstacles

    def add_obstacle(self, x, y):
        self.obstacles.add((x, y))

    def add_cost(self, x, y, cost):
        self.costs[(x, y)] = cost

    def get_cost(self, x, y):
        return self.costs.get((x, y), 1)  # default = 1

    def neighbors(self, x, y):
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        result = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and not self.is_obstacle(nx, ny):
                result.append((nx, ny))
        return result
    def remove_obstacle(self, x, y):
        self.obstacles.discard((x, y))

    @property
    def width(self):
        return self.cols

    @property
    def height(self):
        return self.rows
