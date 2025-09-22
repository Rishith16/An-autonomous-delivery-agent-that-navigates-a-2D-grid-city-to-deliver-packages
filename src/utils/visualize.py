import matplotlib.pyplot as plt

def plot_grid(grid, path=None, start=None, goal=None, title=None, save=None):
    plt.figure(figsize=(6,6))
    for r in range(grid.rows):
        for c in range(grid.cols):
            if grid.is_obstacle(r, c):
                plt.plot(c, r, "ks")  # black square
    if path:
        xs = [p[1] for p in path]
        ys = [p[0] for p in path]
        plt.plot(xs, ys, "r-", linewidth=2)
    if start:
        plt.plot(start[1], start[0], "go", markersize=12, label="Start")
    if goal:
        plt.plot(goal[1], goal[0], "bo", markersize=12, label="Goal")
    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.title(title)
    
    if save:   #  single save mechanism
        plt.savefig(save)
    else:
        plt.show()
    
    plt.close()
def save_original_and_dynamic(grid, path, start, goal, block_cell, outdir="results"):
    # original plan
    plot_grid(grid, path, start, goal,
              save=f"{outdir}/original_plan.png",
              title="Original Plan (before dynamic obstacle)")

    # inject dynamic obstacle
    grid.set_obstacle(*block_cell)
    plot_grid(grid, None, start, goal,
              save=f"{outdir}/dynamic_map.png",
              title="Dynamic Map (after obstacle injected)")

