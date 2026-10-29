"""
Pure graph measurements used to rate a maze.
This module must stay free of bpy so it can be unit-tested outside Blender.
"""

import math
import random
from collections import deque

SOLVER_RUNS = 5
COVERAGE_BUCKETS = 4


def clamp(value):
    return min(1.0, max(0.0, float(value)))


def linked_cells(grid):
    return [c for c in grid.all_cells if c.has_any_link()]


def is_reachable(start, goal):
    seen = {start}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell is goal:
            return True
        for neighbor in cell.links:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return False


def count_decision_points(path):
    count = 0
    for i, cell in enumerate(path[:-1]):
        forward = [n for n in cell.links if i == 0 or n is not path[i - 1]]
        if len(forward) >= 2:
            count += 1
    return count


def _branch_depth(first, blocked):
    seen = {first}
    frontier = [first]
    depth = 0
    while frontier:
        depth += 1
        next_frontier = []
        for cell in frontier:
            for neighbor in cell.links:
                if neighbor not in seen and neighbor not in blocked:
                    seen.add(neighbor)
                    next_frontier.append(neighbor)
        frontier = next_frontier
    return depth


def false_branch_depths(path):
    on_path = set(path)
    return [_branch_depth(n, on_path) for cell in path for n in cell.links if n not in on_path]


def _dfs_steps(start, goal, choose):
    """Moves made by a depth-first walker, counting backtracking moves."""
    visited = {start}
    stack = [start]
    steps = 0
    while stack:
        current = stack[-1]
        if current is goal:
            return steps
        candidates = [n for n in current.links if n not in visited]
        if candidates:
            chosen = choose(candidates)
            visited.add(chosen)
            stack.append(chosen)
        else:
            stack.pop()
        steps += 1
    return steps


def _rng(seed):
    return random.Random(0 if seed is None else seed)


def random_solver_steps(start, goal, seed):
    """Mean number of moves of a random depth-first solver over SOLVER_RUNS runs."""
    rng = _rng(seed)
    return sum(_dfs_steps(start, goal, rng.choice) for _ in range(SOLVER_RUNS)) / SOLVER_RUNS


def normalized_position(grid, cell):
    columns = grid.get_columns_this_row(cell.row)
    return (
        cell.column / max(1, columns - 1),
        cell.row / max(1, grid.rows - 1),
        float(cell.level),
    )


def greedy_solver_ratio(grid, start, goal, path_length, seed):
    rng = _rng(seed)
    target = normalized_position(grid, goal)

    def choose(candidates):
        return min(candidates, key=lambda n: (math.dist(normalized_position(grid, n), target), rng.random()))

    return _dfs_steps(start, goal, choose) / max(1, path_length - 1)


def turn_rate(path):
    if len(path) < 3:
        return 0.0
    turns = 0
    for a, b, c in zip(path, path[1:], path[2:]):
        incoming = a.get_neighbor_direction(b)
        outgoing = b.get_neighbor_direction(c)
        if incoming != -1 and outgoing != -1 and incoming != outgoing:
            turns += 1
    return turns / (len(path) - 2)


def _bucket(grid, cell):
    x, y, _ = normalized_position(grid, cell)
    last = COVERAGE_BUCKETS - 1
    return (min(last, int(x * COVERAGE_BUCKETS)), min(last, int(y * COVERAGE_BUCKETS)), cell.level)


def spatial_coverage(grid, cells, path):
    available = {_bucket(grid, c) for c in cells}
    if not available:
        return 0.0
    visited = {_bucket(grid, c) for c in path}
    return len(visited & available) / len(available)
