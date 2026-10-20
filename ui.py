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
        
        layout.label(text="GENERAL")
        layout.prop(context.scene, "mirrorlink_precision_exponent")

        layout.label(text="")
        layout.label(text="ANALYZE")
        row = layout.row(align=True)
        row.operator("mirrorlink.analyze_geometry", text="Geometry")
        row.operator("mirrorlink.analyze_attribute", text="Attribute")

        layout.label(text="")
        layout.label(text="SELECTION")
        row = layout.row(align=True)
        row.operator("mirrorlink.select_center_vertices", text="at center")
        row.operator("mirrorlink.select_overlapping_vertices", text="overlapping")
        row = layout.row(align=True)
        row.operator("mirrorlink.select_marked_pair", text="'Pairs'")
        row.operator("mirrorlink.select_marked_center", text="'Center'")
        row.operator("mirrorlink.select_marked_unset", text="'Unset'")
        row.operator("mirrorlink.select_marked_ignore", text="'Ignore'")

        layout.label(text="")
        layout.label(text="MODIFICATION")
        layout.label(text="Attribute")
        row = layout.row(align=True)
        row.operator("mirrorlink.set_selected_to_unset", text="'Unset'")
        row.operator("mirrorlink.set_selected_to_ignore", text="'Ignore'")

        layout.label(text="Location & Attribute")
        row = layout.row(align=True)
        row.operator("mirrorlink.set_centers_at_zero", text="Set 'Center' at x=0")
        row.scale_y = 2
        row = layout.row(align=True)
        left = row.column(align=True)
        left.prop(context.scene, "mirrorlink_pair_2_verts_mode", text="")
        e = left.row(align=True)
        e.operator("mirrorlink.symetrize_pair", text="Pair")
        e.scale_y = 3
        right = row.column(align=True)
        right.prop(context.scene, "mirrorlink_pair_mesh", text="",)
        e = right.row(align=True)
        e.operator("mirrorlink.symetrize_whole_mesh", text="Symetrize")
        e.scale_y = 3

        row = layout.row(align=True)
        row.scale_y = 2
        row.operator("mirrorlink.set_up_mesh_attribute", text="Set Up Mesh")


tolerated_chars = "· • – — ← → ↑ ↓ ○ ● □ ■ △ ◇ ± × ÷ ≠ ≤ ≥ ≈ ° Ø × ✓"


