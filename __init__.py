bl_info = {
    "name": "MirrorLink",
    "author": "Tohm",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > MirrorLink",
    "description": "Tool for managing mesh symmetry",
    "category": "Mesh",
}

# Ces imports suffisent à enregistrer les classes (via @register_me)
from . import operators, ui  # noqa: F401
from .core import register, unregister  # noqa: F401
