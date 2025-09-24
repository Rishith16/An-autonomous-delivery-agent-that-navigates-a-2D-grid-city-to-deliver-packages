# An Autonomous Delivery Agent – path planning in a 2D grid city

##  Overview
This project simulates an **autonomous delivery agent** navigating a 2D grid-based city.  
The city contains:
- **Free cells** → agent can move freely
- **Static obstacles** → permanent blocks (e.g., buildings, walls)
- **Varying terrain costs** → higher costs for busy or rough roads
- **Dynamic obstacles** → moving objects (cars, crowds) that appear/disappear

The agent moves in **four directions (up, down, left, right)**.  
We compare path planning algorithms:
- **BFS**
- **UCS**
- **A***
- **Replanner** (for dynamic cases)

### MAPS

Map files are plain text. The first line contains six integers:

rows cols start_x start_y goal_x goal_y
- Subsequent lines are a grid where:

S and G mark start/goal cells and count as cost 1
- Marks blocked cells (impassable)

Example:

5 5 0 0 4 4
```S....
.....
..#..
....#
....G
```
A demo dynamic obstacle schedule is encoded in maps/schedule:

```[
    {"id": 1, "trajectory": [[2,2], [2,3], [2,4], [2,5], [2,6]], "start": 2, "loop": true},
]
```
##Project Structure
```
AIML PROJECT/
│
├── maps/                           # Input grid maps (small.txt, medium.txt, large.txt, dynamic.txt)
├── outputs/                        # Logs, plots, and results generated from experiments
├── schedule/                       # Scheduling files (e.g., schedule.json)
│
├── src/                            # Core source code
│ ├── data/                         # Environment data handling
│ │ ├── grid.py
│ │ └── dynamic_obstacles.py        # for adding dynamic obstacles in the maps
│ │
│ ├── experiments/                  # Scripts for experiments & result plotting
│ │ ├── dynamics.py
│ │ ├── plot_results.py
│ │ └── run_experiment.py            # act as main function too and it has CLI
│ │
│ ├── models/                        # Path planning algorithms
│ │ ├── bfs.py
│ │ ├── ucs.py
│ │ ├── astar.py
│ │ └── replanner.py
│ │
│ ├── preprocessing/   
| | └──map_loader.py                 # Preprocessing utilities
│ └── utils/                         # Helper functions
│    ├──metrics.py
|    └── visualize.py
├── tests/                           # Unit tests
|    ├──test_grid.py
|    ├──test_sample.py
|    └──test_search.py
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore file
└── README.md                        # This file
```

---

##  Quick Start

### Prerequisites
- Python 3.x  
- Install dependencies:
  pip install -r requirements.txt

## Run Experiments(CLI)
-After installing dependencies and setting up the repo, you can run experiments using:
```python -m src.experiments.run_experiment --map <map_file> --algo a<algorithm>[options]```

-Arguments
```
--map (required) → Path to the map file (e.g., maps/small.txt)
--algo (required) → Algorithm to use: bfs, ucs, astar, or replanner(hill climb)
--out → Output directory (default: outputs/)
--seed → Random seed (default: 0)
--fuel → Fuel limit for the agent (optional)
--time_limit → Max runtime in seconds (optional)
--dynamic → Enable moving obstacles (default: off)
--schedule → JSON file describing obstacle movement (only used with --dynamic)
```
-Examples

1. Static environment (simple map + A search):*
```python -m src.experiments.run_experiment --map maps/small.txt --algo astar```
2. Uniform Cost Search with fuel limit:
```python -m src.experiments.run_experiment --map maps/medium.txt --algo ucs --fuel 50```
3. Dynamic environment with schedule:
```python -m src.experiments.run_experiment --map maps/dynamic.txt --algo replanner --dynamic --schedule schedules/move.json```

-All results,logs, and outputs will be saved in the outputs/folder by default.

##Results & Outputs
 - After running an experiment, all results, logs, and plots are saved in the outputs/ directory.
 -   You may find:
 -   Path visualizations (matplotlib plots of explored paths).
 -   Summary stats (travel cost, time taken, success rate).
 -   Dynamic maps (showing moving obstacles over time).
 - Example:
      ``` outputs/
         ├── run_2025-09-22_10-00-01/
         │   ├── path.png
         │   ├── stats.csv
         │   └── log.txt
      ```
 

## Contributing
  This is a student project, so contributions are welcome!
     Fork the repo
     Create a new branch
     Submit a pull request with clear descriptions
## Report and Demo
- The project report (REPORT.pdf) covering environment modeling, agent design, heuristics, experimental results, analysis, and conclusion is available in the repository root.

- The demo (DEMO:SCREENSHOTS.pdf) includes screenshots and an illustrative walkthrough of the agent acting in a dynamic map.
