import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree

ATTNAME = 'pair-id'
FIRSTBINOM = 1
CENTER     = 0
UNSET      = -1
IGNORE     = -2

#=========#=========#=========#=========#=========#=========#=========#=========
# UTILITY
#=========#=========#=========#=========#=========#=========#=========#=========

def alert(message, title="Tohm Mirror Link", icon='INFO'):
    def draw(self, context):
        for line in str(message).split("\n"):
            self.layout.label(text=line)
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
# SELECTION (WITHOUT BINOM ID ATTRIBUTE)
#=========#=========#=========#=========#=========#=========#=========#=========

def select_center_vertices(threshold):
    print("Select Center Vertices")
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
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
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
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
# SELECTION BY ATTRIBUTE VALUE
#=========#=========#=========#=========#=========#=========#=========#=========

def select_pairs():
    print("Select Pairs")
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
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
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
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
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    if not ml_layer: return
    for v in bm.verts:
        if v.select:
            v[ml_layer] = attribute_value

def set_id_to_selected_pair():
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    if not ml_layer: return
    select = [v for v in bm.verts if v.select]
    if len(select) != 2:
        alert(f"{len(select)} selected vertices, require exactely two.")
        return
    v1, v2 = select
    choosen_id = min(v1[ml_layer], v2[ml_layer])
    v1[ml_layer] = choosen_id
    v2[ml_layer] = choosen_id
    bmesh.update_edit_mesh(mesh)



#=========#=========#=========#=========#=========#=========#=========#=========
# MESH MODIFICATION
#=========#=========#=========#=========#=========#=========#=========#=========

def symetrize_pair():
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    if not ml_layer: return
    select = [v for v in bm.verts if v.select]
    if len(select) != 2:
        print("set pair can only work for one active and one selected vertex")
        return
    co1 = select[0].co * Vector((-1, 1, 1))
    co2 = select[1].co
    co = (co1 + co2) / 2
    co1 = co * Vector((-1, 1, 1))
    co2 = co
    print(co1, co2)
    select[0].co = co1
    select[1].co = co2
    bmesh.update_edit_mesh(mesh)

def symetrize(mode="POSITIVE"):
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    if not ml_layer: return

    # Groupement : uniquement les vrais binoms
    groups = {}
    for v in bm.verts:
        bid = v[ml_layer]
        if bid >= FIRSTBINOM:
            groups.setdefault(bid, []).append(v)

    pairs = [g for g in groups.values() if len(g) == 2]
    broken = [g for g in groups.values() if len(g) != 2]
    not_binom = sum(1 for v in bm.verts if v[ml_layer] < FIRSTBINOM)

    print(f"{not_binom} vertices not in a pair (ignore, center or unset)")
    print(f"{len(pairs)} correctly paired")
    print(f"{len(broken)} binom ids with a wrong vertex count (skipped)")

    def mirror(co):
        return Vector((-co.x, co.y, co.z))

    if mode not in ("POSITIVE", "NEGATIVE", "AVERAGE"):
        print(f"Unrecognized mode: {mode}")
        return

    for v1, v2 in pairs:
        if mode == "AVERAGE":
            v2.co = (v2.co + mirror(v1.co)) / 2
            v1.co = mirror(v2.co)
        else:
            if mode == "POSITIVE":
                src, dst = (v1, v2) if v1.co.x > v2.co.x else (v2, v1)
            else:  # NEGATIVE
                src, dst = (v1, v2) if v1.co.x < v2.co.x else (v2, v1)
            dst.co = mirror(src.co)

    bmesh.update_edit_mesh(mesh)




#=========#=========#=========#=========#=========#=========#=========#=========
# WALKS
#=========#=========#=========#=========#=========#=========#=========#=========

def find_and_set_pairs(threshold=1e-9):
    print("=== find and set pairs ===")
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    if not obj:
        print("No object found...")
        return

    refresh_indices(bm)
    tree = build_tree(bm)

    # 0. RESET : tout redevient UNSET, sauf les IGNORE posés par l'user
    for v in bm.verts:
        if v[ml_layer] != IGNORE:
            v[ml_layer] = UNSET

    # 1. SUPERPOSÉS (parmi les UNSET) : on collecte, PUIS on marque
    overlapping = set()
    for v in bm.verts:
        if v[ml_layer] != UNSET:
            continue
        for _, idx, _ in tree.find_range(v.co, threshold):
            other = bm.verts[idx]
            if idx != v.index and other[ml_layer] == UNSET:
                overlapping.add(v)
                overlapping.add(other)
    for v in overlapping:
        v[ml_layer] = IGNORE

    # 2. APPARIEMENT : on ne regarde que ce qui est encore UNSET
    pair_id = 1
    at_center = no_partner = 0
    for v in bm.verts:
        if v[ml_layer] != UNSET:      # IGNORE, superposé, ou déjà apparié plus haut
            continue

        if abs(v.co.x) < threshold:   # centre AVANT le miroir
            v[ml_layer] = CENTER
            at_center += 1
            continue

        other, gap, _ = nearest_mirror(bm, tree, v)
        if gap < threshold and other[ml_layer] == UNSET:
            v[ml_layer] = other[ml_layer] = pair_id
            pair_id += 1
        else:
            v[ml_layer] = IGNORE
            no_partner += 1

    # 3. RAPPORT
    pairs = pair_id - 1
    ignored = sum(1 for v in bm.verts if v[ml_layer] == IGNORE)
    print(f"{pairs} pairs")
    print(f"{at_center} at center")
    print(f"{no_partner} singles")
    print(f"{ignored} ignored")
    print(f"{len(overlapping)} overlapping")

    if overlapping:
        print(f"Warning: {len(overlapping)} overlapping vertices (threshold {threshold}), selected.")
        for v in bm.verts:
            v.select_set(v in overlapping)

    bmesh.update_edit_mesh(mesh)



def analyze_mesh(threshold=1e-4):
    lines = []

    def bucketize(values):
        thresholds = {
            0.0: 0,
            threshold: 0,
            float("inf"): 0,
        }
        for val in values:
            for t in thresholds:
                if val <= t:
                    thresholds[t] += 1
                    break
        return thresholds.values()

    def pc(n):
        val = 100 * n / len(bm.verts)
        return f"{val:>3.1f}%"

    lines.append("\n=== Analyze Mesh ===")
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
    if not obj:
        lines.append("No object found...")
        alert("\n".join(lines))
        return

    bm.verts.ensure_lookup_table()
    total = len(bm.verts)
    lines.append(f"{total} vertices\n")

    # X distance
    axis_dists = [abs(v.co.x) for v in bm.verts]
    xzero, thres, inf = bucketize(axis_dists)
    lines.append("Distance to mirror (YZ plane / |x| distance)")
    lines.append(f"{xzero} ({pc(xzero)}) vertices at perfect x=0")
    lines.append(f"{thres} ({pc(thres)}) vertices below given threshold {threshold}")
    lines.append(f"{inf} ({pc(inf)}) vertices considered not to be at center")
    lines.append("\n")

    # Nearest mirrored distance
    tree = build_tree(bm)
    mirror_dists = []
    worst = []  # (dist, v_index, other_index)
    for v in bm.verts:
        other, dist, _ = nearest_mirror(bm, tree, v)
        mirror_dists.append(dist)
        worst.append((dist, v.index, other.index))
    xzero, thres, inf = bucketize(mirror_dists)
    lines.append("Distance to nearest mirror vertex")
    lines.append(f"{xzero} ({pc(xzero)}) vertices having a perfect match at -x")
    lines.append(f"{thres} ({pc(thres)}) vertices having a match at -x +/-{threshold}")
    lines.append(f"{inf} ({pc(inf)}) vertices considered not to have a match at -x")
    lines.append("\n")

    message = "\n".join(lines)
    alert(message)
    print(message)
    bmesh.update_edit_mesh(mesh)



def build_sym_from_semi_mesh(merge_threshold=1e-4):
    print("=== build sym from semi mesh BEGIN ===")

    print("get bmesh stuff")
    obj, mesh, bm, ml_layer = get_bmesh_stuff()
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




