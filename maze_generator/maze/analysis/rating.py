"""
Difficulty and fun rating of a generated maze.
This module must stay free of bpy so it can be unit-tested outside Blender.
"""

import math
from dataclasses import dataclass, field

from maze_generator.maze.analysis import metrics

DIFFICULTY_WEIGHTS = {
    "Decision density": 0.25,
    "False branch depth": 0.25,
    "Solver effort": 0.40,
    "Path share": 0.10,
}
FUN_WEIGHTS = {
    "Difficulty sweet spot": 0.25,
    "Choice quality": 0.25,
    "Path rhythm": 0.20,
    "Spatial coverage": 0.15,
    "No directional shortcut": 0.15,
}
DIFFICULTY_LEVELS = ((25, "Easy"), (50, "Medium"), (75, "Hard"))
SWEET_SPOT = 55
DECISION_DENSITY_FULL = 0.6
# Absolute log scales so bigger mazes rate harder.
# False branch depth: depth 1 -> 0, depth 2**BRANCH_DEPTH_DOUBLINGS (32) -> 1.
BRANCH_DEPTH_DOUBLINGS = 5
# Solver effort: 10 moves -> 0, 10 000 moves -> 1.
EFFORT_MIN_MOVES = 10
EFFORT_DECADES = 3
# A maze "has choices" when a random solver wastes at least this share of the shortest path.
MIN_RANDOM_WASTE = 0.5
# Directional bias: greedy solver wastes less than this share of what the random solver wastes.
BIAS_WASTE_SHARE = 0.25
BIAS_MIN_PATH = 10


@dataclass
class MazeRating:
    ratable: bool
    reason: str = ""
    difficulty: int = 0
    difficulty_level: str = ""
    difficulty_parts: dict = field(default_factory=dict)
    fun: int = 0
    fun_parts: dict = field(default_factory=dict)
    has_directional_bias: bool = False


def _weighted_total(parts, weights):
    return round(100 * sum(parts[name] * weight for name, weight in weights.items()))


def _difficulty_level(score):
    for limit, name in DIFFICULTY_LEVELS:
        if score < limit:
            return name
    return "Extreme"


def rate_maze(grid, seed=0):
    try:
        return _rate(grid, seed)
    except Exception:  # Rating must never break maze generation.
        return MazeRating(ratable=False, reason="internal error")


def _rate(grid, seed):
    cells = metrics.linked_cells(grid)
    cell_count = len(cells)
    if cell_count < 2:
        return MazeRating(ratable=False, reason="maze too small")
    path = list(grid.longest_path or [])
    if len(path) < 2 or any(c is None for c in path):
        return MazeRating(ratable=False, reason="no solution path")
    start, goal = path[0], path[-1]
    if not metrics.is_reachable(start, goal):
        return MazeRating(ratable=False, reason="goal unreachable")

    length = len(path)
    shortest_moves = max(1, length - 1)
    sqrt_n = math.sqrt(cell_count)
    depths = metrics.false_branch_depths(path)
    mean_depth = sum(depths) / len(depths) if depths else 0.0
    random_steps = metrics.random_solver_steps(start, goal, seed)
    random_waste = random_steps / shortest_moves - 1
    greedy_waste = metrics.greedy_solver_ratio(grid, start, goal, length, seed) - 1

    difficulty_parts = {
        "Decision density": metrics.clamp((metrics.count_decision_points(path) / length) / DECISION_DENSITY_FULL),
        "False branch depth": metrics.clamp(math.log2(mean_depth) / BRANCH_DEPTH_DOUBLINGS) if depths else 0.0,
        "Solver effort": metrics.clamp(math.log10(max(1.0, random_steps) / EFFORT_MIN_MOVES) / EFFORT_DECADES),
        "Path share": metrics.clamp((length / cell_count) / 0.5),
    }
    difficulty = _weighted_total(difficulty_parts, DIFFICULTY_WEIGHTS)

    max_good_depth = max(6.0, 2 * sqrt_n)
    good_branches = sum(1 for d in depths if 3 <= d <= max_good_depth)
    no_shortcut = metrics.clamp(greedy_waste / random_waste) if random_waste >= 0.05 else 1.0
    fun_parts = {
        "Difficulty sweet spot": 1 - metrics.clamp(abs(difficulty - SWEET_SPOT) / 45),
        "Choice quality": good_branches / len(depths) if depths else 0.0,
        "Path rhythm": 1 - metrics.clamp(abs(metrics.turn_rate(path) - 0.5) / 0.5),
        "Spatial coverage": metrics.spatial_coverage(grid, cells, path),
        "No directional shortcut": no_shortcut,
    }

    has_bias = (
        length >= BIAS_MIN_PATH
        and random_waste >= MIN_RANDOM_WASTE
        and greedy_waste < BIAS_WASTE_SHARE * random_waste
    )
    return MazeRating(
        ratable=True,
        difficulty=difficulty,
        difficulty_level=_difficulty_level(difficulty),
        difficulty_parts=difficulty_parts,
        fun=_weighted_total(fun_parts, FUN_WEIGHTS),
        fun_parts=fun_parts,
        has_directional_bias=has_bias,
    )
