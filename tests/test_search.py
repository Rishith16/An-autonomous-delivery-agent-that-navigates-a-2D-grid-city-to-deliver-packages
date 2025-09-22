import unittest
from src.data.grid import Grid
from src.models.bfs import bfs
from src.models.ucs import ucs
from src.models.astar import astar

class SearchAlgoTests(unittest.TestCase):
    def setUp(self):
        # small grid with one obstacle in middle
        self.g = Grid(5, 5)
        self.g.add_obstacle(2, 2)

    def test_bfs_gives_path(self):
        path = bfs(self.g, (0, 0), (4, 4))
        # bfs should always give us *a* path if possible
        self.assertIsNotNone(path)

    def test_ucs_gives_path_and_cost(self):
        path, cost ,_= ucs(self.g, (0, 0), (4, 4))
        self.assertIsNotNone(path)
        self.assertGreaterEqual(cost, 0)  # cost can’t be negative

    def test_astar_is_reasonable(self):
        path, cost, _ = astar(self.g, (0, 0), (4, 4))
        # if astar is broken, this will crash
        self.assertTrue(isinstance(path, list))
        self.assertGreaterEqual(cost, 0)

if __name__ == "__main__":
    unittest.main()
