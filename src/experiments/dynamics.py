import time
from pathlib import Path
from  utils.visualize import plot_grid
from  data.dynamic_obstacles import DynamicObstacles
from  models.replanner import Replanner
from  data.grid import Grid

def run_dynamic(mapfile, algo="replanner", outdir="outputs", seed=0, fuel=100, time_limit=1000):
    # Load base grid
    grid = Grid.load_from_file(mapfile)
    replanner = Replanner(grid)

    # Example: dynamic obstacle schedule
    schedules = [
        {"id": 1, "trajectory": [(5,5), (5,6), (5,7), (5,8)], "start": 2},
        {"id": 2, "trajectory": [(8,8), (9,8), (10,8)], "start": 5}
    ]
    dyn = DynamicObstacles.load_from_list(schedules)

    start, goal = (0,0), (grid.rows-1, grid.cols-1)
    path, cost, nodes, runtime = replanner.plan_path(start, goal, algo, fuel, time_limit)

    t = 0
    while path and path[-1] != goal:
        occ = dyn.occupied_at(t)
        for pos in occ:
            grid.set_obstacle(*pos)

        path, cost, nodes, rt = replanner.replan_if_needed(path, start, goal,
                                                           algo=algo, fuel_limit=fuel, time_limit=time_limit)
        t += 1

        if not path:
            break

    # Logging
    row = {
        "map": Path(mapfile).name,
        "algo": algo,
        "rows": grid.rows,
        "cols": grid.cols,
        "start": start,
        "goal": goal,
        "cost": cost,
        "length": len(path) if path else 0,
        "nodes": nodes,
        "time_s": runtime,
        "seed": seed,
        "notes": "dynamic"
    }

    # Save visualization
    plot_grid(grid, path, start=start, goal=goal,
              title=f"{algo} dynamic run", save=f"{outdir}/dynamic_{algo}.png")

    return row
