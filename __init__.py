bl_info = {
    "name": "SmartScene Toolkit",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "3D View > Object Context Menu / Edit Mode Menu",
    "description": "Scene structure utilities: parenting, duplication, mirroring, collection management",
    "category": "Object",
}

import importlib

# Import all modules
from . import (
    parent_to_cursor,
    move_hierarchy_to_new_collection,
    hierarchy_duplicate,
    mirror_to_cursor,
    mirror_to_cursor_edit,
)

modules = [
    parent_to_cursor,
    move_hierarchy_to_new_collection,
    hierarchy_duplicate,
    mirror_to_cursor,
    mirror_to_cursor_edit,
]

def register():
    for mod in modules:
        importlib.reload(mod)
        if hasattr(mod, "register"):
            mod.register()

def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()
