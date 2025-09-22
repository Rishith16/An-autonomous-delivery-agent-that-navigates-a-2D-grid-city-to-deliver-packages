import argparse
import random
import time
from pathlib import Path
import json

from src.preprocessing.map_loader import load_map_from_file
from src.models.bfs import bfs
from src.models.ucs import ucs
from src.models.astar import astar
from src.models.replanner import Replanner
from src.utils.metrics import CSVLogger
from src.utils.visualize import plot_grid
from src.data.dynamic_obstacles import MovingObstacleManager

def _add_obstacle_to_grid(grid, pos):
    r, c = pos
    if hasattr(grid, "add_obstacle"):
        grid.add_obstacle(r, c)
    elif hasattr(grid, "set_obstacle"):
        grid.set_obstacle(r, c)
    elif hasattr(grid, "obstacles"):
        grid.obstacles.add((r, c))
    else:
        raise AttributeError("Grid has no method to add obstacle")

def _remove_obstacle_from_grid(grid, pos):
    r, c = pos
    if hasattr(grid, "remove_obstacle"):
        grid.remove_obstacle(r, c)
    elif hasattr(grid, "clear_obstacle"):
        grid.clear_obstacle(r, c)
    elif hasattr(grid, "obstacles"):
        grid.obstacles.discard((r, c))
    else:
        return

ALGS = {"bfs": bfs, "ucs": ucs, "astar": astar, "replanner": None}

def normalize_result(res, grid):
    """
    Return (path:list[(r,c)], cost:float, nodes:int)
    Accepts many shapes:
      - path list
      - (path,)
      - (path, cost)
      - (path, cost, nodes)
      - (path, cost, nodes, runtime)
      - empty or None
    """
    if res is None:
        return [], float("inf"), 0

    if isinstance(res, (tuple, list)):
  
        if len(res) >= 3 and isinstance(res[0], list):
            path = res[0] or []
            cost = res[1]
            nodes = res[2]
            return (path, cost, nodes)
        if len(res) == 2:
            path, cost = res
            if isinstance(path, list):
                nodes = len(path)
                return (path, cost, nodes)
        if len(res) == 1 and isinstance(res[0], list):
            path = res[0]
            cost = sum(grid.get_cost(*p) for p in path) if path else float("inf")
            nodes = len(path)
            return (path, cost, nodes)
        if all(isinstance(x, tuple) and len(x) == 2 for x in res):
            path = res
            cost = sum(grid.get_cost(*p) for p in path) if path else float("inf")
            nodes = len(path)
            return (path, cost, nodes)
    return [], float("inf"), 0

def safe_plot(grid, path, start, goal, title, save):
    if not path:
        plot_grid(grid, path=None, start=start, goal=goal, title=title, save=save)
        return
    if not (isinstance(path, list) and all(isinstance(p, tuple) and len(p) == 2 for p in path)):
        if isinstance(path, tuple) or isinstance(path, list):
            first = path[0] if path else None
            if isinstance(first, list):
                path = first
            else:
                path = []
        else:
            path = []
    plot_grid(grid, path=path, start=start, goal=goal, title=title, save=save)
def _add_obstacle_to_grid(grid, pos):
    r, c = pos
    grid.add_obstacle(r, c)

def _remove_obstacle_from_grid(grid, pos):
    r, c = pos
    grid.remove_obstacle(r, c)
def run_single(mapfile, algo, outdir="outputs", seed=0, fuel=None, time_limit=None):
    random.seed(seed)
    grid, start, goal = load_map_from_file(mapfile)
    rows, cols = grid.rows, grid.cols
    Path(outdir).mkdir(parents=True, exist_ok=True)

    if algo in ("bfs", "ucs", "astar"):
        fn = ALGS.get(algo)
        t0 = time.perf_counter()
        res = fn(grid, start, goal, fuel_limit=fuel, time_limit=time_limit)
        t1 = time.perf_counter()
        time_s = t1 - t0
        path, cost, nodes = normalize_result(res, grid)

    elif algo == "replanner":
        repl = Replanner(grid)
        res, time_s = None, None
        res, time_s = ((repl.plan_path(start, goal, fuel_limit=fuel, time_limit=time_limit)), 0.0)
        if isinstance(res, tuple) and len(res) == 4:
            path, cost, nodes, runtime = res
            time_s = runtime
        else:
            path, cost, nodes = normalize_result(res, grid)
            time_s = 0.0
    else:
        raise ValueError("unknown algo " + str(algo))

    if not (isinstance(path, list) and all(isinstance(p, tuple) and len(p) == 2 for p in path)):
        path = []

    if cost == float("inf") and path:
        cost = sum(grid.get_cost(*p) for p in path)

    failed = False
    fail_reason = ""
    if not path or cost == float("inf"):
        failed = True
        if time_limit is not None and nodes >= time_limit:
            fail_reason = "FAIL_TIME"
        elif fuel is not None:
            fail_reason = "FAIL_FUEL"
        else:
            fail_reason = "FAIL"

    vizfile = f"{outdir}/{Path(mapfile).stem}_{algo}.png"
    safe_plot(grid, path, start, goal, title=f"{algo} {Path(mapfile).stem}", save=vizfile)

    logger = CSVLogger(f"{outdir}/results.csv")
    logger.log({
        "map": Path(mapfile).name,
        "algo": algo,
        "rows": rows,
        "cols": cols,
        "start": start,
        "goal": goal,
        "cost": cost if not failed else fail_reason,
        "length": len(path) if path else 0,
        "nodes": nodes,
        "time_s": time_s,
        "seed": seed,
        "notes": ""
    })
    logger.close()

    print("done", mapfile, algo, "time", time_s, "nodes", nodes, "cost", cost, ("FAILED" if failed else ""))
from src.data.dynamic_obstacles import DynamicObstacles


def run_dynamic(mapfile, algo, outdir="outputs", seed=0, fuel=None, time_limit=None, schedule_file=None, max_steps=1000):
    """
    Simulate moving obstacles and let Replanner react.
    schedule_file (optional): json file with list of obstacle dicts (trajectory,start,loop,id)
    """
    random.seed(seed)
    grid, start, goal = load_map_from_file(mapfile)
    rows, cols = grid.rows, grid.cols
    Path(outdir).mkdir(parents=True, exist_ok=True)

    if schedule_file:
        with open(schedule_file, "r") as f:
            schedule_list = json.load(f)
    else:
        schedule_list = [
            {"id": 1, "trajectory": [(2,2), (2,3), (2,4), (2,5)], "start": 2, "loop": True},
            {"id": 2, "trajectory": [(5,7), (5,6), (5,5)], "start": 4, "loop": True}
        ]

    mover = MovingObstacleManager.load_from_list(schedule_list)
    repl = Replanner(grid)


    path, cost, nodes, runtime = repl.plan_path(start, goal, algo="astar", fuel_limit=fuel, time_limit=time_limit)
    total_nodes = nodes if nodes else 0
    total_time = runtime if runtime else 0.0


    viz_original = f"{outdir}/{Path(mapfile).stem}_{algo}_original.png"
    safe_plot(grid, path, start, goal, title=f"original {algo} {Path(mapfile).stem}", save=viz_original)

    prev_occ = set()
    agent_pos = start
    executed_path = [agent_pos]
    timestep = 0


    while agent_pos != goal and timestep < max_steps:

        new_occ = mover.occupied_at(timestep)

        for p in (prev_occ - new_occ):
            _remove_obstacle_from_grid(grid, p)


        for p in (new_occ - prev_occ):
            _add_obstacle_to_grid(grid, p)

        prev_occ = new_occ


        if agent_pos in new_occ:
            print("Collision: moving obstacle occupied agent position", agent_pos)
            cost = float("inf")
            nodes = total_nodes
            total_time += 0
            break



        path_res = repl.replan_if_needed(path, agent_pos, goal, algo="astar", fuel_limit=fuel, time_limit=time_limit)

        if isinstance(path_res, tuple) and len(path_res) >= 3:
            new_path = path_res[0]

            if len(path_res) == 4:
                _, new_cost, new_nodes, new_runtime = path_res
                total_nodes += (new_nodes or 0)
                total_time += (new_runtime or 0.0)
            else:

                new_path, new_cost, new_nodes = normalize_result(path_res, grid)
                total_nodes += new_nodes
            path = new_path

        if not path or len(path) < 2:

            print("No available next step (path too short or missing). Stopping.")
            cost = float("inf")
            nodes = total_nodes
            break

        next_pos = path[1]

        if next_pos in new_occ:

            path_res2 = repl.replan_if_needed(path, agent_pos, goal, algo="astar", fuel_limit=fuel, time_limit=time_limit)
            path, cost_tmp, nodes_tmp = normalize_result(path_res2, grid)
            total_nodes += (nodes_tmp or 0)
            if not path or len(path) < 2:
                print("Blocked next cell after replan. Stopping.")
                cost = float("inf")
                nodes = total_nodes
                break
            next_pos = path[1]

       
        agent_pos = next_pos
        executed_path.append(agent_pos)

        if agent_pos in path:
            idx = path.index(agent_pos)
            path = path[idx:] 
        else:
            
            path = []

        timestep += 1

    
    if agent_pos == goal:
        final_cost = sum(grid.get_cost(*p) for p in executed_path)
    else:
        final_cost = float("inf")

    logger = CSVLogger(f"{outdir}/results.csv")
    logger.log({
        "map": Path(mapfile).name,
        "algo": algo,
        "rows": rows,
        "cols": cols,
        "start": start,
        "goal": goal,
        "cost": final_cost if final_cost != float("inf") else "FAIL",
        "length": len(executed_path) if executed_path else 0,
        "nodes": total_nodes,
        "time_s": total_time,
        "seed": seed,
        "notes": "dynamic"
    })
    logger.close()

    
    vizfile = f"{outdir}/{Path(mapfile).stem}_{algo}_dynamic.png"
    safe_plot(grid, executed_path if executed_path else None, start, goal,
              title=f"{algo} dynamic {Path(mapfile).stem}", save=vizfile)

    print("done dynamic:", mapfile, algo, "steps:", len(executed_path), "nodes:", total_nodes, "cost:", final_cost)
    return



def main():
    p = argparse.ArgumentParser()
    p.add_argument("--map", required=True)
    p.add_argument("--algo", required=True, choices=["bfs", "ucs", "astar", "replanner"])
    p.add_argument("--out", default="outputs")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--fuel", type=int, default=None)
    p.add_argument("--time_limit", type=int, default=None)
    p.add_argument("--dynamic", action="store_true", help="simulate moving obstacles")
    p.add_argument("--schedule", type=str, default=None, help="JSON schedule file for moving obstacles")
    args = p.parse_args()

    if args.dynamic:
        run_dynamic(args.map, args.algo, outdir=args.out, seed=args.seed,
                    fuel=args.fuel, time_limit=args.time_limit, schedule_file=args.schedule)
    else:
        run_single(args.map, args.algo, outdir=args.out, seed=args.seed, fuel=args.fuel, time_limit=args.time_limit)




if __name__ == "__main__":
    main()
