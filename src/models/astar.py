import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal, fuel_limit=None, time_limit=None):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    nodes_expanded = 0
    import time
    t0 = time.perf_counter()

    while frontier:
        _, current = heapq.heappop(frontier)
        nodes_expanded += 1

        if time_limit is not None and nodes_expanded > time_limit:
            return [], float("inf"), nodes_expanded

        if current == goal:
            break

        for nbr in grid.neighbors(*current):
            step_cost = grid.get_cost(*nbr)
            new_cost = cost_so_far[current] + step_cost

            if fuel_limit is not None and new_cost > fuel_limit:
                continue

            if nbr not in cost_so_far or new_cost < cost_so_far[nbr]:
                cost_so_far[nbr] = new_cost
                priority = new_cost + heuristic(nbr, goal)
                heapq.heappush(frontier, (priority, nbr))
                came_from[nbr] = current

    if goal not in came_from:
        return [], float("inf"), nodes_expanded

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()

    return path, cost_so_far[goal], nodes_expanded
