import bpy

from .core import register_scene_property
from .utils import ENUM



# PRECISION

@register_scene_property
def mirrorlink_precision_exponent():
    return bpy.props.IntProperty(
        name="Precision Exponent",
        description="Exponent used to calculate the tolerance (10^exponent)",
        default=-4,
        min=-12,
        max=3,
    )



# PAIR 2 VERTS

@register_scene_property
def mirrorlink_pair_2_verts_mode():
    return bpy.props.EnumProperty(
        name="Source",
        items=[
            (str(ENUM.ACTIVE),     "Active", "Use the active vertex coordinate"),
            (str(ENUM.X_NEGATIVE), "-x   →   +x", "Use the vertex with the lower x value"),
            (str(ENUM.X_POSITIVE), "+x   →   -x", "Use the vertex with the greater x value"),
            (str(ENUM.AVERAGE),    "Average", "Use the average value"),
            (str(ENUM.NONE),       "Leave", "Don't move vertices"),
        ],
        default=str(ENUM.ACTIVE),
    )



# MARK CENTER

@register_scene_property
def mirrorlink_set_center_mode():
    return bpy.props.EnumProperty(
        name="Mode",
        items=[
            (str(ENUM.NONE), "Leave", "Don't move vertices"),
            (str(ENUM.MOVE), "Move", "Move at x = 0"),
        ],
        default=str(ENUM.MOVE),
    )



# RESTORE MESH

@register_scene_property
def mirrorlink_restore_source_mode():
    return bpy.props.EnumProperty(
        name="Source",
        items=[
            (str(ENUM.X_NEGATIVE), "-x   →   +x", "Use the vertex with the lower x value"),
            (str(ENUM.X_POSITIVE), "+x   →   -x", "Use the vertex with the greater x value"),
            (str(ENUM.AVERAGE),    "Average", "Use the average value"),
        ],
        default=str(ENUM.X_NEGATIVE),
    )


@register_scene_property
def mirrorlink_restore_select_mode():
    return bpy.props.EnumProperty(
        name="Source",
        items=[
            (str(ENUM.ALL), "All", "Modify all vertices"),
            (str(ENUM.SELECTED), "Selected", "Modify selected vertices"),
        ],
        default=str(ENUM.ALL),
    )