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
        name="Mode",
        items=[
            (str(ENUM.ACTIVE),     "Active",     "Use the active vertex coordinate"),
            (str(ENUM.X_NEGATIVE), "Negative X", "Use the vertex with the lower x value"),
            (str(ENUM.X_POSITIVE), "Positive X", "Use the vertex with the greater x value"),
            (str(ENUM.AVERAGE),    "Average",    "Use the average value"),
            (str(ENUM.NONE),       "Leave",      "Don't move vertices"),
        ],
        default=str(ENUM.ACTIVE),
    )

@register_scene_property
def mirrorlink_set_center_mode():
    return bpy.props.EnumProperty(
        name="Mode",
        items=[
            (str(ENUM.NONE), "Leave", "Don't move vertices"),
            (str(ENUM.MOVE), "Move",  "Move at x = 0"),
        ],
        default=str(ENUM.MOVE),
    )

@register_scene_property
def mirrorlink_pair_mesh():
    return bpy.props.EnumProperty(
        name="Mesh pairing mode",
        items=[
            (str(ENUM.X_NEGATIVE), "X negative to positive", "Use the vertex with the lower x value"),
            (str(ENUM.X_POSITIVE), "X positive to negative", "Use the vertex with the greater x value"),
            (str(ENUM.AVERAGE),    "Average",                "Use the average value"),
        ],
        default=str(ENUM.X_NEGATIVE),
    )