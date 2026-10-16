import bpy
from itertools import groupby
from .core import register_me, operators


@register_me
class MIRRORLINK_PT_main(bpy.types.Panel):
    bl_label = "MirrorLink"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MirrorLink"

    def draw(self, context):
        layout = self.layout
        ops = [o for o in operators() if o.in_panel]

        for group, items in groupby(ops, key=lambda o: o.group):
            items = list(items)

            if group is None:                    # sans groupe : un bouton par ligne
                for o in items:
                    layout.operator(o.bl_idname)
                continue

            layout.label(text=group)
            cols = len(items) if len(items) <= 3 else 2    # une ligne si <= 3, sinon grille 2 colonnes
            grid = layout.grid_flow(row_major=True, columns=cols, align=True)
            for o in items:
                grid.operator(o.bl_idname, text=o.button_text or o.bl_label)
