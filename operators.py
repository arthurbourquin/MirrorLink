import bpy

from .functions import build_sym_from_semi_mesh, find_and_set_binoms, debug


class MIRRORLINK_OT_Debug(bpy.types.Operator):
    bl_idname = "mirrorlink.debug"
    bl_label = "Debug"

    def execute(self, context):
        debug()
        return {'FINISHED'}



class MIRRORLINK_OT_SetBinoms(bpy.types.Operator):
    bl_idname = "mirrorlink.set_binoms"
    bl_label = "Set Binoms"

    def execute(self, context):
        find_and_set_binoms()
        return {'FINISHED'}



class MIRRORLINK_OT_BuildSymFromSemiMesh(bpy.types.Operator):
    bl_idname = "mirrorlink.build_sym_from_semi_mesh"
    bl_label = "Mirror Mesh & Set Binoms"

    def execute(self, context):
        build_sym_from_semi_mesh()
        return {'FINISHED'}