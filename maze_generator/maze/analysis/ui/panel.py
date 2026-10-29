"""
Rating Panel
"""

import bpy
from maze_generator.maze.analysis.store import get_rating


class RatingPanel(bpy.types.Panel):
    """
    Rating Panel
    """

    bl_idname = "MAZE_GENERATOR_PT_RatingPanel"
    bl_label = "Rating"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MG"

    @classmethod
    def poll(cls, context):
        objects = context.scene.mg_props.objects
        return objects.cells or objects.walls

    def draw_header(self, context):
        self.layout.label(text="", icon="SOLO_ON")

    def draw(self, context):
        layout = self.layout
        mg_props = context.scene.mg_props
        rating = get_rating(context.scene.name_full)
        if rating is None:
            layout.label(text="Generate a maze to see its rating", icon="INFO")
            return
        if not rating.ratable:
            layout.label(text=f"Rating unavailable: {rating.reason}", icon="ERROR")
            return

        layout.label(text=f"Difficulty : {rating.difficulty} / 100 ({rating.difficulty_level})", icon="MOD_DYNAMICPAINT")
        layout.label(text=f"Fun : {rating.fun} / 100 (heuristic)", icon="FUND")
        if rating.has_directional_bias:
            layout.label(text="Strong directional bias: easier than it looks", icon="ERROR")

        display = mg_props.display
        layout.prop(
            display,
            "show_rating_details",
            text="Details",
            icon="TRIA_DOWN" if display.show_rating_details else "TRIA_RIGHT",
            emboss=False,
        )
        if display.show_rating_details:
            self._draw_parts(layout, "Difficulty", rating.difficulty_parts)
            self._draw_parts(layout, "Fun", rating.fun_parts)

    @staticmethod
    def _draw_parts(layout, title, parts):
        box = layout.box()
        box.label(text=title)
        for name, value in parts.items():
            box.label(text=f"{name} : {round(value * 100)}")
