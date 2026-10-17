import bpy
import bmesh
from enum import IntEnum
from mathutils import Vector

ATTNAME = 'pair-id'

class ENUM(IntEnum):
    # Mirror Link Addon Attribute
    FIRSTPAIR = 1
    CENTER = 0
    UNSET = -1
    IGNORE = -2
    USERIGNORE = -3
    FORCEIGNORE = -4
    # modes
    XPOSITIVE = -10
    XNEGATIVE = -11
    AVERAGE = -20
    ACTIVE = -21



def alert(message, title="Tohm Mirror Link", icon='INFO'):
    if isinstance(message, list):
        lines = [str(msg) for msg in message]
    elif isinstance(message, str):
        lines = message.split("\n")
    else:
        lines = [str(message)]

    def draw(self, context):
        for l in lines:
            self.layout.label(text=l)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def get_bmesh_stuff():
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        return (None, None, None, None)
    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    ml_layer = bm.verts.layers.int.get(ATTNAME)
    if ml_layer is None:
        ml_layer = bm.verts.layers.int.new(ATTNAME)
        for v in bm.verts:
            v[ml_layer] = -1
    return (obj, mesh, bm, ml_layer)



def mirror(co):
    return Vector((-co.x, co.y, co.z))