from collections import deque

def bfs(grid, start, goal, fuel_limit=None, time_limit=None):
    q = deque([start])
    came_from = {start: None}
    cost_so_far = {start: 0}
    nodes_expanded = 0

    while q:
        current = q.popleft()
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

            if nbr not in came_from:
                came_from[nbr] = current
                cost_so_far[nbr] = new_cost
                q.append(nbr)

    if goal not in came_from:
        return [], float("inf"), nodes_expanded

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()

    return path, cost_so_far[goal], nodes_expanded

