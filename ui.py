import bpy
from .core import register_me


@register_me
class MIRRORLINK_PT_main(bpy.types.Panel):
    bl_label = "MirrorLink"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MirrorLink"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Selection")
        layout.operator("mirrorlink.select_center_vertices", text="Select Center Vertices")
        layout.operator("mirrorlink.select_overlapping_vertices", text="Select Overlapping Vertices")
        grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=True)
        grid.operator("mirrorlink.select_marked_pair", text="Select 'Pairs'")
        grid.operator("mirrorlink.select_marked_center", text="Select 'Center'")
        grid.operator("mirrorlink.select_marked_unset", text="Select 'Unset'")
        grid.operator("mirrorlink.select_marked_ignore", text="Select 'Ignore'")

        layout.label(text="Set Attribute For Selection")
        grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=True)
        grid.operator("mirrorlink.set_id_to_selected_pair", text="Set 'Pair'")
        grid.operator("mirrorlink.set_selected_to_center", text="Set 'Center'")
        grid.operator("mirrorlink.set_selected_to_unset", text="Set 'Unset'")
        grid.operator("mirrorlink.set_selected_to_ignore", text="Set 'Ignore'")

        layout.label(text="Mesh Modification")
        row = layout.row(align=True)
        row.scale_y = 4
        row.operator("mirrorlink.symetrize_pair", text="●-● Pair")
        row.operator("mirrorlink.symetrize_whole_mesh", text="SYMETRIZE")

        layout.label(text="Build")
        layout.operator("mirrorlink.analyze_geometry", text="Analyze Geometry")
        layout.operator("mirrorlink.analyze_attribute", text="Analyze Linkage")
        row = layout.row(align=True)
        row.scale_y = 2
        row.operator("mirrorlink.find_and_set_pairs", text="Mirror Link Mesh")


tolerated_chars = "· • – — ← → ↑ ↓ ○ ● □ ■ △ ◇ ± × ÷ ≠ ≤ ≥ ≈ ° Ø × ✓"


