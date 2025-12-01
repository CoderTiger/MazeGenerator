"""
Weave Grid
"""


from mathutils import Vector
from .grid import (
    Grid,
    Cell,
    CellOver,
    CellUnder,
)


class GridWeave(Grid):
    """
    Weave Grid
    """

    def __init__(self, *args, use_kruskal: bool = False, weave: int = 0, **kwargs):
        self.use_kruskal = use_kruskal
        self.weave = weave / 100
        super().__init__(*args, **kwargs)

    def prepare_grid(self):
        if self.use_kruskal:
            CellOver.get_neighbors = lambda: Cell.neighbors
        else:
            CellOver.get_neighbors = lambda: CellOver.neighbors_copy

        for l in range(self.levels):
            for c in range(self.columns):
                for r in range(self.rows):
                    if self[c, r, l] is None:
                        new_cell = CellOver(r, c, l, half_neighbors=(0, 1))
                        # Initialize vertex data for CellOver
                        size = self.cell_size
                        center = Vector((c + l * (self.columns + 1), r, 0))
                        new_cell.first_vert_index = len(self.verts)
                        self.verts.extend(
                            (
                                center + Vector((size / 2, size / 2, 0)),
                                center + Vector((-size / 2, size / 2, 0)),
                                center + Vector((-size / 2, -size / 2, 0)),
                                center + Vector((size / 2, -size / 2, 0)),
                            )
                        )
                        self[c, r, l] = new_cell
                    
                    if self[c, r, l]:
                        self[c, r, l].request_tunnel_under += lambda cell, neighbor: self.tunnel_under(neighbor)

    def tunnel_under(self, cell_over):
        """
        Tunnel under the specified cell of type 'CellOver'

        Returns the resulting 'CellUnder'
        """
        new_cell = CellUnder(cell_over)
        
        # Generate vertices for the new cell (required for mesh generation)
        size = self.cell_size
        column = new_cell.column
        row = new_cell.row
        level = new_cell.level
        
        center = Vector((column + level * (self.columns + 1), row, -0.5 * size))
        
        new_cell.first_vert_index = len(self.verts)
        self.verts.extend(
            (
                center + Vector((size / 2, size / 2, 0)),
                center + Vector((-size / 2, size / 2, 0)),
                center + Vector((-size / 2, -size / 2, 0)),
                center + Vector((size / 2, -size / 2, 0)),
            )
        )

        self._cells.append(new_cell)
        self._union_find.data[new_cell] = new_cell
        return new_cell
