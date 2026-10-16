from . import functions
from .core import BaseOperator, register_me, precision_prop

ATTNAME = 'pair-id'
FIRSTBINOM = 1
CENTER     = 0
UNSET      = -1
IGNORE     = -2


#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION (WITHOUT BINOM ID ATTRIBUTE)
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class SelectCenterVertices(BaseOperator):
    dialog = True
    precision: precision_prop()
    def run(self, context):
        functions.select_center_vertices(10 ** self.precision)

@register_me
class SelectOverlappingVertices(BaseOperator):
    dialog = True
    precision: precision_prop()
    def run(self, context):
        functions.select_overlapping_vertices(10 ** self.precision)



#=========#=========#=========#=========#=========#=========#=========#=========
# SELECTION BY ATTRIBUTE VALUE
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class SelectMarkedPair(BaseOperator):
    def run(self, context):
        functions.select_by_attribute_value(FIRSTBINOM)

@register_me
class SelectMarkedCenter(BaseOperator):
    def run(self, context):
        functions.select_by_attribute_value(CENTER)

@register_me
class SelectMarkedUnset(BaseOperator):
    def run(self, context):
        functions.select_by_attribute_value(UNSET)

@register_me
class SelectMarkedIgnore(BaseOperator):
    def run(self, context):
        functions.select_by_attribute_value(IGNORE)



#=========#=========#=========#=========#=========#=========#=========#=========
# SET ATTRIBUTE
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class SetIdToSelectedPair(BaseOperator):
    def run(self, context):
        functions.set_id_to_selected_pair()
@register_me
class SetSelectedToCenter(BaseOperator):
    def run(self, context):
        functions.set_selected(CENTER)
@register_me
class SetSelectedToUnset(BaseOperator):
    def run(self, context):
        functions.set_selected(UNSET)
@register_me
class SetSelectedToIgnore(BaseOperator):
    def run(self, context):
        functions.set_selected(IGNORE)



#=========#=========#=========#=========#=========#=========#=========#=========
# MESH MODIFICATION
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class SymetrizePair(BaseOperator):
    def run(self, context):
        functions.symetrize_pair("POSITIVE")

@register_me
class SymetrizeWholeMeshPositive(BaseOperator):
    def run(self, context):
        functions.symetrize("POSITIVE")

@register_me
class SymetrizeWholeMeshNegative(BaseOperator):
    def run(self, context):
        functions.symetrize("NEGATIVE")



#=========#=========#=========#=========#=========#=========#=========#=========
# WALKS
#=========#=========#=========#=========#=========#=========#=========#=========

@register_me
class AnalyzeGeometry(BaseOperator):
    precision: precision_prop()
    def run(self, context):
        functions.analyze_geometry(10 ** self.precision)

@register_me
class AnalyzeAttribute(BaseOperator):
    precision: precision_prop()
    def run(self, context):
        functions.analyze_attribute(10 ** self.precision)

@register_me
class FindAndSetPairs(BaseOperator):
    def run(self, context):
        functions.find_and_set_pairs()

@register_me
class BuildSymFromSemiMesh(BaseOperator):
    def run(self, context):
        functions.build_sym_from_semi_mesh()
