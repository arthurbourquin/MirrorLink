import bpy
import bmesh
from mathutils import Vector


ml_name = 'binom-id' # attribute, domain: point, type: int



#---------#---------#---------#---------
# HELPERS

def get_bmesh_stuff():
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        return (None, None, None, None)
    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    ml_layer = bm.verts.layers.int.get(ml_name)
    if ml_layer is None:
        ml_layer = bm.verts.layers.int.new(ml_name)
        for v in bm.verts:
            v[ml_layer] = -1
    return (obj, mesh, bm, ml_layer)


def refresh_indices(bm):
    for seq in (bm.verts, bm.edges, bm.faces):
        seq.index_update()
        seq.ensure_lookup_table()


def check_binoms(obj, mesh, bm, ml_layer, merge_threshold=1e-4):
    # count binom ids instances (how many bid x, bid y, etc.)
    bids = dict() # {bid: count}
    for v in bm.verts:
        bid = v[ml_layer]
        if not bid in bids:
            bids[v] = 0
        bids[v] += 1
    # arrange binom ids by count
    bids_trans = dict()
    for bid, count in bids.items():
        if not count in bids_trans:
            bids_trans[count] = []
        bids_trans[count].append(bid)
    # calculate statistics
    vert_count = len(bm.verts)    
    bid_count = len(bids)
    zero_x_vert_count = len([v for v in bm.verts if abs(v.co.x) < merge_threshold])
    



#---------#---------#---------#---------
# FUNCTIONS

def build_sym_from_semi_mesh(merge_threshold=1e-4):
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    if not obj:
        return

    orig_verts = list(bm.verts)
    orig_faces = list(bm.faces)
    dup_res = bmesh.ops.duplicate(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces))
    vert_map = dup_res["vert_map"] # orig and dup
    face_map = dup_res["face_map"] # orig and dup

    # set binom & mirror
    i = 0
    for v in orig_verts:
        # set binom
        binom = vert_map[v]
        v[ml_layer] = binom[ml_layer] = i
        i += 1
        # mirror
        binom.co.x *= -1.0

    # flip normals    
    dup_faces = [face_map[f] for f in orig_faces]
    bmesh.ops.reverse_faces(bm, faces=dup_faces)

    # merge
    zero_x_verts = [v for v in bm.verts if abs(v.co.x) < merge_threshold]
    if zero_x_verts:
        bmesh.ops.remove_doubles(bm, verts=zero_x_verts, dist=merge_threshold,)


def find_and_set_binoms():
    print("On cherche et on trouve")


