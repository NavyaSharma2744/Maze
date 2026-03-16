"""
Step-by-step visual versions of search algorithms.
Yields state at each step for animation.
"""

from collections import deque
import heapq
import random


class AlgorithmStep:
    def __init__(
        self,
        step_num,
        current_pos,
        frontier,
        explored,
        path_so_far,
        action,
        message,
        is_goal=False,
        f_scores=None,
    ):
        self.step_num = step_num
        self.current_pos = current_pos
        self.frontier = frontier
        self.explored = explored
        self.path_so_far = path_so_far
        self.action = action
        self.message = message
        self.is_goal = is_goal
        self.f_scores = f_scores


def reconstruct_path(came_from, current):
    path = []
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path


def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def nearest_exit_distance(pos, exits):
    return min(manhattan_distance(pos, e) for e in exits)


def weighted_choice(candidates, weights):
    total = sum(weights)
    if total <= 0:
        return random.choice(candidates)

    pick = random.uniform(0, total)
    running = 0.0
    for candidate, weight in zip(candidates, weights):
        running += weight
        if pick <= running:
            return candidate
    return candidates[-1]


def bfs_visual(maze):
    """BFS step-by-step. Uses QUEUE (FIFO)."""
    start = maze.start
    queue = deque([start])
    visited = {start}
    came_from = {start: None}
    explored = set()
    step = 0

    yield AlgorithmStep(
        step,
        start,
        list(queue),
        set(),
        [start],
        'start',
        f"START: Add {start} to queue"
    )

    while queue:
        step += 1
        current = queue.popleft()
        explored.add(current)
        path = reconstruct_path(came_from, current)

        yield AlgorithmStep(
            step,
            current,
            list(queue),
            explored.copy(),
            path,
            'pop',
            f"POP: {current} from FRONT"
        )

        if maze.is_exit(*current):
            yield AlgorithmStep(
                step,
                current,
                list(queue),
                explored.copy(),
                path,
                'goal',
                f"GOAL! Path: {len(path) - 1} steps",
                is_goal=True
            )
            return

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
                step += 1
                yield AlgorithmStep(
                    step,
                    current,
                    list(queue),
                    explored.copy(),
                    path,
                    'push',
                    f"PUSH: {neighbor} to BACK"
                )

    yield AlgorithmStep(
        step + 1,
        start,
        [],
        explored.copy(),
        [],
        'fail',
        "No path found"
    )


def dfs_visual(maze):
    """DFS step-by-step. Uses STACK (LIFO)."""
    start = maze.start
    stack = [start]
    visited = {start}
    came_from = {start: None}
    explored = set()
    step = 0

    yield AlgorithmStep(
        step,
        start,
        list(stack),
        set(),
        [start],
        'start',
        f"START: Add {start} to stack"
    )

    while stack:
        step += 1
        current = stack.pop()
        explored.add(current)
        path = reconstruct_path(came_from, current)

        yield AlgorithmStep(
            step,
            current,
            list(stack),
            explored.copy(),
            path,
            'pop',
            f"POP: {current} from TOP"
        )

        if maze.is_exit(*current):
            yield AlgorithmStep(
                step,
                current,
                list(stack),
                explored.copy(),
                path,
                'goal',
                f"GOAL! Path: {len(path) - 1} steps",
                is_goal=True
            )
            return

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)
                step += 1
                yield AlgorithmStep(
                    step,
                    current,
                    list(stack),
                    explored.copy(),
                    path,
                    'push',
                    f"PUSH: {neighbor} to TOP"
                )

    yield AlgorithmStep(
        step + 1,
        start,
        [],
        explored.copy(),
        [],
        'fail',
        "No path found"
    )


def astar_visual(maze):
    """A* step-by-step. Uses PRIORITY QUEUE by f=g+h."""
    start = maze.start

    def h(pos):
        return min(manhattan_distance(pos, e) for e in maze.exits)

    g_score = {start: 0}
    f_score = {start: h(start)}
    counter = 0
    open_set = [(f_score[start], counter, start)]
    open_set_hash = {start}
    came_from = {start: None}
    explored = set()
    step = 0

    def get_frontier():
        return [item[2] for item in sorted(open_set)]

    yield AlgorithmStep(
        step,
        start,
        get_frontier(),
        set(),
        [start],
        'start',
        f"START: Add {start} with f={f_score[start]}"
    )

    while open_set:
        step += 1
        f, _, current = heapq.heappop(open_set)
        open_set_hash.discard(current)
        explored.add(current)
        path = reconstruct_path(came_from, current)
        g = g_score[current]

        yield AlgorithmStep(
            step,
            current,
            get_frontier(),
            explored.copy(),
            path,
            'pop',
            f"POP: {current} with f={f} (g={g}, h={f-g})"
        )

        if maze.is_exit(*current):
            yield AlgorithmStep(
                step,
                current,
                get_frontier(),
                explored.copy(),
                path,
                'goal',
                f"GOAL! Path: {len(path) - 1} steps",
                is_goal=True
            )
            return

        for neighbor in maze.get_neighbors(*current):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                new_f = tentative_g + h(neighbor)
                f_score[neighbor] = new_f

                if neighbor not in open_set_hash:
                    counter += 1
                    heapq.heappush(open_set, (new_f, counter, neighbor))
                    open_set_hash.add(neighbor)
                    step += 1
                    yield AlgorithmStep(
                        step,
                        current,
                        get_frontier(),
                        explored.copy(),
                        path,
                        'push',
                        f"PUSH: {neighbor} with f={new_f}"
                    )

    yield AlgorithmStep(
        step + 1,
        start,
        [],
        explored.copy(),
        [],
        'fail',
        "No path found"
    )


def aco_visual(
    maze,
    num_ants=8,
    num_iterations=12,
    alpha=1.0,
    beta=3.0,
    evaporation_rate=0.25,
    q=100.0,
    max_steps_multiplier=4,
):
    """
    ACO step-by-step visualization.

    This visual version shows:
    - iteration progress
    - each ant's movement
    - pheromone-guided probabilistic choices
    - best path found so far
    """
    start = maze.start
    exits = list(maze.exits)
    step = 0

    if maze.is_exit(*start):
        yield AlgorithmStep(
            step,
            start,
            [],
            {start},
            [start],
            'goal',
            "START is already an exit!",
            is_goal=True
        )
        return

    pheromone = {}
    all_cells = []

    for r in range(maze.rows):
        for c in range(maze.cols):
            pos = (r, c)
            if hasattr(maze, "is_wall") and maze.is_wall(r, c):
                continue
            all_cells.append(pos)

    for cell in all_cells:
        try:
            neighbors = maze.get_neighbors(*cell)
        except TypeError:
            neighbors = maze.get_neighbors(cell)

        for nbr in neighbors:
            pheromone[(cell, nbr)] = 1.0

    max_steps = max(maze.rows * maze.cols * max_steps_multiplier, 20)
    global_explored = set()
    best_path = None
    best_len = float("inf")

    yield AlgorithmStep(
        step,
        start,
        [],
        set(),
        [start],
        'start',
        f"START ACO: {num_ants} ants, {num_iterations} iterations"
    )

    for iteration in range(1, num_iterations + 1):
        iteration_successes = []

        step += 1
        yield AlgorithmStep(
            step,
            start,
            [],
            global_explored.copy(),
            best_path[:] if best_path else [start],
            'iteration',
            f"ITERATION {iteration}: Launching {num_ants} ants"
        )

        for ant_idx in range(1, num_ants + 1):
            current = start
            ant_path = [current]
            ant_visited = {current}
            ant_explored = {current}

            step += 1
            yield AlgorithmStep(
                step,
                current,
                [],
                global_explored.union(ant_explored),
                ant_path[:],
                'ant_start',
                f"ANT {ant_idx}: Starting at {start}"
            )

            success = False

            for move_num in range(1, max_steps + 1):
                if maze.is_exit(*current):
                    success = True
                    break

                try:
                    neighbors = maze.get_neighbors(*current)
                except TypeError:
                    neighbors = maze.get_neighbors(current)

                if not neighbors:
                    step += 1
                    yield AlgorithmStep(
                        step,
                        current,
                        [],
                        global_explored.union(ant_explored),
                        ant_path[:],
                        'dead_end',
                        f"ANT {ant_idx}: Dead end at {current}"
                    )
                    break

                candidates = [n for n in neighbors if n not in ant_visited]
                if not candidates:
                    candidates = list(neighbors)

                weights = []
                for nxt in candidates:
                    tau = pheromone.get((current, nxt), 1.0)
                    dist = nearest_exit_distance(nxt, exits)
                    eta = 1.0 / (dist + 1)
                    score = (tau ** alpha) * (eta ** beta)
                    weights.append(score)

                next_cell = weighted_choice(candidates, weights)

                ant_path.append(next_cell)
                ant_visited.add(next_cell)
                ant_explored.add(next_cell)
                global_explored.add(next_cell)

                step += 1
                yield AlgorithmStep(
                    step,
                    next_cell,
                    list(candidates),
                    global_explored.copy(),
                    ant_path[:],
                    'move',
                    f"ANT {ant_idx}: Move {move_num} -> {next_cell}"
                )

                current = next_cell

                if maze.is_exit(*current):
                    success = True
                    break

            if success:
                path_len = len(ant_path) - 1
                iteration_successes.append((ant_path[:], path_len))

                if path_len < best_len:
                    best_len = path_len
                    best_path = ant_path[:]

                step += 1
                yield AlgorithmStep(
                    step,
                    current,
                    [],
                    global_explored.copy(),
                    ant_path[:],
                    'ant_goal',
                    f"ANT {ant_idx}: Reached exit! Path length = {path_len}"
                )
            else:
                step += 1
                yield AlgorithmStep(
                    step,
                    current,
                    [],
                    global_explored.copy(),
                    ant_path[:],
                    'ant_fail',
                    f"ANT {ant_idx}: Did not reach an exit"
                )

        for edge in list(pheromone.keys()):
            pheromone[edge] *= (1.0 - evaporation_rate)
            if pheromone[edge] < 0.01:
                pheromone[edge] = 0.01

        for ant_path, length in iteration_successes:
            deposit = q / max(1, length)
            for i in range(len(ant_path) - 1):
                a = ant_path[i]
                b = ant_path[i + 1]
                pheromone[(a, b)] = pheromone.get((a, b), 1.0) + deposit
                pheromone[(b, a)] = pheromone.get((b, a), 1.0) + deposit

        step += 1
        if best_path:
            yield AlgorithmStep(
                step,
                best_path[-1],
                [],
                global_explored.copy(),
                best_path[:],
                'iteration_done',
                f"ITERATION {iteration} DONE: Best path so far = {best_len}"
            )
        else:
            yield AlgorithmStep(
                step,
                start,
                [],
                global_explored.copy(),
                [start],
                'iteration_done',
                f"ITERATION {iteration} DONE: No successful path yet"
            )

    if best_path:
        step += 1
        yield AlgorithmStep(
            step,
            best_path[-1],
            [],
            global_explored.copy(),
            best_path[:],
            'goal',
            f"ACO GOAL! Best path found = {best_len} steps",
            is_goal=True
        )
        return

    yield AlgorithmStep(
        step + 1,
        start,
        [],
        global_explored.copy(),
        [],
        'fail',
        "ACO failed to find a path"
    )


if __name__ == "__main__":
    from maze import Maze

    maze = Maze()

    print("BFS Visual Test:")
    for s in bfs_visual(maze):
        print(f"  Step {s.step_num}: {s.message}")
        if s.is_goal:
            break

    print("\nACO Visual Test:")
    for s in aco_visual(maze):
        print(f"  Step {s.step_num}: {s.message}")
        if s.is_goal or s.action == 'fail':
            break
