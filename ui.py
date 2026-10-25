import bpy
from .core import register_class



@register_class
class MIRRORLINK_PT_main(bpy.types.Panel):
    bl_label = "MirrorLink"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MirrorLink"

    def draw(self, context):
        layout = self.layout
        
        layout.prop(context.scene, "mirrorlink_precision_exponent")

        layout.label(text="")
        layout.label(text="MESH SCAN")
        row = layout.row(align=True)
        row.scale_y = 2
        row.operator("mirrorlink.scan_mesh_report", text="Report")
        row.operator("mirrorlink.scan_mesh_select", text="Select")
        row.operator("mirrorlink.scan_mesh_set",    text="Set!")


        layout.label(text="")
        layout.label(text="SELECT")
        row = layout.row(align=True)
        row.operator("mirrorlink.select_marked_ignore", text="'Ignore'")
        row.operator("mirrorlink.select_marked_unset",  text="'Unset'")
        row.operator("mirrorlink.select_marked_pair",   text="'Pairs'")
        row.operator("mirrorlink.select_marked_center", text="'Center'")
        row = layout.row(align=True)
        row.operator("mirrorlink.select_overlapping_vertices", text="overlapping")
        row.operator("mirrorlink.select_center_vertices",      text="at center")



        layout.label(text="")
        layout.label(text="MODIFY")
        # Mark 'Ignore' / 'Unset'
        row = layout.row(align=True)
        box_lft = row.box().column(align=True)
        box_rgt = row.box().column(align=True)

        btn = box_lft.column(align=True)
        btn.scale_y = 2
        btn.operator("mirrorlink.set_selected_to_ignore", text="Mark 'Ignore'")

        btn = box_rgt.column(align=True)
        btn.scale_y = 2
        btn.operator("mirrorlink.set_selected_to_unset", text="Mark 'Unset'")

        # Mark 'Pair' / 'Center'
        row = layout.row(align=True)
        box_lft = row.box().column(align=True)
        box_rgt = row.box().column(align=True)

        box_lft.prop(context.scene, "mirrorlink_pair_2_verts_mode", text="")
        btn = box_lft.column(align=True)
        btn.scale_y = 2
        btn.operator("mirrorlink.symetrize_pair", text="'Pair' it")

        box_rgt.prop(context.scene, "mirrorlink_set_center_mode", text="")
        btn = box_rgt.column(align=True)
        btn.scale_y = 2
        btn.operator("mirrorlink.set_selected_to_center", text="Mark 'Center'")



        layout.label(text="")
        col = layout.column(align=True)
        col.prop(context.scene, "mirrorlink_pair_mesh", text="")
        col.operator("mirrorlink.restore_mesh", text="Restore Mesh")





# · • – — ← → ↑ ↓ ○ ● □ ■ △ ◇ ± × ÷ ≠ ≤ ≥ ≈ ° Ø × ✓
