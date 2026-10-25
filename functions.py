import bpy
import bmesh
from math import floor, log10
from mathutils import Vector
from mathutils.kdtree import KDTree

from . import utils
from .utils import ENUM, ATT



#=========#=========#=========#=========#=========#=========#=========#=========
# SCAN & AUTOMATIC SETUP
#=========#=========#=========#=========#=========#=========#=========#=========

def scan_mesh(threshold=1e-4, mode=ENUM.REPORT):
    logs = []
    def mag(x): return floor(log10(abs(x))) if x != 0 else 0
    logs.append(f"\n=== Scan Mesh ===")
    fmode = "Report" if mode==ENUM.REPORT else "Select" if mode==ENUM.SELECT else "Set" if mode==ENUM.SET else "Unknown"
    logs.append(f"At precision {mag(threshold)}, in {fmode} mode")
    logs.append("")

    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not obj: return

    ignored = [v for v in bm.verts if utils.is_ignore(v[ml_layer])]
    unsets  = [v for v in bm.verts if utils.is_unset(v[ml_layer])]
    pairs   = [v for v in bm.verts if utils.is_pair(v[ml_layer])]
    centers = [v for v in bm.verts if utils.is_center(v[ml_layer])]

    # Attribute analysis
    broken_pairs, mislocated_pairs = utils.get_bad_pairs(pairs, ml_layer, threshold)
    mislocated_centers = [v for v in centers if abs(v.co.x) > threshold]

    # Geometry analysis
    tree = utils.build_tree(bm.verts)
    overlapping = utils.get_overlapping(bm, unsets, tree, threshold)
    sane_pair_candidates_pid = utils.get_pairs_candidates(bm, unsets, tree, threshold)
    sane_pair_candidates = {v for pair in sane_pair_candidates_pid for v in pair}
    center_candidates = utils.get_center_candidates(unsets, threshold)
    sane_center_candidates = center_candidates - (sane_pair_candidates | overlapping)
    broken = set(unsets) - (sane_pair_candidates | sane_center_candidates)

    # Analyze and deduce
    def pc(n, tot): return "?%" if tot == 0 else "0%" if n == 0 else "100%" if n == tot else f"~{100 * n / tot:.0f}%"
    total_len = len(bm.verts)
    ignored_len = len(ignored)
    unsets_len = len(unsets)
    pairs_len = len(pairs)
    broken_pairs_len = len(broken_pairs)
    mislocated_pairs_len = len(mislocated_pairs)
    centers_len = len (centers)
    mislocated_centers_len = len(mislocated_centers)
    overlapping_len = len(overlapping)
    sane_pair_candidates_len = len(sane_pair_candidates)
    sane_center_candidates_len = len(sane_center_candidates)
    broken_len = len(broken)
    logs.append(f"{total_len} vertices")
    logs.append(f"{ignored_len} 'Ignore', ({pc(ignored_len, total_len)})")
    logs.append(f"{unsets_len} 'Unset', ({pc(unsets_len, total_len)})")
    logs.append(f"{pairs_len} 'Pair', ({pc(pairs_len, total_len)}), {mislocated_pairs_len} mislocated, {broken_pairs_len} broken")
    logs.append(f"{centers_len} 'Center', ({pc(centers_len, total_len)}), {mislocated_centers_len} mislocated")
    logs.append("")
    logs.append("'Unset' vertices:")
    logs.append(f"{overlapping_len} overlapping vertices, {pc(overlapping_len, total_len)}")
    logs.append(f"{sane_pair_candidates_len} 'Pair' candidates, {pc(sane_pair_candidates_len, total_len)}")
    logs.append(f"{sane_center_candidates_len} 'Center' candidates, {pc(sane_center_candidates_len, total_len)}")
    logs.append(f"{broken_len} considered broken, {pc(broken_len, total_len)}")

    # selection

    if mode == ENUM.REPORT:
        utils.alert(logs)    
    elif mode == ENUM.SET:
        # 'Pair'
        pid = utils.pack_pid(bm, ml_layer, True)
        for pair in sane_pair_candidates_pid:
            v1, v2 = pair
            v1[ml_layer] = v2[ml_layer] = pid
            pid += 1
        # 'Center'
        for v in sane_center_candidates:
            v[ml_layer] = ATT.CENTER
            v.co.x = 0
    elif mode == ENUM.SELECT:
        for v in bm.verts:
            v.select_set(False)
        for v in broken | set(broken_pairs):
            v.select_set(True)
        bm.select_flush_mode()
    else:
        print("Unknown mode...")

    bmesh.update_edit_mesh(mesh)
    if mode == ENUM.REPORT:
        bpy.ops.object.mode_set(mode=objmode)

    print("\n".join(logs))