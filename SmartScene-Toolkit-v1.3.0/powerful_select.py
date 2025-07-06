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
    "name": "🪄 SmartScene Toolkit - Powerful Select Tools",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "Object Mode > Powerful Select",
    "category": "Object",
    "description": "Jump to objects/parents in Outliner, enhanced Alt shortcuts"
}


def try_outliner_jump(context):
    """Try to jump to the active object in Outliner.
    This is optional UX enhancement. If Outliner is not open, do nothing."""
    for area in context.window.screen.areas:
        if area.type == 'OUTLINER':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {
                        'window': context.window,
                        'screen': context.screen,
                        'area': area,
                        'region': region,
                    }

                    try:
                        with context.temp_override(**override):
                            bpy.ops.outliner.show_active()
                    except Exception as e:
                        print("Outliner jump failed:", e)
                    return

    # Outliner not found – non-blocking UX notification
    context.window_manager.popup_menu(
        lambda self, ctx: self.layout.label(text="Please open an Outliner to enable jump."),
        title="Outliner Not Found",
        icon='INFO'
    )


class OBJECT_OT_select_parent(bpy.types.Operator):
    """Select the parent of the active object (if any) and jump to it in Outliner"""
    bl_idname = "object.select_parent"
    bl_label = "Parent Select"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.parent:
            for o in context.selected_objects:
                o.select_set(False)

            obj.parent.select_set(True)
            context.view_layer.objects.active = None
            context.view_layer.objects.active = obj.parent
            try_outliner_jump(context)
            self.report({'INFO'}, f"Selected parent: {obj.parent.name}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No parent found")
            return {'CANCELLED'}


class OBJECT_OT_powerful_select(bpy.types.Operator):
    """Jump to active object in Outliner (Alt+. without hover)"""
    bl_idname = "object.powerful_select"
    bl_label = "Powerful Select"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Selected object: {obj.name}")
        context.view_layer.objects.active = None
        context.view_layer.objects.active = obj
        try_outliner_jump(context)
        
        return {'FINISHED'}


class OBJECT_MT_smartscene_powerful_select(bpy.types.Menu):
    """More Powerful Select functions"""
    bl_idname = "OBJECT_MT_smartscene_powerful_select"
    bl_label = "Powerful Select"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.select_parent", text="Parent Select", icon='OUTLINER_OB_EMPTY')
        layout.operator("object.powerful_select", text="Powerful Select", icon='RESTRICT_SELECT_OFF')

def menu_func(self, context):
    if context.mode == "OBJECT":
        self.layout.operator(
            OBJECT_MT_smartscene_powerful_select.bl_idname,
            icon="RESTRICT_SELECT_OFF",
        )

classes = (
    OBJECT_OT_select_parent,
    OBJECT_OT_powerful_select,
    OBJECT_MT_smartscene_powerful_select,
)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)

    # Hotkey Registration:
    # Alt + . for Powerful Select
    # Alt + ，for Parent Select
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi1 = km.keymap_items.new("object.powerful_select", type='PERIOD', value='PRESS', alt=True)
        kmi2 = km.keymap_items.new("object.select_parent", type='COMMA', value='PRESS', alt=True)
        addon_keymaps.extend([(km, kmi1), (km, kmi2)])

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
