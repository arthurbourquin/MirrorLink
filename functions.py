import bpy
import bmesh
from mathutils import Vector

ml_name = 'sym-binom' # attribute, domain: point, type: int

def get_bmesh():
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


def build_sym_from_semi_mesh(merge_threshold=1e-4):
    obj, mesh, bm, ml_layer = get_bmesh()
    if not obj:
        return

    # store idx for further binom
    for v in bm.verts:
        v[ml_name] = v.index

    orig_verts = list(bm.verts)

    dup_geom = bmesh.ops.duplicate(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces))
    dup_verts = dup_geom["vert_map"]
    dup_faces = dup_geom["face_map"]

    # set binom
    for v in orig_verts:
        

    # mirror
    for d in dup_geom:
        if isinstance(d, bmesh.types.BMVert):
            d.co.x *= -1.0

    # flip normals    
    dup_faces = [g for g in dup_geom if isinstance(g, bmesh.types.BMFace)]
    bmesh.ops.reverse_faces(bm, faces=dup_faces)

    # at x=0 vertices
    zero_x_verts = [v for v in bm.verts if abs(v.co.x) < merge_threshold]
    for v in zero_x_verts:
        v[ml_name] = v.index
    if zero_x_verts:
        bmesh.ops.remove_doubles(
            bm, verts=zero_x_verts, dist=merge_threshold,
        )


    


def find_and_set_binoms():
    print("On cherche et on trouve")
