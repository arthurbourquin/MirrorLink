import bpy
import bmesh

from . import functions
from .core import BaseOperator, register_class
from . import utils
from.utils import ENUM, ATT










#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION
#=========#=========#=========#=========#=========#=========#=========#=========

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
# SET
#=========#=========#=========#=========#=========#=========#=========#=========

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
        if mode != ENUM.NONE:
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
        print(f"Set Selected To 'Center', mode {"MOVE" if mode==ENUM.MOVE else "NONE" if mode==ENUM.NONE else "?"}")
        obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
        if not ml_layer: return
        verts = [v for v in bm.verts if v.select]
        for v in verts:
            v[ml_layer] = ATT.CENTER
            if mode == ENUM.MOVE:
                v.co.x = 0
        bmesh.update_edit_mesh(mesh)










#=========#=========#=========#=========#=========#=========#=========#=========
# MESH MODIFICATION
#=========#=========#=========#=========#=========#=========#=========#=========

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
            if select_mode == ENUM.ALL:
                v1.co = co1
                v2.co = co2
            elif select_mode == ENUM.SELECTED:
                if v1.select: v1.co = co1
                if v2.select: v2.co = co2
            else:
                print("Unknown mode in Restore Mesh")
        # 'Center'
        centers = [v for v in bm.verts if utils.is_center(v[ml_layer])]
        for v in centers:
            if select_mode == ENUM.ALL:
                v.co.x = 0
            elif select_mode == ENUM.SELECTED:
                if v.select: v.co.x = 0
            else:
                print("Unknown mode in Restore Mesh")
        bmesh.update_edit_mesh(mesh)
        bpy.ops.object.mode_set(mode=objmode)










#=========#=========#=========#=========#=========#=========#=========#=========
# SCAN
#=========#=========#=========#=========#=========#=========#=========#=========

@register_class
class ScanMeshReport(BaseOperator):
    bl_description =  "Scan Mesh and report (no modifications)\n"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.scan_mesh(threshold, ENUM.REPORT)

@register_class
class ScanMeshSelect(BaseOperator):
    bl_description =  "Scan Mesh and select bad elements\n"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.scan_mesh(threshold, ENUM.SELECT)

@register_class
class ScanMeshSet(BaseOperator):
    bl_description  = "Scan the mesh and set up the attribute.\n"
    bl_description += "Only 'Unset' vertices are modified: those identified\n"
    bl_description += "as 'Pair' or 'Center' will be set accordingly."
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.scan_mesh(threshold, ENUM.SET)