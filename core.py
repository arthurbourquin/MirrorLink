"""
Anything that avoids boilerplate code:
name derivation, auto-registration, operator base.
"""

import re
import bpy

from .utils import ENUM

PREFIX = "mirrorlink"   # idnames prefix -> "mirrorlink.debug"



#=========#=========#=========#=========#=========#=========#=========#=========
# CONVERSION
#=========#=========#=========#=========#=========#=========#=========#=========
# Human   "My Stuff"
# Pascal  "MyStuff"
# snake   "my_stuff"

def to_snake(pascal_name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", pascal_name).lower()

def to_human(snake_name):
    return snake_name.replace("_", " ").title()



#=========#=========#=========#=========#=========#=========#=========#=========
# REGISTER
#=========#=========#=========#=========#=========#=========#=========#=========

_classes = []
_scene_properties = {}

def register_class(cls):
    _classes.append(cls)
    return cls

def register_scene_property(func):
    _scene_properties[func.__name__] = func()
    return func


def register():
    for name, prop in _scene_properties.items():
        setattr(bpy.types.Scene, name, prop)

    for c in _classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(_classes):
        if hasattr(c, "bl_rna") and c.is_registered:
            bpy.utils.unregister_class(c)

    for c in reversed(_classes):
        if hasattr(c, "bl_rna") and c.is_registered:
            bpy.utils.unregister_class(c)


def operators():
    """All registered operators, in the order in which they were defined."""
    return [c for c in _classes if issubclass(c, BaseOperator)]



#=========#=========#=========#=========#=========#=========#=========#=========
# OERATOR BASE
#=========#=========#=========#=========#=========#=========#=========#=========

class BaseOperator(bpy.types.Operator):
    """
    Subclasses implement only run().
    Class options:
      dialog   = True   -> opens a window to set properties before running
      in_panel = False  -> no automatic button in the panel
    bl_idname / bl_label are derived from the class name, unless they are defined manually.
    """
    bl_options = {'REGISTER', 'UNDO'}
    dialog = False
    in_panel = True
    group = None         # consecutive operators from the same group = side by side
    button_text = None   # short button text (otherwise bl_label)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = to_snake(cls.__name__)
        if "bl_idname" not in cls.__dict__:
            cls.bl_idname = f"{PREFIX}.{name}"
        if "bl_label" not in cls.__dict__:
            cls.bl_label = to_human(name)

    def invoke(self, context, event):
        if self.dialog:
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def execute(self, context):
        return self.run(context) or {'FINISHED'}

    def run(self, context):
        raise NotImplementedError
