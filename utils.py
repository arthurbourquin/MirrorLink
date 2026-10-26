import bpy
import bmesh

from enum import IntEnum
from mathutils import Vector
from mathutils.kdtree import KDTree


#=========#=========#=========#=========#=========#=========#=========#=========
# ENUM AND PAIR ID
#=========#=========#=========#=========#=========#=========#=========#=========

ATTNAME = 'pair-id'

class ATT(IntEnum):
    FIRSTPAIR = 0
    CENTER = -1
    UNSET = -2
    IGNORE = -3

def is_pair(att): return att >= ATT.FIRSTPAIR
def is_center(att): return att == ATT.CENTER
def is_unset(att): return att == ATT.UNSET
def is_ignore(att): return att == ATT.IGNORE

def get_available_pair_id(bm, ml_layer):
    return max([v[ml_layer] for v in bm.verts]) + 1

def group_verts_by_pid(verts, ml_layer):
    vert_dict = dict()
    for v in verts:
        pid = v[ml_layer]
        if not pid in vert_dict:
            vert_dict[pid] = []
        vert_dict[pid].append(v)
    return vert_dict

from enum import IntEnum, auto
class ENUM(IntEnum):
    X_NEGATIVE = auto()
    X_POSITIVE = auto()
    AVERAGE = auto()
    ACTIVE = auto()
    NONE = auto()
    MOVE = auto()

    REPORT = auto()
    SET = auto()
    SELECT = auto()

    SELECTED = auto()
    ALL = auto()


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

def symetrize_coordinates(co1, co2, mode): # if active: co1 is active
    if mode == ENUM.AVERAGE:
        co = (mirror(co1) + co2) / 2
        co1 = mirror(co)
        co2 = co
    elif mode == ENUM.X_NEGATIVE:
        if co1.x < co2.x:
            co2 = mirror(co1)
        else:
            co1 = mirror(co2)
    elif mode == ENUM.X_POSITIVE:
        if co1.x > co2.x:
            co2 = mirror(co1)
        else:
            co1 = mirror(co2)
    elif mode == ENUM.ACTIVE:
        co2 = mirror(co1)
    return co1, co2

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
    # get bmesh
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    # prepare vertex indices
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    # get or create attribute
    ml_layer = bm.verts.layers.int.get(ATTNAME)
    if ml_layer is None:
        ml_layer = bm.verts.layers.int.new(ATTNAME)
        for v in bm.verts:
            v[ml_layer] = ATT.UNSET
    return (obj, mesh, bm, ml_layer, objmode)



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

def build_tree(verts):
    tree = KDTree(len(verts))
    for v in verts:
        tree.insert(v.co, v.index)
    tree.balance()
    return tree




#=========#=========#=========#=========#=========#=========#=========#=========
# ...
#=========#=========#=========#=========#=========#=========#=========#=========

def get_overlapping(bm, verts, tree, threshold=1e-4):
    overlapping = set()
    for v in verts:
        res = tree.find_range(v.co, threshold)
        for _co, idx, dst in res:
            other = bm.verts[idx]
            if other == v:
                continue
            if dst < threshold:
                overlapping.add(other)
    return overlapping

def get_center_candidates(verts, threshold=1e-4):
    centers = set()
    for v in verts:
        if abs(v.co.x) < threshold:
            centers.add(v)
    return centers

def get_pairs_candidates(bm, verts, tree, threshold=1e-4):
    verts = set(verts)
    candidates = {v: [] for v in verts}
    for v in verts:
        if abs(v.co.x) < threshold:
            continue
        mirrored = mirror(v.co)
        res = tree.find_range(mirrored, threshold)
        for _co, idx, _dst in res:
            other = bm.verts[idx]
            if other in verts and other != v:
                candidates[v].append(other)
    pairs = set()
    for v in verts:
        if len(candidates[v]) != 1:
            continue
        other = candidates[v][0]
        if candidates[other] == [v]:
            left, right = sorted([v, other], key=lambda p: p.co.x)
            pairs.add((left, right))
    return pairs # flat for now, keep code for further use

def get_bad_pairs(pairs_, ml_layer, threshold=1e-4):
    pairs = [v for v in pairs_ if is_pair(v[ml_layer])]
    pair_dict = group_verts_by_pid(pairs, ml_layer)
    broken_pairs = []
    mislocated_pairs = []
    for verts in pair_dict.values():
        if len(verts) != 2:
            broken_pairs += verts
        else:
            v1, v2 = verts
            v = v1.co - mirror(v2.co)
            dst2 = v.x*v.x + v.y*v.y + v.z*v.z
            if dst2 > threshold* threshold:
                mislocated_pairs += verts
    return broken_pairs, mislocated_pairs

def pack_pid(bm, ml_layer, unset_broken_pairs=False):
    verts_by_pid: dict[int, list] = group_verts_by_pid(bm.verts, ml_layer)
    pair_verts_by_pid = {
        pid: verts for pid, verts in verts_by_pid.items() if is_pair(pid)
    }
    next_pid = 0
    for verts in pair_verts_by_pid.values():
        if unset_broken_pairs and len(verts) != 2:
            for v in verts:
                v[ml_layer] = ATT.UNSET
        else:
            for v in verts:
                v[ml_layer] = next_pid
            next_pid += 1
    return next_pid