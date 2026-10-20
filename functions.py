import bpy
import bmesh
from math import floor, log10
from mathutils import Vector
from mathutils.kdtree import KDTree

from . import utils
from .utils import ENUM



#=========#=========#=========#=========#=========#=========#=========#=========
# UTILITY
#=========#=========#=========#=========#=========#=========#=========#=========

def refresh_indices(bm):
    for seq in (bm.verts, bm.edges, bm.faces):
        seq.index_update()
        seq.ensure_lookup_table()

def build_tree(bm):
    bm.verts.ensure_lookup_table()
    tree = KDTree(len(bm.verts))
    for v in bm.verts:
        tree.insert(v.co, v.index)
    tree.balance()
    return tree

def nearest_mirror(bm, tree, v):
    """Retourne (vertex_miroir, dist_3d, (dx, dy, dz)) pour le vertex v."""
    mirrored = Vector((-v.co.x, v.co.y, v.co.z))
    co, idx, gap = tree.find(mirrored)
    other = bm.verts[idx]

    dx = v.co.x + other.co.x
    dy = v.co.y - other.co.y
    dz = v.co.z - other.co.z
    return other, gap, (dx, dy, dz)

def get_available_pair_id(bm, ml_layer):
    return max([v[ml_layer] for v in bm.verts]) + 1


#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION (GEOMETRY BASED)
#=========#=========#=========#=========#=========#=========#=========#=========

def select_overlapping_vertices(threshold):
    print("Select Overlapping Vertices")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    refresh_indices(bm)
    tree = build_tree(bm)
    count = 0
    for v in bm.verts:
        for _, idx, _ in tree.find_range(v.co, threshold):
            other = bm.verts[idx]
            if idx != v.index:
                v.select_set(True)
                count += 1
            else:
                v.select_set(False)
    print(f"{count} vertices selected")
    bmesh.update_edit_mesh(mesh)

def select_ambigous(threshold):
    print("Select Center Vertices")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    refresh_indices(bm)
    pair_bucket = bucketize_for_pairs(bm, threshold)
    sel_pair = pair_bucket[float("inf")]
    center_bucker = bucketize_for_center(bm, threshold)
    sel_ctr = center_bucker[float("inf")]
    sel_ignore = set([v for v in bm.verts if v[ml_layer] != ENUM.IGNORE])
    ambigous = sel_pair & sel_ctr & sel_ignore
    print(len(ambigous))
    for v in bm.verts:
        v.select_set(False)
    for v in ambigous:
        v.select_set(True)
    bmesh.update_edit_mesh(mesh)


def select_center_vertices(threshold):
    print("Select Center Vertices")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    count = 0
    for v in bm.verts:
        if abs(v.co.x) < threshold:
            v.select_set(True)
            count += 1
        else:
            v.select_set(False)
    print(f"{count} vertices selected")
    bmesh.update_edit_mesh(mesh)



#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION (ATTRIBUTE BASED)
#=========#=========#=========#=========#=========#=========#=========#=========

def select_pairs():
    print("Select Pairs")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    count = 0
    for v in bm.verts:
        if v[ml_layer] >= 0:
            v.select_set(True)
            count += 1
        else:
            v.select_set(False)
    print(f"{count} vertices selected")
    bmesh.update_edit_mesh(mesh)

def select_by_attribute_value(attribute_value):
    print(f"Select by attribute {attribute_value}")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    count = 0
    for v in bm.verts:
        val = v[ml_layer]
        val = min(val, 1)
        if attribute_value == val:
            v.select_set(True)
        else:
            v.select_set(False)
    print(f"{count} vertices selected")
    bmesh.update_edit_mesh(mesh)



#=========#=========#=========#=========#=========#=========#=========#=========
# SET ATTRIBUTE
#=========#=========#=========#=========#=========#=========#=========#=========

def set_selected(attribute_value):
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    for v in bm.verts:
        if v.select:
            v[ml_layer] = attribute_value

def set_id_to_selected_pair():
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    select = [v for v in bm.verts if v.select]
    if len(select) != 2:
        utils.alert(f"{len(select)} selected vertices, require exactely two.")
        return
    v1, v2 = select
    choosen_id = min(v1[ml_layer], v2[ml_layer])
    v1[ml_layer] = choosen_id
    v2[ml_layer] = choosen_id
    bmesh.update_edit_mesh(mesh)



#=========#=========#=========#=========#=========#=========#=========#=========
# MESH MODIFICATION
#=========#=========#=========#=========#=========#=========#=========#=========

def set_centers_at_zero():
    lines =[]
    lines.append("=== set 'Center' vertices at x = 0 ")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    modifs = 0
    for v in bm.verts:
        if v[ml_layer] == ENUM.CENTER:
            if v.co.x != 0:
                v.co.x = 0
                modifs += 1
    lines.append(f"{modifs} modifications made")
    utils.alert(lines)
    print("\n".join(lines))
    bmesh.update_edit_mesh(mesh)
    return

def symetrize_coordinates(co1, co2, mode): # if active: co1 is active
    if mode == ENUM.AVERAGE:
        co = (utils.mirror(co1) + co2) / 2
        co1 = utils.mirror(co)
        co2 = co
    elif mode == ENUM.XNEGATIVE:
        if co1.x < co2.x:
            co2 = utils.mirror(co1)
        else:
            co1 = utils.mirror(co2)
    elif mode == ENUM.XPOSITIVE:
        if co1.x > co2.x:
            co2 = utils.mirror(co1)
        else:
            co1 = utils.mirror(co2)
    elif mode == ENUM.ACTIVE:
        co2 = utils.mirror(co1)
    return co1, co2

def symetrize_pair(mode=ENUM.ACTIVE):
    msg = f"=== symetrize pair ==="
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    selection = [v for v in bm.verts if v.select]
    if len(selection) != 2:
        utils.alert("Need 2 selected vertives, no less, no more.")
        return
    active = bm.select_history.active
    if active:
        selected = [v for v in selection if v != active][0]
    else:
        active, selected = selection

    active.co, selected.co = symetrize_coordinates(active.co, selected.co, mode)

    if active[ml_layer] >= ENUM.FIRSTPAIR:
        pair_id = active[ml_layer]
    elif selected[ml_layer] >= ENUM.FIRSTPAIR:
        pair_id = selected[ml_layer]
    else:
        pair_id = get_available_pair_id(bm, ml_layer)

    active[ml_layer]   = pair_id
    selected[ml_layer] = pair_id

    msg += f"id {pair_id}"
    print(msg)

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode=objmode)


def symetrize(mode=ENUM.XNEGATIVE):
    print("=== Symetrize mesh ")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return

    groups = {}
    for v in bm.verts:
        bid = v[ml_layer]
        if bid >= ENUM.FIRSTPAIR:
            groups.setdefault(bid, []).append(v)

    pairs = [g for g in groups.values() if len(g) == 2]
    broken = [g for g in groups.values() if len(g) != 2]
    not_binom = sum(1 for v in bm.verts if v[ml_layer] < ENUM.FIRSTPAIR)

    print(f"{not_binom} vertices not in a pair (ignore, center or unset)")
    print(f"{len(pairs)} correctly paired")
    print(f"{len(broken)} binom ids with a wrong vertex count (skipped)")

    modifications = 0
    for v1, v2 in pairs:
        co1, co2 = symetrize_coordinates(v1.co, v2.co, mode)
        if v1.co != co1 or v2.co != co2:
            modifications += 1
        v1.co = co1
        v2.co = co2

    print(f"{modifications} modifications made")

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode=objmode)


#=========#=========#=========#=========#=========#=========#=========#=========
# NEW GETTERS
#=========#=========#=========#=========#=========#=========#=========#=========

def get_centers_by_attribute(bm, ml_layer):
    return [v for v in bm.verts if v[ml_layer] == ENUM.CENTER]
 
def get_centers_by_geometry(bm, threshold=1e-4):
    exact = set()
    near  = set()
    for v in bm.verts:
        dist = abs(v.co.x)
        if dist == 0.0:
            exact.add(v)
        elif dist <= threshold:
            near.add(v)
    return {0.0: exact, threshold: near}

# grouped by number of overlapping vertices
def get_overlapping_by_geometry(bm, threshold=1e-4, tree=None, pair_twist=False):
    if tree == None:
        refresh_indices(bm)
        tree = build_tree(bm)
    exact = dict() # {neighbor count: set of verts}
    near  = dict() # same
    for v in bm.verts:
        exact_ = set()
        near_  = set()
        co = v.co if not pair_twist else Vector((-v.co.x, v.co.y, v.co.z))
        res = tree.find_range(co, threshold)
        for _pos, idx, dst in res:
            if v.index == idx:
                continue
            other = bm.verts[idx]
            if dst == 0:
                exact_.add(other)
            else:
                near_.add(other)
        exact_len = len(exact_)
        near_len  = len(near_)
        exact.setdefault(exact_len, set()).add(v)
        near.setdefault(near_len, set()).add(v)
    return {0.0: exact, threshold: near}

def get_pairs_by_geometry(bm, threshold=1e-4, tree=None):
    return get_overlapping_by_geometry(bm, threshold, tree, True)





#=========#=========#=========#=========#=========#=========#=========#=========
# ALALYZE
#=========#=========#=========#=========#=========#=========#=========#=========


def bucketize_for_center(bm, threshold=1e-4):
    bucket = {0.0: set(), threshold: set(), float("inf"): set()}
    for v in bm.verts:
        dist = abs(v.co.x)
        for thr, verts in bucket.items():
            if dist <= thr:
                verts.add(v)
                break
    return bucket

def bucketize_for_overlapping(bm, threshold=1e-4):
    bucket = {0.0: set(), threshold: set(), float("inf"): set()}
    refresh_indices(bm)
    tree = build_tree(bm)
    for v in bm.verts:
        dist = float("inf")
        for _co, idx, d in tree.find_range(v.co, threshold):
            if idx == v.index:
                continue
            if d == 0.0:
                dist = 0.0
                break
            dist = min(dist, d)
        for thr, verts in bucket.items():
            if dist <= thr:
                verts.add(v)
                break
    return bucket

def bucketize_for_pairs(bm, threshold=1e-4):
    bucket = {0.0: set(), threshold: set(), float("inf"): set()}
    refresh_indices(bm)
    tree = build_tree(bm)
    for v in bm.verts:
        _other, gap, _yxz = nearest_mirror(bm, tree, v)
        for thr, verts in bucket.items():
            if gap <= thr and v != _other:
                verts.add(v)
                break
    return bucket

def compare_buckets(bucketA, bucketB):
    zero, thr, inf = bucketA.keys()
    verticesA = bucketA[zero] | bucketA[thr]
    verticesB = bucketB[zero] | bucketB[thr]
    common_vertices = verticesA & verticesB
    return list(common_vertices)




def analyze_attribute(threshold=1e-4):
    logs = []
    logs.append("=== Analyze Linkage ===")

    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not obj:
        utils.alert(logs)
        print("\n".join(logs))
        return

    # Processing

    bm.verts.ensure_lookup_table()

    vertices = {}
    for v in bm.verts:
        id = v[ml_layer]
        if id < ENUM.IGNORE:
            id = "OTHER"
        if id not in vertices:
            vertices[id] = []
        vertices[id].append(v)

    # 'Center'
    centers = vertices.get(ENUM.CENTER, [])
    mislocated_centers = []
    for v in centers:
        if abs(v.co.x) > threshold:
            mislocated_centers.append(v)

    # 'Pair'
    pairs = {k: v for k, v in vertices.items() if k >= ENUM.FIRSTPAIR}
    not_dual_pairs = []
    mislocated_pairs = []
    for id, verts in pairs.items():
        if len(verts) != 2:
            not_dual_pairs += verts
            continue
        v1, v2 = verts
        dx = abs(v1.co.x + v2.co.x)
        dy = abs(v1.co.y - v2.co.y)
        dz = abs(v1.co.z - v2.co.z)
        if dx >= threshold or dy >= threshold or dz >= threshold:
            mislocated_pairs.extend(verts)

    # 'Unset'
    unsets = vertices.get(ENUM.UNSET, [])

    # 'Ignore'
    ignores = vertices.get(ENUM.IGNORE, [])

    # other
    others = vertices.get("OTHER", [])

    # Analyze and deduce

    ctr_len = len(centers)
    par_len = len(pairs)
    uns_len = len(unsets)
    ign_len = len(ignores)
    oth_len = len(ignores)

    mis_ctr_len = len(mislocated_centers)
    mis_par_len = len(mislocated_pairs)

    brk_par_len = len(not_dual_pairs)

    all_set = len(bm.verts) == ctr_len + par_len + ign_len


    if all_set and not mis_ctr_len and not mis_par_len:
        logs.append("Mesh is very sane")
    else:
        logs.append("Warning")
        if mis_ctr_len:
            logs.append(f"{mis_ctr_len} mislocated 'Center' vertices")
        if mis_par_len:
            logs.append(f"{mis_par_len} mislocated 'Pair' vertices")
        if brk_par_len:
            logs.append(f"{brk_par_len} broken 'Pair' vertices")
        if oth_len:
            logs.append(f"{oth_len} undefined vertices...")

    logs.append(f"{ctr_len} 'Center' vertices")
    logs.append(f"{par_len} 'Pair' vertices")
    logs.append(f"{uns_len} 'Unset' vertices")
    logs.append(f"{ign_len} 'Ignore' vertices")
    logs.append(f"{oth_len} undefined vertices")

    utils.alert(logs)
    print("\n".join(logs))



def analyze_geometry(threshold=1e-4):
    logs = []

    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not obj:
        utils.alert(logs)
        print("\n".join(logs))
        return

    def mag(x):
        return floor(log10(abs(x))) if x != 0 else 0

    bm.verts.ensure_lookup_table()
    total = len(bm.verts)

    # Processing

    o_bkt = bucketize_for_overlapping(bm, threshold)
    o_zero = o_bkt[0]
    o_near = o_bkt[threshold]
    o_zero_len = len(o_zero)
    o_near_len = len(o_near)
    o_len = o_zero_len + o_near_len
    no_overlap = o_len == 0

    c_bkt = bucketize_for_center(bm, threshold)
    c_zero = c_bkt[0]
    c_near = c_bkt[threshold]
    c_zero_len = len(c_zero)
    c_near_len = len(c_near)
    c_len = c_zero_len + c_near_len
    no_center = c_len == 0

    p_bkt = bucketize_for_pairs(bm, threshold)
    p_zero = p_bkt[0]
    p_near = p_bkt[threshold]
    p_zero_len = len(p_zero)
    p_near_len = len(p_near)
    p_len = p_zero_len + p_near_len
    no_pair = p_len == 0

    undefined_vertices = len(bm.verts) - c_len - p_len

    overlapping_center = compare_buckets(o_bkt, c_bkt)
    overlapping_pair = compare_buckets(o_bkt, p_bkt)
    center_and_pair = compare_buckets(c_bkt, p_bkt)

    # Analyze and deduce

    o_c_len = len(overlapping_center)
    o_p_len = len(overlapping_pair)
    c_p_len = len(center_and_pair)
    no_ambiguities = o_c_len + o_p_len + c_p_len == 0
    perfect_positionning = o_near_len + c_near_len + p_near_len == 0


    logs.append("\n=== Analyze Mesh ===")
    logs.append(f"{total} vertices\n")
    logs.append(f"Used threshold precision: {mag(threshold)}")
    logs.append("")

    if no_overlap and not no_pair and not undefined_vertices and no_ambiguities:
        if perfect_positionning:
            logs.append("Mesh is very sane!")
            logs.append("✓ No overlaps")
            logs.append("✓ No ambigute vertex (ie both 'Pair' and 'Center' candidate)")
            logs.append("✓ 'Pairs' candidates at perfect mirror locations")
        else:
            logs.append(f"Mesh is sane for threshold {threshold}")
            logs.append("✓ No overlaps")
            logs.append("✓ No ambigous vertex (ie both 'Pair' and 'Center' candidate)")
            logs.append("✓ 'Pairs' candidates at perfect mirror locations")
    else:
        logs.append("Warning")
        if undefined_vertices:
            logs.append(f"{undefined_vertices} vertices neiter 'Pairs' nor 'Center' candidate")
        if o_len:
            logs.append(f"{o_len} overlapping vertices, {o_zero_len} perfectly overlapping")
        if o_c_len:
            logs.append(f"{o_c_len} overlapping 'Center' candidates")
        if o_p_len:
            logs.append(f"{o_p_len} overlapping 'Pair' candidates")
        if c_p_len:
            logs.append(f"{c_p_len} Both 'Center' and 'Pair' candidates")
    logs.append("")

    logs.append(f"{o_len} overlapping vertices")
    logs.append(f"{c_len} 'Center' candidates")
    logs.append(f"{p_len} 'Pair' candidates")

    utils.alert(logs)
    print("\n".join(logs))
    bmesh.update_edit_mesh(mesh)



#=========#=========#=========#=========#=========#=========#=========#=========
# AUTOMATIC SET
#=========#=========#=========#=========#=========#=========#=========#=========

def set_up_mesh_attribute(threshold=1e-4):
    logs = []
    logs.append("=== set up mesh attribute ===")

    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not obj:
        print("No object found...")
        return

    refresh_indices(bm)
    tree = build_tree(bm)

    # Overlapping
    overlap_bucket = bucketize_for_overlapping(bm, threshold)
    overlap = overlap_bucket[0] | overlap_bucket[threshold]
    for v in overlap:
        v[ml_layer] = ENUM.IGNORE

    # reset all to 'Unset' except 'Ignore'
    verts = [v for v in bm.verts if v[ml_layer] != ENUM.IGNORE]
    for v in verts:
        v[ml_layer] = ENUM.UNSET

    # set 'Center' (takes over 'Pair' if ambiguity)
    center_bucket = bucketize_for_center(bm, threshold)
    centers = center_bucket[0] | center_bucket[threshold]
    for v in centers:
        if v[ml_layer] == ENUM.UNSET:
            v[ml_layer] = ENUM.CENTER

    # set 'Pair'
    verts = [v for v in verts if v[ml_layer] == ENUM.UNSET]
    # takes the first mirror verex, but should not be more:
    # we ignored overlapping vertices
    refresh_indices(bm)
    tree = build_tree(bm)
    pair_id = ENUM.FIRSTPAIR
    for v in verts:
        if v[ml_layer] == ENUM.UNSET:
            other, gap, _xyz = nearest_mirror(bm, tree, v)
            if gap <= threshold:
                v[ml_layer]     = pair_id
                other[ml_layer] = pair_id
                pair_id += 1

    # Logs
    id_cnt = pair_id - 1
    pair_cnt = sum(1 for v in bm.verts if v[ml_layer] >= ENUM.FIRSTPAIR)
    cntr_cnt = sum(1 for v in bm.verts if v[ml_layer] == ENUM.CENTER)
    unst_cnt = sum(1 for v in bm.verts if v[ml_layer] == ENUM.UNSET)
    ignr_cnt = sum(1 for v in bm.verts if v[ml_layer] == ENUM.IGNORE)
    ok_symbol = "(correct)" if id_cnt * 2 == pair_cnt else "incorrect count!"
    logs.append(f"{id_cnt} pair ids for {pair_cnt} 'Pair' vertices {ok_symbol}")
    logs.append(f"{cntr_cnt} 'Center'")
    logs.append(f"{unst_cnt} 'Unset'")
    logs.append(f"{ignr_cnt} 'Ignore' vertices")

    if overlap:
        for v in bm.verts:
            v.select_set(v in overlap)
        logs.append(f"Warning: {len(overlap)} overlapping vertices detected and selected.")

    utils.alert(logs)
    print("\n".join(logs))

    bmesh.update_edit_mesh(mesh)



#=========#=========#=========#=========#=========#=========#=========#=========
# BUILD FROM SEMI MESH
#=========#=========#=========#=========#=========#=========#=========#=========

def build_sym_from_semi_mesh(merge_threshold=1e-4):
    print("=== build sym from semi mesh BEGIN ===")

    print("get bmesh stuff")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return

    print("bmesh ops duplicate")
    orig_verts = list(bm.verts)
    orig_faces = list(bm.faces)
    dup_res = bmesh.ops.duplicate(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces))
    vert_map = dup_res["vert_map"] # orig and dup
    face_map = dup_res["face_map"] # orig and dup

    print("set pair ids and mirror")
    # set pair & mirror
    i = 0
    for v in orig_verts:
        # set pair
        pair = vert_map[v]
        v[ml_layer] = pair[ml_layer] = i
        i += 1
        # mirror
        pair.co.x *= -1.0

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

    print("check pairs")

    print("=== build sym from semi mesh END ===")




