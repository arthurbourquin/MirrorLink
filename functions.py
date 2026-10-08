import bpy
import bmesh
from mathutils import Vector

MIRLNKATT = 'sym-binom' # attribute, domain: point, type: int

def get_bmesh():
    obj = mesh = bm = None
    user_mode = obj.mode
    obj = bpy.context.active_object
    if obj and obj.type == 'MESH':
        if user_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode=user_mode)
    return [obj, mesh, bm]

def mirror_x(obj, merge_threshold=1e-4):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    # duplicate
    dup_geom = bmesh.ops.duplicate(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces))["geom"]
    # mirror
    for d in dup_geom:
        if isinstance(d, bmesh.types.BMVert):
            d.co.x *= -1.0
    # flip normals    
    dup_faces = [g for g in dup_geom if isinstance(g, bmesh.types.BMFace)]
    bmesh.ops.reverse_faces(bm, faces=dup_faces)
    # merge
    verts_to_weld = [v for v in bm.verts if abs(v.co.x) < merge_threshold]
    if verts_to_weld:
        bmesh.ops.remove_doubles(
            bm, verts=verts_to_weld, dist=merge_threshold,
        )
    # ...
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()



def build_sym_from_semi_mesh(merge_threshold=1e-4):
    obj, mesh, bm = get_bmesh()
    if not obj:
        return

    # store idx for further binom
    for v in bm.verts:
        v[MIRLNKATT] = v.index

    # duplicate
    dup_geom = bmesh.ops.duplicate(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces))["geom"]

    # set binom
    for v in bm.verts:
        if v[MIRLNKATT] == v.index:
            v[MIRLNKATT] = []

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
        v[MIRLNKATT] = v.index
    if zero_x_verts:
        bmesh.ops.remove_doubles(
            bm, verts=zero_x_verts, dist=merge_threshold,
        )


    


def find_and_set_binoms():
    print("On cherche et on trouve")
