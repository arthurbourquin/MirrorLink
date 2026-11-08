# python
from math import floor, log10

# Blender
import bpy
import bmesh

# Custom
from .core import BaseOperator, register_class
from . import utils
from .utils import ATT










#=========#=========#=========#=========#=========#=========#=========#=========
# MARK: SELECTION
#=========#=========#=========#=========#=========#=========#=========#=========





# MARK: op





# GEOMETRY BASED

@register_class
class SelectOverlappingVertices(BaseOperator):
    bl_description =  "Select all overlapping vertices\n"
    bl_description += "(regardless of attribute)"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
        if not ml_layer: return
        tree = utils.build_tree(bm.verts)
        overlaps = utils.get_overlapping(bm, bm.verts, tree, threshold)
        for v in overlaps:
            v.select_set(True)
        bm.select_flush_mode()
        bmesh.update_edit_mesh(mesh)



@register_class
class SelectCenterVertices(BaseOperator):
    bl_description =  "Select all vertices at center\n"
    bl_description += "(regardless of attribute)"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
        if not ml_layer: return
        for v in bm.verts:
            if abs(v.co.x) < threshold:
                v.select_set(True)
            else:
                v.select_set(False)
        bm.select_flush_mode()
        bmesh.update_edit_mesh(mesh)



# ATTRIBUTE BASED

def select_by_attribute_value(att_val):
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    for v in bm.verts:
        v_att_val = min(v[ml_layer], ATT.FIRSTPAIR)
        if att_val == v_att_val:
            v.select_set(True)
        else:
            v.select_set(False)
    bm.select_flush_mode()
    bmesh.update_edit_mesh(mesh)



@register_class
class SelectMarkedUnset(BaseOperator):
    def run(self, context):
        select_by_attribute_value(ATT.UNSET)

@register_class
class SelectMarkedIgnore(BaseOperator):
    def run(self, context):
        select_by_attribute_value(ATT.IGNORE)

@register_class
class SelectMarkedPair(BaseOperator):
    def run(self, context):
        select_by_attribute_value(ATT.FIRSTPAIR)

@register_class
class SelectMarkedCenter(BaseOperator):
    def run(self, context):
        select_by_attribute_value(ATT.CENTER)










#=========#=========#=========#=========#=========#=========#=========#=========
# MARK: SET
#=========#=========#=========#=========#=========#=========#=========#=========





# MARK: op





def set_selected(attribute_value):
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return
    for v in bm.verts:
        if v.select:
            v[ml_layer] = attribute_value

@register_class
class SetSelectedToIgnore(BaseOperator):
    def run(self, context):
        set_selected(ATT.IGNORE)

@register_class
class SetSelectedToUnset(BaseOperator):
    def run(self, context):
        set_selected(ATT.UNSET)

@register_class
class SymetrizePair(BaseOperator):
    bl_description = "Set selected to 'Pair'\n"
    bl_description += "Must have exactely 2 selected vertices\n"
    bl_description += "- Vertices will have the same unique 'Pair' ID\n"
    def run(self, context):
        mode = int(context.scene.mirrorlink_pair_2_verts_mode)
        obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
        if not ml_layer: return
        # check selection
        selection = [v for v in bm.verts if v.select]
        if len(selection) != 2:
            utils.alert("Need 2 selected vertives, no less, no more.")
            return
        # set active if active and selected
        act = bm.select_history.active
        if act: sel = [v for v in selection if v != act][0]
        else:   act, sel = selection
        # set coordinates
        if mode != utils.ENUM.NONE:
            act.co, sel.co = utils.symetrize_coordinates(act.co, sel.co, mode)
        # get & set pid
        if utils.is_pair(act[ml_layer]):   pid = act[ml_layer]
        elif utils.is_pair(sel[ml_layer]): pid = sel[ml_layer]
        else:                              pid = utils.get_available_pair_id(bm, ml_layer)
        act[ml_layer] = pid
        sel[ml_layer] = pid
        #
        bmesh.update_edit_mesh(mesh)
        bpy.ops.object.mode_set(mode=objmode)


@register_class
class SetSelectedToCenter(BaseOperator):
    def run(self, context):
        mode = int(context.scene.mirrorlink_set_center_mode)
        print(f"Set Selected To 'Center', mode {"MOVE" if mode==utils.ENUM.MOVE else "NONE" if mode==utils.ENUM.NONE else "?"}")
        obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
        if not ml_layer: return
        verts = [v for v in bm.verts if v.select]
        for v in verts:
            v[ml_layer] = ATT.CENTER
            if mode == utils.ENUM.MOVE:
                v.co.x = 0
        bmesh.update_edit_mesh(mesh)










#=========#=========#=========#=========#=========#=========#=========#=========
# MARK: MESH MODIF
#=========#=========#=========#=========#=========#=========#=========#=========





# MARK: op





@register_class
class SetCentersAtZero(BaseOperator):
    bl_description = "Set 'Center' vertices à x = 0"
    def run(self, context):
        obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
        if not ml_layer: return
        for v in [vtx for vtx in bm.verts if vtx[ml_layer] == ATT.CENTER]:
            v.co.x = 0
        bmesh.update_edit_mesh(mesh)



@register_class
class RestoreMesh(BaseOperator):
    bl_description = "Symetrize * the whole mesh *\n"
    bl_description += "Walk the mesh and\n"
    bl_description += "- for each 'Pair' symetrize both vertices\n"
    bl_description += "- leave 'Center', 'Unset' and 'Ignore' vertices untouched"
    def run(self, context):
        source_mode = int(context.scene.mirrorlink_restore_source_mode)
        select_mode = int(context.scene.mirrorlink_restore_select_mode)
        obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
        if not obj: return
        # 'Pair'
        all_pairs = [v for v in bm.verts if utils.is_pair(v[ml_layer])]
        pair_dict = utils.group_verts_by_pid(all_pairs, ml_layer)
        valid_pairs = [pair for pair in pair_dict.values() if len(pair) == 2]
        for v1, v2 in valid_pairs:
            co1, co2 = utils.symetrize_coordinates(v1.co, v2.co, source_mode)
            if select_mode == utils.ENUM.ALL:
                v1.co = co1
                v2.co = co2
            elif select_mode == utils.ENUM.SELECTED:
                if v1.select: v1.co = co1
                if v2.select: v2.co = co2
            else:
                print("Unknown mode in Restore Mesh")
        # 'Center'
        centers = [v for v in bm.verts if utils.is_center(v[ml_layer])]
        for v in centers:
            if select_mode == utils.ENUM.ALL:
                v.co.x = 0
            elif select_mode == utils.ENUM.SELECTED:
                if v.select: v.co.x = 0
            else:
                print("Unknown mode in Restore Mesh")
        bmesh.update_edit_mesh(mesh)
        bpy.ops.object.mode_set(mode=objmode)










#=========#=========#=========#=========#=========#=========#=========#=========
# MARK: SCAN / SET
#=========#=========#=========#=========#=========#=========#=========#=========





# MARK: fn





def scan_mesh(threshold=1e-4, mode=utils.ENUM.REPORT):
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not obj: return

    logs = []
    if mode == utils.ENUM.REPORT:   logs.append("Report")
    elif mode == utils.ENUM.SELECT: logs.append("Selection")
    elif mode == utils.ENUM.SET:    logs.append("Set Mesh")
    else:                           raise AssertionError("Unknown mode for mesh scan")
    logs[-1] += f", precision {utils.mag(threshold)}"
    logs.append("")

    ignored = {v for v in bm.verts if utils.is_ignore(v[ml_layer])}
    unsets  = {v for v in bm.verts if utils.is_unset(v[ml_layer])}
    pairs   = {v for v in bm.verts if utils.is_pair(v[ml_layer])}
    centers = {v for v in bm.verts if utils.is_center(v[ml_layer])}

    # Attribute analysis
    broken_pairs, mislocated_pairs = utils.get_bad_pairs(pairs, ml_layer, threshold)
    mislocated_centers = {v for v in centers if abs(v.co.x) > threshold}

    # Geometry analysis
    tree = utils.build_tree(bm.verts)
    overlapping = utils.get_overlapping(bm, bm.verts, tree, threshold)
    unsets_overlapping = utils.get_overlapping(bm, unsets, tree, threshold)
    pair_candidates_set_of_tuples = utils.get_pairs_candidates(bm, unsets, tree, threshold)
    pair_candidates = {v for pair in pair_candidates_set_of_tuples for v in pair}
    center_candidates = utils.get_center_candidates(unsets, threshold)
    center_candidates = center_candidates - (pair_candidates | unsets_overlapping)
    unsets_erratics = unsets - (pair_candidates | center_candidates)

    # Analyze and deduce
    def pc(n, tot): return"?%"if tot==0 else"0%"if n==0 else"100%"if n==tot else f"~{100*n/tot:.0f}%"
    total_len   = len(bm.verts)
    ignored_len = len(ignored)
    unsets_len  = len(unsets)
    pairs_len   = len(pairs)

    broken_pairs_len = len(broken_pairs)
    mislocated_pairs_len = len(mislocated_pairs)

    centers_len = len (centers)
    mislocated_centers_len = len(mislocated_centers)

    sane_pair_candidates_len = len(pair_candidates)
    sane_center_candidates_len = len(center_candidates)
    unsets_erratics_len = len(unsets_erratics)

    overlapping_len = len(overlapping)

    logs.append(f"{total_len} vertices")
    logs.append("")
    logs.append(f"{pairs_len} 'Pairs'")
    logs.append(f"• {mislocated_pairs_len} mislocated")
    logs.append(f"• {broken_pairs_len} broken")
    logs.append("")
    logs.append(f"{centers_len} 'Center'")
    logs.append(f"• {mislocated_centers_len} mislocated")
    logs.append("")
    logs.append(f"{unsets_len} 'Unset'")
    logs.append(f"• {sane_pair_candidates_len} 'Pair' candidates")
    logs.append(f"• {sane_center_candidates_len} 'Center' candidates")
    logs.append(f"• {unsets_erratics_len} erratics")
    logs.append("")
    logs.append(f"{ignored_len} 'Ignore'")
    logs.append("")
    logs.append(f"{overlapping_len} overlapping vertices in mesh")


    # selection

    if mode == utils.ENUM.REPORT:
        utils.alert(logs)    
    elif mode == utils.ENUM.SET:
        # 'Pair'
        pid = utils.pack_pid(bm, ml_layer, True)
        for pair in pair_candidates_set_of_tuples:
            v1, v2 = pair
            v1[ml_layer] = v2[ml_layer] = pid
            pid += 1
        # 'Center'
        for v in center_candidates:
            v[ml_layer] = ATT.CENTER
            v.co.x = 0
    elif mode == utils.ENUM.SELECT:
        bm.select_mode = {'VERT'}
        for v in bm.verts:
            v.select_set(False)
        for v in overlapping | broken_pairs | mislocated_pairs | mislocated_centers:
            print(v.index)
            v.select_set(True)
        bm.select_flush_mode()
    else:
        raise AssertionError("Unknown mode for mesh scan")

    bmesh.update_edit_mesh(mesh)
    if mode == utils.ENUM.REPORT:
        bpy.ops.object.mode_set(mode=objmode)

    print("\n".join(logs))




# MARK: op





@register_class
class ScanMeshReport(BaseOperator):
    bl_description =  "Scan Mesh and report (no modifications)\n"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        scan_mesh(threshold, utils.ENUM.REPORT)

@register_class
class ScanMeshSelect(BaseOperator):
    bl_description =  "Scan Mesh and select bad elements\n"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        scan_mesh(threshold, utils.ENUM.SELECT)

@register_class
class ScanMeshSet(BaseOperator):
    bl_description  = "Scan the mesh and set up the attribute.\n"
    bl_description += "Only 'Unset' vertices will be modified"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        scan_mesh(threshold, utils.ENUM.SET)