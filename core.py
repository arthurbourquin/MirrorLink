"""Tout ce qui évite le boilerplate : dérivation des noms, enregistrement auto, base d'opérateur."""
import re
import bpy

PREFIX = "mirrorlink"   # préfixe des idnames -> "mirrorlink.debug"


# ----------------------------------------------------------------------
# NOMS : on n'écrit qu'un nom (PascalCase), le reste en est dérivé
# ----------------------------------------------------------------------

def to_snake(name):
    """AnalyzeMesh -> analyze_mesh"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def to_human(snake_name):
    """analyze_mesh -> Analyze Mesh"""
    return snake_name.replace("_", " ").title()


# ----------------------------------------------------------------------
# ENREGISTREMENT : un décorateur, plus de liste à maintenir
# ----------------------------------------------------------------------

_classes = []


def register_me(cls):
    _classes.append(cls)
    return cls


def register():
    for c in _classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(_classes):
        if hasattr(c, "bl_rna") and c.is_registered:
            bpy.utils.unregister_class(c)


def operators():
    """Tous les opérateurs enregistrés, dans l'ordre de définition."""
    return [c for c in _classes if issubclass(c, BaseOperator)]


# ----------------------------------------------------------------------
# BASE D'OPÉRATEUR
# ----------------------------------------------------------------------

class BaseOperator(bpy.types.Operator):
    """Les sous-classes n'implémentent que run().

    Options de classe :
      dialog   = True   -> ouvre une fenêtre pour régler les propriétés avant de lancer
      in_panel = False  -> pas de bouton automatique dans le panneau
    bl_idname / bl_label sont dérivés du nom de classe, sauf s'ils sont définis à la main.
    """
    bl_options = {'REGISTER', 'UNDO'}
    dialog = False
    in_panel = True
    group = None         # opérateurs consécutifs du même groupe = côte à côte
    button_text = None   # texte court du bouton (sinon bl_label)

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


# ----------------------------------------------------------------------
# PROPRIÉTÉS PARTAGÉES
# ----------------------------------------------------------------------

def precision_prop():
    return bpy.props.IntProperty(
        name="Threshold",
        description="Exposant : seuil = 10 ** valeur",
        default=-4,
        min=-20,
        max=20,
    )
