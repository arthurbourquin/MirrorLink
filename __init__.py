bl_info = {
    "name": "MirrorLink",
    "author": "Tohm",
    "version": (0, 1, 0),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > MirrorLink",
    "description": "Tool for managing mesh symmetry",
    "category": "Mesh",
}


import bpy
from . import ui
from . import operators


classes = (
    # pannels
    ui.MIRRORLINK_PT_MainPanel,
    # operators
    operators.MIRRORLINK_OT_SetBinoms,
    operators.MIRRORLINK_OT_BuildSymFromSemiMesh,
)


def register(): # pour enregistrer la class et qu'elle soit utilisable
    for c in classes:
        bpy.utils.register_class(c)

def unregister(): # désenregistre la classe de Blender
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    print("wesh")
    register()






