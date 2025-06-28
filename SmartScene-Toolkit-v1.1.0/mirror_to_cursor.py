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
from mathutils import Matrix

bl_info = {
    "name": "Mirror-Duplicate to Cursor (Plane Style)",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "🧩 SmartScene Toolkit",
    "category": "Object",
    "description": "Mirror-duplicate selected hierarchies across the 3D-cursor XY/YZ/ZX plane"
}

def collect_recursive(objs):
    res = set()
    for o in objs:
        res.add(o)
        res.update(o.children_recursive)
    return res

def find_roots(objs):
    roots, sel = [], set(objs)
    for o in objs:
        p = o
        while p.parent and p.parent in sel:
            p = p.parent
        if p not in roots:
            roots.append(p)
    return roots

def make_mirror_matrix(cursor_vec, axis):
    idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]
    scale = Matrix.Identity(4)
    scale[idx][idx] = -1
    T_back  = Matrix.Translation(cursor_vec)
    T_to_ori = Matrix.Translation(-cursor_vec)
    return T_back @ scale @ T_to_ori


class OBJECT_OT_mirror_dup_cursor(bpy.types.Operator):
    bl_idname = "object.mirror_duplicate_cursor"
    bl_label = "Mirror-Duplicate to Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        name="Mirror Plane",
        items=[
            ('X', "Across YZ (flip X)", "Mirror across YZ plane"),
            ('Y', "Across ZX (flip Y)", "Mirror across ZX plane"),
            ('Z', "Across XY (flip Z)", "Mirror across XY plane"),
        ],
        default='X'
    )

    def duplicate_hierarchy(self, obj, collection):
        obj_copy = obj.copy()
        if obj.data:
            obj_copy.data = obj.data.copy()
        collection.objects.link(obj_copy)
        obj_copy.matrix_world = obj.matrix_world.copy()

        for child in obj.children:
            child_copy = self.duplicate_hierarchy(child, collection)
            child_copy.parent = obj_copy
            child_copy.matrix_parent_inverse = child.matrix_parent_inverse.copy()

        return obj_copy
    

    def execute(self, context):
        sel = context.selected_objects
        if not sel:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        roots = find_roots(sel)
        all_targets = collect_recursive(roots)


        target_collection = context.active_object.users_collection[0] if context.active_object else context.scene.collection

        root_dups = []
        for root in roots:
            dup_root = self.duplicate_hierarchy(root, target_collection)
            root_dups.append(dup_root)


        cursor = context.scene.cursor.location.copy()
        M_mirror = make_mirror_matrix(cursor, self.axis)
        for obj in root_dups:
            obj.matrix_world = M_mirror @ obj.matrix_world

        return {'FINISHED'}


def menu_func(self, context):
    if context.mode == 'OBJECT':
        self.layout.menu("OBJECT_MT_mirror_dup_submenu", icon='MOD_MIRROR')

class OBJECT_MT_mirror_dup_submenu(bpy.types.Menu):
    bl_label = "Mirror Duplicate to Cursor Plane"

    def draw(self, context):
        layout = self.layout
        mirror_items = [
            ('X', "Across YZ (flip X)"),
            ('Y', "Across ZX (flip Y)"),
            ('Z', "Across XY (flip Z)"),
        ]
        for axis, label in mirror_items:
            op = layout.operator(OBJECT_OT_mirror_dup_cursor.bl_idname, text=label, icon='MOD_MIRROR')
            op.axis = axis


classes = (
    OBJECT_OT_mirror_dup_cursor,
    OBJECT_MT_mirror_dup_submenu,
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
