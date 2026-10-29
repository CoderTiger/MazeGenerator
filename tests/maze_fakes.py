"""Test helpers: import the add-on's pure modules without bpy, and build tiny fake mazes."""

import sys
import types
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parents[1] / "maze_generator"
if "maze_generator" not in sys.modules:
    # The real maze_generator/__init__.py imports bpy; register a bare package instead.
    _stub = types.ModuleType("maze_generator")
    _stub.__path__ = [str(_PACKAGE_DIR)]
    sys.modules["maze_generator"] = _stub

_DIRECTIONS = {(0, 1): 0, (1, 0): 1, (0, -1): 2, (-1, 0): 3}


class FakeCell:
    def __init__(self, column, row, level=0):
        self.column = column
        self.row = row
        self.level = level
        self.links = []

    def has_any_link(self):
        return len(self.links) > 0

    def get_neighbor_direction(self, other):
        return _DIRECTIONS.get((other.column - self.column, other.row - self.row), -1)

    def __repr__(self):
        return f"FakeCell(c{self.column};r{self.row})"


class FakeGrid:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        self._cells = {}
        self.longest_path = []

    def cell(self, column, row):
        key = (column, row)
        if key not in self._cells:
            self._cells[key] = FakeCell(column, row)
        return self._cells[key]

    def link(self, a, b):
        cell_a, cell_b = self.cell(*a), self.cell(*b)
        cell_a.links.append(cell_b)
        cell_b.links.append(cell_a)

    def set_path(self, coords):
        self.longest_path = [self.cell(*c) for c in coords]

    @property
    def all_cells(self):
        return list(self._cells.values())

    def get_columns_this_row(self, row):
        return self.columns


def corridor(length):
    """Straight east-west corridor; solution runs from column 0 to column length - 1."""
    grid = FakeGrid(length, 1)
    for column in range(length - 1):
        grid.link((column, 0), (column + 1, 0))
    grid.set_path([(column, 0) for column in range(length)])
    return grid


def corridor_with_branch(length, branch_column, branch_depth):
    """Corridor on row 0 plus a dead-end branch going north from branch_column."""
    grid = FakeGrid(length, branch_depth + 1)
    for column in range(length - 1):
        grid.link((column, 0), (column + 1, 0))
    for row in range(branch_depth):
        grid.link((branch_column, row), (branch_column, row + 1))
    grid.set_path([(column, 0) for column in range(length)])
    return grid


def comb(length, tooth_depth):
    """Corridor on row 0 with dead-end teeth going north from every odd column: easy to beat by heading east."""
    grid = FakeGrid(length, tooth_depth + 1)
    for column in range(length - 1):
        grid.link((column, 0), (column + 1, 0))
    for column in range(1, length - 1, 2):
        for row in range(tooth_depth):
            grid.link((column, row), (column, row + 1))
    grid.set_path([(column, 0) for column in range(length)])
    return grid


def u_maze():
    """U-shaped solution from (0,0) to (4,0) plus a tempting dead end from (0,0) east to (3,0)."""
    grid = FakeGrid(5, 6)
    path = [(0, row) for row in range(6)] + [(column, 5) for column in range(1, 5)]
    path += [(4, row) for row in range(4, -1, -1)]
    for a, b in zip(path, path[1:]):
        grid.link(a, b)
    for column in range(3):
        grid.link((column, 0), (column + 1, 0))
    grid.set_path(path)
    return grid
