import unittest

import maze_fakes
from maze_fakes import FakeGrid, corridor, corridor_with_branch, u_maze
from maze_generator.maze.analysis import metrics


class ClampTest(unittest.TestCase):
    def test_clamp_bounds(self):
        self.assertEqual(metrics.clamp(-1), 0.0)
        self.assertEqual(metrics.clamp(0.4), 0.4)
        self.assertEqual(metrics.clamp(3), 1.0)


class ReachabilityTest(unittest.TestCase):
    def test_linked_cells_ignores_unlinked(self):
        grid = corridor(3)
        grid.cell(9, 9)
        self.assertEqual(len(metrics.linked_cells(grid)), 3)

    def test_is_reachable(self):
        grid = FakeGrid(4, 1)
        grid.link((0, 0), (1, 0))
        grid.link((2, 0), (3, 0))
        self.assertTrue(metrics.is_reachable(grid.cell(0, 0), grid.cell(1, 0)))
        self.assertFalse(metrics.is_reachable(grid.cell(0, 0), grid.cell(3, 0)))


class StructureTest(unittest.TestCase):
    def test_corridor_has_no_decisions_or_branches(self):
        path = corridor(10).longest_path
        self.assertEqual(metrics.count_decision_points(path), 0)
        self.assertEqual(metrics.false_branch_depths(path), [])

    def test_branch_creates_one_decision_and_depth(self):
        path = corridor_with_branch(10, 2, 5).longest_path
        self.assertEqual(metrics.count_decision_points(path), 1)
        self.assertEqual(metrics.false_branch_depths(path), [5])

    def test_turn_rate(self):
        self.assertEqual(metrics.turn_rate(corridor(10).longest_path), 0.0)
        # U maze: 15 cells, turns at (0,5) and (4,5).
        self.assertAlmostEqual(metrics.turn_rate(u_maze().longest_path), 2 / 13)


class SolverTest(unittest.TestCase):
    def test_corridor_solvers_never_waste_moves(self):
        grid = corridor(10)
        start, goal = grid.longest_path[0], grid.longest_path[-1]
        self.assertEqual(metrics.random_solver_steps(start, goal, seed=1), 9.0)
        self.assertEqual(metrics.greedy_solver_ratio(grid, start, goal, 10, seed=1), 1.0)

    def test_greedy_is_misled_by_u_maze(self):
        grid = u_maze()
        path = grid.longest_path
        ratio = metrics.greedy_solver_ratio(grid, path[0], path[-1], len(path), seed=1)
        self.assertAlmostEqual(ratio, 20 / 14)

    def test_random_solver_is_deterministic(self):
        grid = corridor_with_branch(10, 2, 5)
        path = grid.longest_path
        first = metrics.random_solver_steps(path[0], path[-1], seed=3)
        second = metrics.random_solver_steps(path[0], path[-1], seed=3)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first, len(path) - 1)


class CoverageTest(unittest.TestCase):
    def test_corridor_covers_its_only_row(self):
        grid = corridor(8)
        cells = metrics.linked_cells(grid)
        self.assertEqual(metrics.spatial_coverage(grid, cells, grid.longest_path), 1.0)

    def test_branch_cells_not_on_path_reduce_coverage(self):
        grid = corridor_with_branch(4, 0, 3)
        cells = metrics.linked_cells(grid)
        self.assertLess(metrics.spatial_coverage(grid, cells, grid.longest_path), 1.0)


if __name__ == "__main__":
    unittest.main()
