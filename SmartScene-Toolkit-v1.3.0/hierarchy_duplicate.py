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
    "name": "🪄 SmartScene Toolkit - Hierarchy Duplicate (multi-parent)",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "Object Mode > Duplicate Hierarchies",
    "category": "Object",
    "description": "Duplicate selected parent hierarchies with their descendants (works with multiple parents)"
}

class OBJECT_OT_DuplicateHierarchyMulti(bpy.types.Operator):
    """Duplicate selected parent hierarchies (works with multiple parents)"""
    bl_idname = "object.hierarchy_dup_multi"
    bl_label = "Duplicate Hierarchies"
    bl_options = {'REGISTER', 'UNDO'}

    def tag_and_unhide_children(self, parent):
        """Recursively select children & remember hidden state."""
        for child in parent.children:
            child["__memoHIV"] = child.hide_viewport
            if child.hide_viewport:
                child.hide_viewport = False
            child.select_set(True)
            self.tag_and_unhide_children(child)

    def restore_hidden_state(self, parent):
        """Restore hidden status stored in __memoHIV."""
        for child in parent.children:
            if child.get("__memoHIV", False):
                child.hide_viewport = True
            if "__memoHIV" in child:
                del child["__memoHIV"]
            self.restore_hidden_state(child)

    def execute(self, context):
        sel_objs = context.selected_objects
        if not sel_objs:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        sel_set = set(sel_objs)
        root_parents = []
        for obj in sel_objs:
            anc = obj
            while anc.parent and anc.parent in sel_set:
                anc = anc.parent
            if anc not in root_parents:
                root_parents.append(anc)
        
        target_collection = context.active_object.users_collection[0] if context.active_object else context.scene.collection

        def duplicate_hierarchy(obj, collection):
            obj_copy = obj.copy()
            if obj.data:
                obj_copy.data = obj.data.copy()
            collection.objects.link(obj_copy)
            obj_copy.matrix_world = obj.matrix_world.copy()
            obj_copy.select_set(True)

            for child in obj.children:
                child_copy = duplicate_hierarchy(child, collection)
                child_copy.parent = obj_copy
                child_copy.matrix_parent_inverse = child.matrix_parent_inverse.copy()

            return obj_copy
        
        for obj in context.selected_objects:
            obj.select_set(False)

        new_roots = []
        for root in root_parents:
            new_root = duplicate_hierarchy(root, target_collection)
            new_roots.append(new_root)

    
        self.report({'INFO'}, f"Duplicated {len(new_roots)} root hierarchies")


        if new_roots:
            bpy.ops.transform.translate('INVOKE_DEFAULT') 

        return {'FINISHED'}


def menu_entry(self, context):
    self.layout.operator(OBJECT_OT_DuplicateHierarchyMulti.bl_idname, icon='OUTLINER_OB_EMPTY')


addon_keymaps = []


def register():
    bpy.utils.register_class(OBJECT_OT_DuplicateHierarchyMulti)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_entry)

    # Hotkey Registration: Ctrl + Shift + D
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(
            OBJECT_OT_DuplicateHierarchyMulti.bl_idname,
            type='D', value='PRESS', ctrl=True, shift=True
        )
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_object_context_menu.append(menu_entry)
    bpy.utils.unregister_class(OBJECT_OT_DuplicateHierarchyMulti)


if __name__ == "__main__":
    register()
