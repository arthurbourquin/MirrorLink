import bpy
import bmesh
from mathutils import Vector


ml_name = 'binom-id' # attribute, domain: point, type: int



#---------#---------#---------#---------
# DEBUG

def debug():
    print("=== debug BEGIN ===")
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    ouais = sorted(bm.verts, key=lambda v: v[ml_layer])
    for v in ouais:
        print(f"{v[ml_layer]: <2} {v.index: <2} {v.co.x}")
    print("=== debug END ===")



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
    print("=== check binom BEGIN ===")

    print("count ids")
    bids = dict() # {bid: count}
    for v in bm.verts:
        bid = v[ml_layer]
        if not bid in bids:
            bids[bid] = 0
        bids[bid] += 1

    print("arrange ids by count")
    bids_trans = {1: [], 2: [], 3: []} # {count: bids[]}
    for bid, count in bids.items():
        count = 3 if count >= 3 else count
        bids_trans[count].append(bid)
    print(f"single binoms: {len(bids_trans[1])}")
    print(f"dual binoms: {len(bids_trans[2])}")
    print(f"more than 3: {len(bids_trans[3])}")

    print("=== check binom END ===")


#---------#---------#---------#---------
# FUNCTIONS

def build_sym_from_semi_mesh(merge_threshold=1e-4):
    print("=== build sym from semi mesh BEGIN ===")

    print("get bmesh stuff")
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    if not obj:
        return

    print("bmesh ops duplicate")
    orig_verts = list(bm.verts)
    orig_faces = list(bm.faces)
    dup_res = bmesh.ops.duplicate(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces))
    vert_map = dup_res["vert_map"] # orig and dup
    face_map = dup_res["face_map"] # orig and dup

    print("set binom ids and mirror")
    # set binom & mirror
    i = 0
    for v in orig_verts:
        # set binom
        binom = vert_map[v]
        v[ml_layer] = binom[ml_layer] = i
        i += 1
        # mirror
        binom.co.x *= -1.0

    print("flip normals")
    # flip normals    
    dup_faces = [face_map[f] for f in orig_faces]
    bmesh.ops.reverse_faces(bm, faces=dup_faces)

    print("merge vertices at x=0")
    # merge
    zero_x_verts = [v for v in bm.verts if abs(v.co.x) < merge_threshold]
    if zero_x_verts:
        bmesh.ops.remove_doubles(bm, verts=zero_x_verts, dist=merge_threshold,)

    print("update mesh")
    bmesh.update_edit_mesh(mesh)

    print("check binoms")
    check_binoms(obj, mesh, bm, ml_layer, merge_threshold)

    print("=== build sym from semi mesh END ===")


def find_and_set_binoms():
    print("=== find and set binoms ===")


