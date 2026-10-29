"""
Main file required by Blender Add-on
"""
import sys

# When the add-on is installed or updated in a running Blender session, only this package is reloaded and
# stale submodules stay cached. Drop them (from sys.modules and from this package's namespace, which
# `from maze_generator import x` would otherwise reuse) so every submodule is imported from the new files.
for _module_name in [name for name in sys.modules if name.startswith(__name__ + ".")]:
    del sys.modules[_module_name]
    globals().pop(_module_name[len(__name__) + 1 :].split(".")[0], None)

from bpy.utils import register_class, unregister_class
from maze_generator import auto_load
from maze_generator.blender.ui.panels import panels


bl_info = {
    "name": "Maze Generator",
    "author": "Gorgious",
    "description": "Add-on for generating mazes with a bunch of settings",
    "blender": (4, 5, 0),
    "version": (0, 5, 0),
    "location": "",
    "warning": "",
    "category": "Add Mesh",
    "doc_url": "https://github.com/Gorgious56/MazeGenerator/blob/master/README.md",
}


def register():
    for panel in panels:
        register_class(panel)
    auto_load.init()
    auto_load.register()


def unregister():
    auto_load.unregister()
    for panel in reversed(panels):
        unregister_class(panel)
