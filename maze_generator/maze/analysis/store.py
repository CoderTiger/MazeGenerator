"""
Runtime-only storage of the latest maze rating per scene.
Blender recreates RNA wrappers on every access, so plain Python attributes set on
`scene.mg_props` are lost; panels read the rating from here instead.
"""

_ratings = {}


def set_rating(scene_key, rating):
    _ratings[scene_key] = rating


def get_rating(scene_key):
    return _ratings.get(scene_key)


def clear_ratings():
    _ratings.clear()
