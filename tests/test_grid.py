import unittest
from src.data.grid import Grid

class GridTests(unittest.TestCase):
    def test_put_obstacle(self):
        g = Grid(3, 3)
        g.add_obstacle(1, 1)
        # just checking if it actually stored
        self.assertTrue((1, 1) in g.obstacles)

    def test_cost_is_one_by_default(self):
        g = Grid(3, 3)
        # every cell should cost 1 unless we change it
        self.assertEqual(g.get_cost(0, 0), 1)

    def test_if_custom_cost_works(self):
        g = Grid(3, 3)
        g.add_cost(0, 0, 5)
        # if this fails, cost system is broken
        self.assertEqual(g.get_cost(0, 0), 5)

if __name__ == "__main__":
    unittest.main()
