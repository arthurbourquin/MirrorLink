import bpy

from . import functions
from .core import BaseOperator, register_class
from.utils import ENUM



#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION (WITHOUT BINOM ID ENUM)
#=========#=========#=========#=========#=========#=========#=========#=========

@register_class
class SelectCenterVertices(BaseOperator):
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.select_center_vertices(threshold)

@register_class
class SelectOverlappingVertices(BaseOperator):
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.select_overlapping_vertices(threshold)

@register_class
class SelectAmbigous(BaseOperator):
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.select_ambigous(threshold)

#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION BY ENUM VALUE
#=========#=========#=========#=========#=========#=========#=========#=========

@register_class
class SelectMarkedPair(BaseOperator):
    def run(self, context):
        functions.select_by_attribute_value(ENUM.FIRSTPAIR)

@register_class
class SelectMarkedCenter(BaseOperator):
    def run(self, context):
        functions.select_by_attribute_value(ENUM.CENTER)

@register_class
class SelectMarkedUnset(BaseOperator):
    def run(self, context):
        functions.select_by_attribute_value(ENUM.UNSET)

@register_class
class SelectMarkedIgnore(BaseOperator):
    def run(self, context):
        functions.select_by_attribute_value(ENUM.IGNORE)



#=========#=========#=========#=========#=========#=========#=========#=========
# SET ENUM
#=========#=========#=========#=========#=========#=========#=========#=========

@register_class
class SetIdToSelectedPair(BaseOperator):
    def run(self, context):
        functions.set_id_to_selected_pair()
@register_class
class SetSelectedToCenter(BaseOperator):
    def run(self, context):
        functions.set_selected(ENUM.CENTER)
@register_class
class SetSelectedToUnset(BaseOperator):
    def run(self, context):
        functions.set_selected(ENUM.UNSET)
@register_class
class SetSelectedToIgnore(BaseOperator):
    def run(self, context):
        functions.set_selected(ENUM.IGNORE)



#=========#=========#=========#=========#=========#=========#=========#=========
# MESH MODIFICATION
#=========#=========#=========#=========#=========#=========#=========#=========

@register_class
class SetCentersAtZero(BaseOperator):
    bl_description = "Set 'Center' vertices à x = 0"
    def run(self, context):
        functions.set_centers_at_zero()


@register_class
class SymetrizePair(BaseOperator):
    bl_description = "Set selected to 'Pair'\n"
    bl_description += "Must have exactely 2 selected vertices\n"
    bl_description += "- Vertices will have the same unique 'Pair' ID\n"
    bl_description += "- Vertices will be moved to be mirror of each other"
    def run(self, context):
        mesh_mode = int(context.scene.mirrorlink_pair_2_verts_mode)
        functions.symetrize_pair(mesh_mode)


@register_class
class SymetrizeWholeMesh(BaseOperator):
    bl_description = "Symetrize * the whole mesh *\n"
    bl_description += "Walk the mesh and\n"
    bl_description += "- for each 'Pair' symetrize both vertices\n"
    bl_description += "- leave 'Center', 'Unset' and 'Ignore' vertices untouched"
    def run(self, context):
        mesh_mode = int(context.scene.mirrorlink_pair_mesh)
        functions.symetrize(mesh_mode)




#=========#=========#=========#=========#=========#=========#=========#=========
# WALKS
#=========#=========#=========#=========#=========#=========#=========#=========

@register_class
class AnalyzeGeometry(BaseOperator):
    bl_description =  "Analysis of the mesh GEOMETRY using\n"
    bl_description += "only the vertex coordinates,\n"
    bl_description += "- No attribute needed\n"
    bl_description += "- No attribute reading)\n"
    bl_description += "- No modifications"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.analyze_geometry(threshold)

@register_class
class AnalyzeAttribute(BaseOperator):
    bl_description =  "Analysis of the mesh ENUM:\n"
    bl_description += "'Pair', 'Center', 'Unset', 'Ignore\n"
    bl_description += "- No modifications"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.analyze_attribute(threshold)

@register_class
class SetUpMeshAttribute(BaseOperator):
    bl_description =  "Walk the whole mesh to find 'Pairs' and 'Center'\n"
    bl_description += "- 'Unset', 'Pair' and 'Center' vertices will be reset\n"
    bl_description += "- 'Unset', 'Pair' and 'Center' can be set as 'Ignore'\n"
    bl_description += "- 'Ignore' vertices will be untouched"
    def run(self, context):
        threshold = 10 ** context.scene.mirrorlink_precision_exponent
        functions.set_up_mesh_attribute(threshold)

@register_class
class BuildSymFromSemiMesh(BaseOperator):
    bl_description =  "Build a proper symetric mesh\n"
    bl_description =  "Same as applying a Mirror Modifier but\n"
    bl_description =  "all 'Pair' and 'Center' correctly assigned"
    def run(self, context):
        functions.build_sym_from_semi_mesh()
