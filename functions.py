import bpy
import bmesh
from math import floor, log10
from mathutils import Vector
from mathutils.kdtree import KDTree

from . import utils
from .utils import ENUM

FIRSTBINOM = 1
CENTER     = 0
UNSET      = -1
IGNORE     = -2

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

    # Écart par axe : 0 partout si le miroir est parfait
    dx = v.co.x + other.co.x     # v.x vs -other.x
    dy = v.co.y - other.co.y
    dz = v.co.z - other.co.z
    return other, gap, (dx, dy, dz)



#=========#=========#=========#=========#=========#=========#=========#=========
# FUNCTIONS
#=========#=========#=========#=========#=========#=========#=========#=========

#-------------------------------------------------------------------------------
# PRINT / CHECK / LOG

def check_pairs(obj, mesh, bm, ml_layer, merge_threshold=1e-4):
    print("=== check pair BEGIN ===")

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
    print(f"single pairs: {len(bids_trans[1])}")
    print(f"dual pairs: {len(bids_trans[2])}")
    print(f"more than 3: {len(bids_trans[3])}")

    print("=== check pair END ===")




#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION (WITHOUT BINOM ID ENUM)
#=========#=========#=========#=========#=========#=========#=========#=========

def select_center_vertices(threshold):
    print("Select Center Vertices")
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
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

def select_overlapping_vertices(threshold):
    print("Select Overlapping Vertices")
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
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



#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION BY ENUM VALUE
#=========#=========#=========#=========#=========#=========#=========#=========

def select_pairs():
    print("Select Pairs")
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
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
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
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
# SET ENUM
#=========#=========#=========#=========#=========#=========#=========#=========

def set_selected(attribute_value):
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
    if not ml_layer: return
    for v in bm.verts:
        if v.select:
            v[ml_layer] = attribute_value

def set_id_to_selected_pair():
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
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

def symetrize_coordinates(co1, co2, mode):
    # if active
    # - co1 is active vertex coordinate
    # - co2 id selected vertex coordinate
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
    msg = f"=== symetrize pair "
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
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

    msg += f"id {active[ml_layer]} ==="
    print(msg)
    bmesh.update_edit_mesh(mesh)

def symetrize(mode=ENUM.XNEGATIVE):
    logs = []
    logs.append("=== Symetrize mesh ")
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
    if not ml_layer: return

    groups = {}
    for v in bm.verts:
        bid = v[ml_layer]
        if bid >= ENUM.FIRSTPAIR:
            groups.setdefault(bid, []).append(v)

    pairs = [g for g in groups.values() if len(g) == 2]
    broken = [g for g in groups.values() if len(g) != 2]
    not_binom = sum(1 for v in bm.verts if v[ml_layer] < ENUM.FIRSTPAIR)

    logs.append(f"{not_binom} vertices not in a pair (ignore, center or unset)")
    logs.append(f"{len(pairs)} correctly paired")
    logs.append(f"{len(broken)} binom ids with a wrong vertex count (skipped)")

    modifications = 0
    for v1, v2 in pairs:
        co1, co2 = symetrize_coordinates(v1.co, v2.co, mode)
        if v1.co != co1 or v2.co != co2:
            modifications += 1
        v1.co = co1
        v2.co = co2

    logs.append(f"{modifications} modifications made")

    utils.alert(logs)
    print("\n".join(logs))

    bmesh.update_edit_mesh(mesh)



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
            if gap <= thr:
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

    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
    if not obj:
        utils.alert(logs)
        print("\n".join(logs))
        return

    bm.verts.ensure_lookup_table()

    vertices = {}
    for v in bm.verts:
        id = v[ml_layer]
        if id < IGNORE:
            id = "OTHER"
        if id not in vertices:
            vertices[id] = []
        vertices[id].append(v)

    # check pairs
    pairs = {k: v for k, v in vertices.items() if k >= ENUM.FIRSTPAIR}
    not_dual_pairs = []
    not_matching_pairs = []
    for id, verts in pairs.items():
        if len(verts) != 2:
            not_dual_pairs += verts
            continue
        v1, v2 = verts
        dx = abs(v1.co.x + v2.co.x)
        dy = abs(v1.co.y - v2.co.y)
        dz = abs(v1.co.z - v2.co.z)
        if dx >= threshold or dy >= threshold or dz >= threshold:
            not_matching_pairs.extend(verts)
    pairs_ok = len(not_dual_pairs) == 0 and len(not_matching_pairs) == 0

    # check centers
    centers = vertices.get(CENTER, [])
    not_at_center = []
    for v in centers:
        if abs(v.co.x) > threshold:
            not_at_center.append(v)
    centers_ok = len(not_at_center) == 0

    # unset
    unsets = vertices.get(UNSET, [])
    nothing_unset = len(unsets) == 0

    # unset
    ignore = vertices.get(IGNORE, [])
    nothing_ignored = len(ignore) == 0

    # other
    others = vertices.get("OTHER", [])
    no_undefined = len(others) == 0

    logs.append(f"{len(bm.verts)} vertices")
    logs.append("")

    if all((pairs_ok, centers_ok, nothing_unset, no_undefined)):
        logs.append("Mesh is sane ✓")
        logs.append("")

    logs.append(f"{len(not_dual_pairs)} broken pair (pair-id for single vertex or more than 2)")
    logs.append(f"{len(not_matching_pairs)} 'Pairs' vertices misplaced")
    logs.append(f"{len(not_at_center)} 'Centers' vertices misplaced")
    logs.append(f"{len(unsets)} 'Unset' vertices")
    logs.append(f"{len(ignore)} 'Ignore' vertices")
    logs.append(f"{len(others)} undefined vertices")
    utils.alert(logs)
    print("\n".join(logs))



def analyze_geometry(threshold=1e-4):
    logs = []
    logs.append("\n=== Analyze Mesh ===")

    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
    if not obj:
        utils.alert(logs)
        print("\n".join(logs))
        return

    def mag(x):
        return floor(log10(abs(x))) if x != 0 else 0

    bm.verts.ensure_lookup_table()
    total = len(bm.verts)
    logs.append(f"{total} vertices\n")
    logs.append(f"Used threshold precision: {mag(threshold)}")
    logs.append("")

    # Overlapping
    overlap_bucket = bucketize_for_overlapping(bm, threshold)
    ovr_zero = overlap_bucket[0]
    ovr_near = overlap_bucket[threshold]
    ovr_far = overlap_bucket[float("inf")]
    ozl, onl, ofl = [len(ovr_zero), len(ovr_near), len(ovr_far)]
    if ozl + onl == 0:
        logs.append("No overlapping vertices ✓")
        logs.append("")
    else:
        logs.append("Overlapping")
        logs.append(f"{ozl + onl} vertices are considered overlapping")
        logs.append(f"{ozl} of which are exact overlaps")
        logs.append("")


    # Center
    center_bucket = bucketize_for_center(bm, threshold)
    ctr_zero = center_bucket[0]
    ctr_near = center_bucket[threshold]
    ctr_far = center_bucket[float("inf")]
    czl, cnl, cfl = [len(ctr_zero), len(ctr_near), len(ctr_far)]
    logs.append("Center")
    logs.append(f"{czl + cnl} vertices are considered at the center")
    logs.append(f"{czl} of which are exactly at x = 0")
    logs.append("")

    # Pair
    pair_bucket = bucketize_for_pairs(bm, threshold)
    pair_zero = pair_bucket[0]
    pair_near = pair_bucket[threshold]
    pair_far = pair_bucket[float("inf")]
    pzl, pnl, pfl = [len(pair_zero), len(pair_near), len(pair_far)]
    logs.append("Pair")
    logs.append(f"{pzl + pnl} vertices are considered having a match at -x")
    logs.append(f"{pzl} of which are exact match (x, y, z)")
    logs.append("")

    center_and_pairs = len(compare_buckets(center_bucket, pair_bucket))
    if center_and_pairs > 0:
        logs.append(f"{center_and_pairs} vertices are both considered pairs and center")

    utils.alert(logs)
    print("\n".join(logs))
    bmesh.update_edit_mesh(mesh)



#=========#=========#=========#=========#=========#=========#=========#=========
# AUTOMATIC SET
#=========#=========#=========#=========#=========#=========#=========#=========

def set_up_mesh_attribute(threshold=1e-9):
    logs = []
    logs.append("=== set up mesh attribute ===")

    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
    if not obj:
        print("No object found...")
        return

    refresh_indices(bm)
    tree = build_tree(bm)


    # Ignore (alread Ignore and overlapping)
    overlap_bucket = bucketize_for_overlapping(bm, threshold)
    overlap = overlap_bucket[0] | overlap_bucket[threshold]
    for v in overlap:
        v[ml_layer] = IGNORE

    # Get working vertices
    verts = [v for v in bm.verts if v[ml_layer] != IGNORE]
    for v in verts:
        v[ml_layer] = UNSET

    # Center
    center_bucket = bucketize_for_center(bm, threshold)
    centers = center_bucket[0] | center_bucket[threshold]
    for v in centers:
        v[ml_layer] = CENTER

    # Pairs 
    verts = [v for v in verts if v[ml_layer] == UNSET]
    # takes the first mirror verex, but should not be more:
    # we ignored overlapping vertices
    refresh_indices(bm)
    tree = build_tree(bm)
    pair_id = 1 # start at 1 (0 is CENTER)
    FORCEIGNORE = -3
    for v in verts:
        mv, gap, _yxz = nearest_mirror(bm, tree, v)        
        if gap > threshold: # no pair found
            v[ml_layer] = FORCEIGNORE
        else: # pair found
            if mv[ml_layer] == UNSET: # pair unset
                v[ml_layer] = mv[ml_layer] = pair_id # set pair id
                pair_id += 1
            else: # pair set: sould have mark current vertex
                if v[ml_layer] != mv[ml_layer]:
                    print("problème problème...")

    # Logs
    id_cnt = pair_id - 1
    pair_cnt = sum(1 for v in bm.verts if v[ml_layer] >= ENUM.FIRSTPAIR)
    cntr_cnt = sum(1 for v in bm.verts if v[ml_layer] == ENUM.CENTER)
    unst_cnt = sum(1 for v in bm.verts if v[ml_layer] == ENUM.UNSET)
    ignr_cnt = sum(1 for v in bm.verts if v[ml_layer] == ENUM.IGNORE)
    forc_cnt = sum(1 for v in bm.verts if v[ml_layer] == ENUM.FORCEIGNORE)
    ok_symbol = "(correct)" if id_cnt * 2 == pair_cnt else "incorrect count!"
    logs.append(f"{id_cnt} pair ids for {pair_cnt} verives set as 'Pair {ok_symbol}")
    logs.append(f"{cntr_cnt} vertices set as 'Center'")
    logs.append(f"{unst_cnt} vertices still 'Unset'")
    logs.append(f"{forc_cnt} forced as 'Ignore'")

    for v in verts:
        if v[ml_layer] == FORCEIGNORE:
            v[ml_layer] = IGNORE


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
    obj, mesh, bm, ml_layer = utils.get_bmesh_stuff()
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
    check_pairs(obj, mesh, bm, ml_layer, merge_threshold)

    print("=== build sym from semi mesh END ===")




