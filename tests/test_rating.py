import unittest

import maze_fakes
from maze_fakes import FakeGrid, comb, corridor, corridor_with_branch, u_maze
from maze_generator.maze.analysis.rating import rate_maze


class RatingScoresTest(unittest.TestCase):
    def test_straight_corridor_is_easy_and_monotonous(self):
        rating = rate_maze(corridor(10), seed=1)
        self.assertTrue(rating.ratable)
        self.assertLess(rating.difficulty, 25)
        self.assertEqual(rating.difficulty_level, "Easy")
        self.assertLess(rating.fun_parts["Path rhythm"], 0.1)

    def test_deep_branch_is_harder_than_stub(self):
        deep = rate_maze(corridor_with_branch(10, 2, 5), seed=1)
        stub = rate_maze(corridor_with_branch(10, 2, 1), seed=1)
        self.assertGreater(deep.difficulty, stub.difficulty)
        self.assertEqual(deep.fun_parts["Choice quality"], 1.0)
        self.assertEqual(stub.fun_parts["Choice quality"], 0.0)

    def test_directional_bias_detection(self):
        biased = rate_maze(comb(12, 4), seed=1)
        self.assertTrue(biased.has_directional_bias)
        self.assertEqual(biased.fun_parts["No directional shortcut"], 0.0)
        tricky = rate_maze(u_maze(), seed=1)
        self.assertFalse(tricky.has_directional_bias)
        self.assertGreater(tricky.fun_parts["No directional shortcut"], 0.0)

    def test_maze_without_choices_is_not_flagged_as_biased(self):
        rating = rate_maze(corridor(10), seed=1)
        self.assertFalse(rating.has_directional_bias)
        self.assertEqual(rating.fun_parts["No directional shortcut"], 1.0)

    def test_bigger_maze_is_harder(self):
        small = rate_maze(comb(12, 4), seed=1)
        big = rate_maze(comb(60, 20), seed=1)
        self.assertGreater(big.difficulty_parts["Solver effort"], small.difficulty_parts["Solver effort"])
        self.assertGreater(big.difficulty, small.difficulty)

    def test_scores_and_parts_are_in_range(self):
        rating = rate_maze(u_maze(), seed=4)
        self.assertTrue(0 <= rating.difficulty <= 100)
        self.assertTrue(0 <= rating.fun <= 100)
        for value in list(rating.difficulty_parts.values()) + list(rating.fun_parts.values()):
            self.assertTrue(0.0 <= value <= 1.0)
        self.assertEqual(
            list(rating.difficulty_parts),
            ["Decision density", "False branch depth", "Solver effort", "Path share"],
        )
        self.assertEqual(
            list(rating.fun_parts),
            ["Difficulty sweet spot", "Choice quality", "Path rhythm", "Spatial coverage", "No directional shortcut"],
        )

    def test_deterministic(self):
        self.assertEqual(rate_maze(corridor_with_branch(10, 2, 5), seed=7), rate_maze(corridor_with_branch(10, 2, 5), seed=7))


class UnratableTest(unittest.TestCase):
    def test_single_cell(self):
        grid = FakeGrid(1, 1)
        grid.set_path([(0, 0)])
        rating = rate_maze(grid, seed=1)
        self.assertFalse(rating.ratable)
        self.assertEqual(rating.reason, "maze too small")

    def test_missing_path(self):
        grid = corridor(5)
        grid.longest_path = [None]
        self.assertEqual(rate_maze(grid, seed=1).reason, "no solution path")

    def test_unreachable_goal(self):
        grid = FakeGrid(4, 1)
        grid.link((0, 0), (1, 0))
        grid.link((2, 0), (3, 0))
        grid.set_path([(0, 0), (3, 0)])
        self.assertEqual(rate_maze(grid, seed=1).reason, "goal unreachable")

    def test_internal_error_is_contained(self):
        class BrokenGrid:
            @property
            def all_cells(self):
                raise RuntimeError("boom")

        rating = rate_maze(BrokenGrid(), seed=1)
        self.assertFalse(rating.ratable)
        self.assertEqual(rating.reason, "internal error")


class StoreTest(unittest.TestCase):
    def test_store_keeps_latest_rating_per_scene(self):
        from maze_generator.maze.analysis.store import get_rating, set_rating

        first, second = rate_maze(corridor(5), seed=1), rate_maze(u_maze(), seed=1)
        set_rating("Scene", first)
        set_rating("Scene", second)
        self.assertIs(get_rating("Scene"), second)
        self.assertIsNone(get_rating("Other Scene"))

    def test_clear_ratings(self):
        from maze_generator.maze.analysis.store import clear_ratings, get_rating, set_rating

        set_rating("Scene", rate_maze(corridor(5), seed=1))
        clear_ratings()
        self.assertIsNone(get_rating("Scene"))


if __name__ == "__main__":
    unittest.main()
