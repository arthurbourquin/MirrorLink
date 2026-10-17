import bpy

from .core import register_scene_property
from .utils import ENUM



@register_scene_property
def mirrorlink_precision_exponent():
    return bpy.props.IntProperty(
        name="Precision Exponent",
        description="Exponent used to calculate the tolerance (10^exponent)",
        default=-4,
        min=-12,
        max=3,
    )

@register_scene_property
def mirrorlink_pair_2_verts_mode():
    return bpy.props.EnumProperty(
        name="Pair 2 Verts Mode",
        items=[
            (str(ENUM.ACTIVE),    "Active",     "Use the active vertex coordinate"),
            (str(ENUM.XNEGATIVE), "Negative X", "Use the vertex with the lower x value"),
            (str(ENUM.XPOSITIVE), "Positive X", "Use the vertex with the greater x value"),
            (str(ENUM.AVERAGE),   "Average",    "Use the average value"),
        ],
        default=str(ENUM.ACTIVE),
    )

@register_scene_property
def mirrorlink_pair_mesh():
    return bpy.props.EnumProperty(
        name="Mesh pairing mode",
        items=[
            (str(ENUM.XNEGATIVE), "Negative X", "Use the vertex with the lower x value"),
            (str(ENUM.XPOSITIVE), "Positive X", "Use the vertex with the greater x value"),
            (str(ENUM.AVERAGE),   "Average",    "Use the average value"),
        ],
        default=str(ENUM.XNEGATIVE),
    )