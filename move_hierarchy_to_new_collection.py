# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Tianle Yuan

# ***** BEGIN GPL LICENSE BLOCK ****
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK ****

import bpy
from bpy.props import StringProperty

bl_info = {
    "name": "Move Hierarchy to New Collection",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "🧩 SmartScene Toolkit",
    "category": "Object",
    "description": "Move selected objects and their full hierarchy into a new collection",
}

def collect_recursive(objs):
    """Return a set with every object in objs and all their descendants."""
    res = set()
    for o in objs:
        res.add(o)
        res.update(o.children_recursive)
    return res


class OBJECT_OT_move_hierarchy_to_collection(bpy.types.Operator):
    bl_idname = "object.move_hierarchy_to_collection"
    bl_label = "Move Hierarchy to New Collection"
    bl_options = {"REGISTER", "UNDO"}

    collection_name: StringProperty(
        name="Collection Name",
        description="Target collection (will be created if it doesn't exist). "
                    "Leave blank to use <ObjectName>_COLL",
        default="",
    )

    def execute(self, context):
        sel = context.selected_objects
        if not sel:
            self.report({"WARNING"}, "No objects selected")
            return {"CANCELLED"}


        new_name = self.collection_name.strip()
        if not new_name:

            new_name = f"{sel[0].name}_COLL"

        if new_name in bpy.data.collections:
            new_col = bpy.data.collections[new_name]
        else:
            new_col = bpy.data.collections.new(new_name)
            context.scene.collection.children.link(new_col)


        all_objs = collect_recursive(sel)


        for obj in all_objs:
            for col in obj.users_collection:
                col.objects.unlink(obj)
            new_col.objects.link(obj)

        self.report({"INFO"}, f"Moved {len(all_objs)} object(s) to collection: {new_name}")
        return {"FINISHED"}



def menu_func(self, context):
    if context.mode == "OBJECT":
        self.layout.operator(
            OBJECT_OT_move_hierarchy_to_collection.bl_idname,
            icon="OUTLINER_COLLECTION",
        )


classes = (
    OBJECT_OT_move_hierarchy_to_collection,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
