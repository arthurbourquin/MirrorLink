import bpy


class MIRRORLINK_PT_MainPanel(bpy.types.Panel): # dit à Blender "je crée un pannel" ; MIRRORLINK_PT_ convention
    bl_label = "MirrorLink"
    bl_idname = "MIRRORLINK_PT_main_panel"

    bl_space_type = 'VIEW_3D'  # où dans Blender
    bl_region_type = 'UI'      # où dans la fenêtre (side pannel (n))
    bl_category = "MirrorLink" # nom de l'onglet dans side pannel

    def draw(self, context): # Blender appelle cette méthode pour dessiner le panneau
        layout = self.layout

        layout.operator("mirrorlink.debug")
        layout.operator("mirrorlink.set_binoms")
        layout.operator("mirrorlink.build_sym_from_semi_mesh")