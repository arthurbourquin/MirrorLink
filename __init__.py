bl_info = {
    "name": "MirrorLink",
    "author": "Tohm",
    "version": (0, 1, 0),
    "blender": (4, 2, 23),
    "location": "View3D > Sidebar > MirrorLink",
    "description": "Tool for managing mesh symmetry",
    "category": "Mesh",
}

from . import scene_properties
from . import operators, ui
from .core import register, unregister
