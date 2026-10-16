from . import functions
from .core import BaseOperator, register_me, precision_prop

ATTNAME = 'pair-id'
FIRSTBINOM = 1
CENTER     = 0
UNSET      = -1
IGNORE     = -2

SetSelectedTo_Group = "Set selected to"
SelectWithoutAttribute_Group = "Select vertices..."
SelectByAttributeValue_Group = "Select vertices marked as..."
Symetrize_Group = "Symetrize..."


#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION (WITHOUT BINOM ID ATTRIBUTE)
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class SelectCenterVertices(BaseOperator):
    bl_description = "Select all vertices at x = 0 (+/- margin)"
    group = SelectWithoutAttribute_Group
    button_text = "...at center"
    dialog = True
    precision: precision_prop()
    def run(self, context):
        functions.select_center_vertices(10 ** self.precision)

@register_me
class SelectOverlappingVertices(BaseOperator):
    bl_description = "Select all overlapping vertices with margin"
    group = SelectWithoutAttribute_Group
    button_text = "...overlapping"
    dialog = True
    precision: precision_prop()
    def run(self, context):
        functions.select_overlapping_vertices(10 ** self.precision)



#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION BY ATTRIBUTE VALUE
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class SelectMarkedPair(BaseOperator):
    bl_description = "Select all vertices marked as pair"
    group = SelectByAttributeValue_Group
    button_text = "...pair"
    def run(self, context):
        functions.select_by_attribute_value(FIRSTBINOM)

@register_me
class SelectMarkedCenter(BaseOperator):
    bl_description = "Select all vertices marked as being at center"
    group = SelectByAttributeValue_Group
    button_text = "...at center"
    def run(self, context):
        functions.select_by_attribute_value(CENTER)

@register_me
class SelectMarkedUnset(BaseOperator):
    bl_description = "Select all vertices marked as unset"
    group = SelectByAttributeValue_Group
    button_text = "...unset"
    def run(self, context):
        functions.select_by_attribute_value(UNSET)

@register_me
class SelectMarkedIgnore(BaseOperator):
    bl_description = "Select all vertices marked as to be ignored"
    group = SelectByAttributeValue_Group
    button_text = "...to ignore"
    def run(self, context):
        functions.select_by_attribute_value(IGNORE)



#=========#=========#=========#=========#=========#=========#=========#=========
# SET ATTRIBUTE
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class MirrorPair(BaseOperator):
    group = SetSelectedTo_Group
    button_text = "Pair"
    def run(self, context):
        functions.set_id_to_selected_pair()
@register_me
class SetSelectedToCenter(BaseOperator):
    group = SetSelectedTo_Group
    button_text = "Centered"
    def run(self, context):
        functions.set_selected(CENTER)
@register_me
class SetSelectedToUnset(BaseOperator):
    group = SetSelectedTo_Group
    button_text = "Unset"
    def run(self, context):
        functions.set_selected(UNSET)
@register_me
class SetSelectedToIgnore(BaseOperator):
    group = SetSelectedTo_Group
    button_text = "To Ignore"
    def run(self, context):
        functions.set_selected(IGNORE)



#=========#=========#=========#=========#=========#=========#=========#=========
# MESH MODIFICATION
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class SymetrizePair(BaseOperator):
    group = Symetrize_Group
    button_text = "...selected vertices"
    def run(self, context):
        functions.symetrize_pair("POSITIVE")

@register_me
class SymetrizePair(BaseOperator):
    group = Symetrize_Group
    button_text = "...whole Mesh by Pair IDs"
    def run(self, context):
        functions.symetrize("POSITIVE")





#=========#=========#=========#=========#=========#=========#=========#=========
# WALKS
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class AnalyzeMesh(BaseOperator):
    dialog = True
    precision: precision_prop()
    def run(self, context):
        functions.analyze_mesh(10 ** self.precision)

@register_me
class FindAndSetPairs(BaseOperator):
    def run(self, context):
        functions.find_and_set_pairs()

@register_me
class BuildSymFromSemiMesh(BaseOperator):
    bl_label = "Mirror Mesh & Set Pairs"   # label écrit à la main : prioritaire sur le dérivé
    def run(self, context):
        functions.build_sym_from_semi_mesh()
