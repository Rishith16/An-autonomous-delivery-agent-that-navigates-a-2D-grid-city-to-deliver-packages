from src.data.grid import Grid

def load_map_from_file(path):
    with open(path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # first line: rows cols
    rows, cols = map(int, lines[0].split())
    grid = Grid(rows, cols)

    start, goal = None, None

    for r in range(1, rows+1):
        for c, ch in enumerate(lines[r].split()):
            if ch == "#":
                grid.add_obstacle(r-1, c)
            elif ch == "S":
                start = (r-1, c)
            elif ch == "G":
                goal = (r-1, c)
            elif ch.isdigit():
                grid.add_cost(r-1, c, int(ch))  # terrain cost if number

    return grid, start, goal
