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

        row2 = layout.row(align=True)
        col_left_2 = row2.column(align=True)
        col_left_2.operator("mirrorlink.scan_mesh_report", text="Report")
        col_left_2.operator("mirrorlink.scan_mesh_select", text="Select")
        col_right_1 = row2.column(align=True)
        col_right_1.operator("mirrorlink.scan_mesh_set", text="Set")


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


        layout.separator()
        layout.label(text="MODIFY")

        scene = context.scene

        grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=False, align=False)

        # --- Ligne 1 : boutons seuls ---
        col = grid.column(align=True)
        col.scale_y = 2
        col.operator("mirrorlink.set_selected_to_ignore", text="Mark 'Ignore'")

        col = grid.column(align=True)
        col.scale_y = 2
        col.operator("mirrorlink.set_selected_to_unset", text="Mark 'Unset'")

        # --- Ligne 2 : colonnes de 2 (menu + bouton) ---
        col = grid.column(align=True)
        col.prop(scene, "mirrorlink_pair_2_verts_mode", text="")
        sub = col.column(align=True)
        sub.scale_y = 2
        sub.operator("mirrorlink.symetrize_pair", text="'Pair' it")

        col = grid.column(align=True)
        col.prop(scene, "mirrorlink_set_center_mode", text="")
        sub = col.column(align=True)
        sub.scale_y = 2
        sub.operator("mirrorlink.set_selected_to_center", text="Mark 'Center'")



        layout.label(text="")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "mirrorlink_restore_source_mode", text="")
        row.prop(context.scene, "mirrorlink_restore_select_mode", text="")
        row = col.row(align=True)
        row.operator("mirrorlink.restore_mesh", text="Restore Mesh")
        row.scale_y = 2





# · • – — ← → ↑ ↓ ○ ● □ ■ △ ◇ ± × ÷ ≠ ≤ ≥ ≈ ° Ø × ✓
