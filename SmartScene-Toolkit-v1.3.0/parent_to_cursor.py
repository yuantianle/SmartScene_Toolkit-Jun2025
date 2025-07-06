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

bl_info = {
    "name": "🪄 SmartScene Toolkit - Create ECP (Empty Coordinate Parent)",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "Object Mode > Parent to ECP",
    "category": "Object",
}

def collect_with_children_recursive(objs):
    result = set()
    for obj in objs:
        result.add(obj)
        result.update(obj.children_recursive)
    return result

def find_root_objects(objs):
    roots = []
    sel_set = set(objs)
    for o in objs:
        p = o
        while p.parent and p.parent in sel_set:
            p = p.parent
        if p not in roots:
            roots.append(p)
    return roots

class OBJECT_OT_create_ecp(bpy.types.Operator):
    bl_idname = "object.create_ecp_parent"
    bl_label = "Parent to ECP (Empty Coordinate Parent)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        if not selected:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        root_objs = find_root_objects(selected)
        all_targets = collect_with_children_recursive(root_objs)


        cursor_loc = context.scene.cursor.location.copy()


        bpy.ops.object.empty_add(type='PLAIN_AXES', location=cursor_loc)
        ecp = context.active_object
        ecp.name = "ECP"


        if not ecp.users_collection:
            self.report({'ERROR'}, "ECP not placed in any collection")
            return {'CANCELLED'}
        target_collection = ecp.users_collection[0]


        for obj in root_objs:
            obj.parent = ecp
            obj.matrix_parent_inverse = ecp.matrix_world.inverted()


        for obj in all_targets:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            if obj.name not in target_collection.objects:
                target_collection.objects.link(obj)

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_create_ecp.bl_idname, icon='OUTLINER_OB_EMPTY')

addon_keymaps = []

def register():
    bpy.utils.register_class(OBJECT_OT_create_ecp)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)

    # Hotkey Registration:
    # Ctrl + Shift + P to create ECP parent
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new("object.create_ecp_parent", type='P', value='PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_OT_create_ecp)

if __name__ == "__main__":
    register()
