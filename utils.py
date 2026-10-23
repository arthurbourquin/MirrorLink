import bpy
import bmesh
from enum import IntEnum
from mathutils import Vector
from mathutils.kdtree import KDTree

ATTNAME = 'pair-id'

class ENUM(IntEnum):
    # Mirror Link Addon Attribute
    FIRSTPAIR = 1
    CENTER = 0
    UNSET = -1
    IGNORE = -2
    # modes
    XPOSITIVE = -10
    XNEGATIVE = -11
    AVERAGE = -20
    ACTIVE = -21
    # getters
    SELECT = -30
    RETURN = -31



#=========#=========#=========#=========#=========#=========#=========#=========
# PRINT ALERT
#=========#=========#=========#=========#=========#=========#=========#=========

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



#=========#=========#=========#=========#=========#=========#=========#=========
# MISCELLANEOUS
#=========#=========#=========#=========#=========#=========#=========#=========

def mirror(co):
    return Vector((-co.x, co.y, co.z))

def get_available_pair_id(bm, ml_layer):
    return max([v[ml_layer] for v in bm.verts]) + 1



#=========#=========#=========#=========#=========#=========#=========#=========
# BMESH
#=========#=========#=========#=========#=========#=========#=========#=========

def get_bmesh_stuff():
    # get active object
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        return (None, None, None, None, None)
    # save current mode and force Edit Mode
    objmode = obj.mode
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    # get or create attribute
    ml_layer = bm.verts.layers.int.get(ATTNAME)
    if ml_layer is None:
        ml_layer = bm.verts.layers.int.new(ATTNAME)
        for v in bm.verts:
            v[ml_layer] = -1
    return (obj, mesh, bm, ml_layer, objmode)

def refresh_indices(bm):
    for seq in (bm.verts, bm.edges, bm.faces):
        seq.index_update()
        seq.ensure_lookup_table()



#=========#=========#=========#=========#=========#=========#=========#=========
# KDTREE RELATED
#=========#=========#=========#=========#=========#=========#=========#=========

def nearest_mirror(bm, tree, v):
    mirrored = mirror(v.co)
    co, idx, gap = tree.find(mirrored)
    other = bm.verts[idx]
    dx = v.co.x + other.co.x
    dy = v.co.y - other.co.y
    dz = v.co.z - other.co.z
    return other, gap, (dx, dy, dz)

def build_tree(bm):
    bm.verts.ensure_lookup_table()
    tree = KDTree(len(bm.verts))
    for v in bm.verts:
        tree.insert(v.co, v.index)
    tree.balance()
    return tree



#=========#=========#=========#=========#=========#=========#=========#=========
# GET
#=========#=========#=========#=========#=========#=========#=========#=========

def get_center_candidates(obj, mesh, bm, ml_layer, objmode, threshold):
    exact = dict()
    near = dict()
    for v in bm.verts:
        dst = abs(v.co.x)
        if dst == 0.0:
            exact.add(v)
        else:
            near.add(v)
    return {0.0: exact, threshold: near}

def get_pair_candidates(obj, mesh, bm, ml_layer, objmode, tree, threshold):
    print("=== Get Pairs Candidates ===")
    exact = dict()
    near = dict()
    for v in bm.verts:
        co = mirror(v.co)
        res = tree.find_range(co, threshold)
        exact_ = 0
        near_ = 0
        for _co, idx, dst in res:
            if idx != v.index:
                if dst == 0.0:
                    exact_ += 1
                else:
                    near_ += 1
        if exact_:
            exact.setdefault(exact_, set()).add(v)
        if near_:
            near.setdefault(near_, set()).add(v)
    obj.mode = objmode
    return {0.0: exact, threshold: near}

