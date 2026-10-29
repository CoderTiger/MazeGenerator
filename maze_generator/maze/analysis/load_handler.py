"""
Recompute maze ratings when a .blend file is opened.
Ratings are runtime-only, so they are rebuilt by replaying the maze logic from the saved scene parameters.
"""

import bpy
from bpy.app.handlers import persistent
from maze_generator.blender.generation.operators.generate_maze import build_grid
from maze_generator.maze.analysis.rating import rate_maze
from maze_generator.maze.analysis.store import clear_ratings, set_rating


@persistent
def rate_mazes_on_load(_dummy):
    clear_ratings()
    for scene in bpy.data.scenes:
        props = scene.mg_props
        if not (props.objects.cells or props.objects.walls):
            continue
        try:
            grid = build_grid(props)
        except Exception:  # Rating must never break file loading.
            continue
        if grid is not None:
            set_rating(scene.name_full, rate_maze(grid, props.algorithm.seed))


def register():
    if rate_mazes_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(rate_mazes_on_load)


def unregister():
    if rate_mazes_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(rate_mazes_on_load)
