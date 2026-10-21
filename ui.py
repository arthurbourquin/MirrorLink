import bpy
from .core import register_class



@register_class
class MIRRORLINK_PT_main(bpy.types.Panel):
    bl_label = "MirrorLink"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MirrorLink"

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="GENERAL")
        layout.prop(context.scene, "mirrorlink_precision_exponent")

        layout.label(text="")
        layout.label(text="ANALYZE")
        row = layout.row(align=True)
        row.operator("mirrorlink.analyze_geometry", text="Geometry")
        row.operator("mirrorlink.analyze_attribute", text="Attribute")

        layout.label(text="")
        layout.label(text="SELECTION")
        row = layout.row(align=True)
        row.operator("mirrorlink.select_ambigous", text="ambigous")
        row.operator("mirrorlink.select_center_vertices", text="at center")
        row.operator("mirrorlink.select_overlapping_vertices", text="overlapping")
        row = layout.row(align=True)
        row.operator("mirrorlink.select_marked_pair", text="'Pairs'")
        row.operator("mirrorlink.select_marked_center", text="'Center'")
        row.operator("mirrorlink.select_marked_unset", text="'Unset'")
        row.operator("mirrorlink.select_marked_ignore", text="'Ignore'")

        layout.label(text="")
        layout.label(text="MODIFICATION")
        layout.label(text="Attribute")
        row = layout.row(align=True)
        row.operator("mirrorlink.set_selected_to_unset", text="'Unset'")
        row.operator("mirrorlink.set_selected_to_ignore", text="'Ignore'")

        layout.label(text="Location & Attribute")
        row = layout.row(align=True)
        row.operator("mirrorlink.set_centers_at_zero", text="'Center' at x = 0")
        row.scale_y = 2
        row = layout.row(align=True)
        left = row.column(align=True)
        left.prop(context.scene, "mirrorlink_pair_2_verts_mode", text="")
        e = left.row(align=True)
        e.operator("mirrorlink.symetrize_pair", text="Pair", icon="LINKED")
        e.scale_y = 3
        right = row.column(align=True)
        right.prop(context.scene, "mirrorlink_pair_mesh", text="",)
        e = right.row(align=True)
        e.operator("mirrorlink.symetrize_whole_mesh", text="Symetrize")
        e.scale_y = 3

        row = layout.row(align=True)
        row.scale_y = 2
        row.operator("mirrorlink.set_up_mesh_attribute", text="Set Up Mesh")



"""
· • – — ← → ↑ ↓ ○ ● □ ■ △ ◇ ± × ÷ ≠ ≤ ≥ ≈ ° Ø × ✓
Pictos:
FULLSCREEN_ENTER
FULLSCREEN_EXIT
OBJECT_ORIGIN
OBJECT_DATA
MESH_CUBE
SPHERE
MODIFIER
TOOL_SETTINGS
PREFERENCES
SETTINGS
TRANSFORM
ORIENTATION_GLOBAL
EMPTY_AXIS
CONSTRAINT
DUPLICATE
ADD
REMOVE
TRASH
CHECKMARK
CANCEL
PLAY
PAUSE
FILE_FOLDER
FILE_TICK
EXPORT
IMPORT
QUESTION
INFO
ERROR
WARNING
VIEWZOOM
ZOOM_IN
ZOOM_OUT
PIVOT_CURSOR
SNAP_ON
LINKED
UNLINKED
RESTRICT_SELECT_OFF
HIDE_ON
HIDE_OFF
OBJECT
OBJECT_HIDDEN
EDITMODE_HLT
SCULPTMODE_HLT
POSE_HLT
PARTICLEMODE
OUTLINER_OB_MESH
OUTLINER_OB_EMPTY
OUTLINER_OB_CAMERA
OUTLINER_OB_LIGHT
OUTLINER_OB_ARMATURE
CAMERA_DATA
LIGHT
LIGHT_DATA
CURVE_DATA
MATERIAL
TEXTURE
SHADING_RENDERED
SHADING_SOLID
SHADING_WIRE
SHADING_TEXTURE
RENDER_STILL
RENDER_ANIMATION
IMAGE
IMAGE_DATA
UV
GROUP
COLLECTION_NEW
FILE_NEW
FILE_REFRESH
FILE
UNDO
REDO
LOOP_BACK
FILE_BACKUP
REC
DECORATE
DRIVER
KEYFRAME
KEYFRAME_HLT
PLAY_REVERSE
FRAME_PREV
FRAME_NEXT
REW
FF
ALIGN_LEFT
ALIGN_CENTER
ALIGN_RIGHT
ALIGN_JUSTIFY
LINENUMBERS_ON
BOLD
ITALIC
UNDERLINE
COPYDOWN
PASTEDOWN
PASTEFLIPDOWN
ARROW_LEFTRIGHT
TRIA_LEFT
TRIA_RIGHT
TRIA_UP
TRIA_DOWN
DISCLOSURE_TRI_DOWN
DISCLOSURE_TRI_RIGHT
DOWNARROW_HLT
RIGHTARROW
UPARROW
BACK
FORWARD
HOME
FILE_PARENT
FILEBROWSER
FOLDER_REDIRECT
WORLD
SCENE
PROPERTIES
WORKSPACE
SCREEN
WINDOW
CONSOLE
SCRIPT
HELP
URL
LINK
UNLINK
LOCKED
UNLOCKED
PINNED
UNPINNED
RESTRICT_VIEW_OFF
RESTRICT_RENDER_OFF
RESTRICT_INSTANCED_OFF
CHECKBOX_HLT
CHECKBOX_DEHLT
RADIOBUT_ON
RADIOBUT_OFF
FAKE_USER_ON
FAKE_USER_OFF
DECORATE_KEYFRAME
DECORATE_ANIMATE
DECORATE_DRIVER
DECORATE_LINKED
PLUS
MINUS
X
MENU_PANEL
PANEL_CLOSE
PANEL
WINDOW_CLOSE
WINDOW_MAXIMIZE
WINDOW_MINIMIZE
FULLSCREEN
RESTRICT_COLOR_OFF
COLOR
BRUSH_DATA
GP_SELECT_POINTS
GP_SELECT_STROKES
GP_SELECT_BETWEEN_STROKES
"""

