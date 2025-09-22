import time
from .astar import astar
from .ucs import ucs
from .bfs import bfs

class Replanner:
    def __init__(self, grid):
        self.grid = grid

    def plan_path(self, start, goal, algo="astar", fuel_limit=None, time_limit=None):
        
        t0 = time.perf_counter()

        if algo == "astar":
            path, cost,_ = astar(self.grid, start, goal,
                               fuel_limit=fuel_limit, time_limit=time_limit)
        elif algo == "ucs":
            path, cost,_ = ucs(self.grid, start, goal)
        elif algo == "bfs":
            path, cost,_ = bfs(self.grid, start, goal)
        elif algo == "hill":
            path, cost, nodes, runtime = self.hill_climb(start, goal,
                                                         fuel_limit=fuel_limit,
                                                         time_limit=time_limit)
            return path, cost, nodes, runtime
        else:
            raise ValueError(f"Unknown algorithm: {algo}")

        t1 = time.perf_counter()
        runtime = t1 - t0
        nodes = len(path) if path else 0
        return path, cost, nodes, runtime

    def replan_if_needed(self, current_path, start, goal,
                         algo="astar", fuel_limit=None, time_limit=None):
        """
        If path blocked due to new obstacles, replan.
        """
        if not current_path:
            return self.plan_path(start, goal, algo, fuel_limit, time_limit)

        for (x, y) in current_path:
            if self.grid.is_obstacle(x, y):
                return self.plan_path(start, goal, algo, fuel_limit, time_limit)

        return current_path, None, len(current_path), 0.0

    # ---------------- local search ----------------
    def heuristic(self, state, goal):
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])

    def hill_climb(self, start, goal, max_steps=100, restarts=5,
                   fuel_limit=None, time_limit=None):
        """
        Hill climbing with random restarts.
        Stops if fuel/time exceeded.
        """
        import random
        best_path = None
        best_score = float("inf")
        nodes_expanded = 0

        t0 = time.perf_counter()
        for attempt in range(restarts):
            current = start
            path = [current]
            steps = 0

            while current != goal and steps < max_steps:
                if fuel_limit and steps > fuel_limit:
                    break
                if time_limit and (time.perf_counter() - t0) > time_limit:
                    break

                neighbors = self.grid.neighbors(*current)
                if not neighbors:
                    break

                next_state = min(neighbors,
                                 key=lambda n: self.heuristic(n, goal))
                steps += 1
                nodes_expanded += 1
                path.append(next_state)
                current = next_state

            score = self.heuristic(current, goal)
            if current == goal and score < best_score:
                best_path, best_score = path, score

        runtime = time.perf_counter() - t0
        cost = len(best_path) if best_path else float("inf")
        return best_path, cost, nodes_expanded, runtime
