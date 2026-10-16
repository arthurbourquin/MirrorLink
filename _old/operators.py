import bpy

from .. import functions


class MIRRORLINK_OT_Debug(bpy.types.Operator):
    bl_idname = "mirrorlink.debug"
    bl_label = "Debug"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        functions.debug()
        return {'FINISHED'}


class MIRRORLINK_OT_AnalyseMesh(bpy.types.Operator):
    bl_idname = "mirrorlink.analyze_mesh"
    bl_label = "Analyze Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    precision: bpy.props.IntProperty(
        name="Threshold",
        description="precision",
        default=-4,
        min=-20,
        max=20,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        select_threshold = 10 ** self.precision
        functions.analyze_mesh(select_threshold)
        return {'FINISHED'}


class MIRRORLINK_OT_SelectCenterVertices(bpy.types.Operator):
    bl_idname = "mirrorlink.select_center_vertices"
    bl_label = "Select Center Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    precision: bpy.props.IntProperty(
        name="Threshold",
        description="precision",
        default=-4,
        min=-20,
        max=20,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        select_threshold = 10 ** self.precision
        functions.select_center_vertices(select_threshold)
        return {'FINISHED'}


class MIRRORLINK_OT_SetSelectedToNonSymetric(bpy.types.Operator):
    bl_idname = "mirrorlink.set_selected_to_non_symetric"
    bl_label = "Set selected To Non Symetric"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        functions.set_selected_to_non_symetric()
        return {'FINISHED'}

class MIRRORLINK_OT_SetSelectedToCenter(bpy.types.Operator):
    bl_idname = "mirrorlink.set_selected_to_center"
    bl_label = "Set selected To Center"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        functions.set_selected_to_center()
        return {'FINISHED'}


class MIRRORLINK_OT_Mirror2SelectedVerts(bpy.types.Operator):
    bl_idname = "mirrorlink.mirror_2_selected_verts"
    bl_label = "Set Binom Pair"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        functions.mirror_2_selected_verts()
        return {'FINISHED'}



class MIRRORLINK_OT_SetBinoms(bpy.types.Operator):
    bl_idname = "mirrorlink.set_binoms"
    bl_label = "Set Binoms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        functions.find_and_set_binoms()
        return {'FINISHED'}



class MIRRORLINK_OT_BuildSymFromSemiMesh(bpy.types.Operator):
    bl_idname = "mirrorlink.build_sym_from_semi_mesh"
    bl_label = "Mirror Mesh & Set Binoms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        functions.build_sym_from_semi_mesh()
        return {'FINISHED'}