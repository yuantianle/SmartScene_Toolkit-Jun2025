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
import bmesh
from mathutils import Vector

bl_info = {
    "name": "🪄 SmartScene Toolkit - Mirror Duplicate (Edit Mode, Multi-Object) to Cursor",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "Object Mode > Mirror Duplicate to Cursor (edit mode)",
    "category": "Object",
    "description": "Duplicate and mirror selected mesh elements across 3D cursor plane in Edit Mode (multi-object supported)"
}

class MESH_OT_mirror_dup_edit_cursor(bpy.types.Operator):
    """Duplicate and mirror selected geometry in Edit Mode using cursor as mirror center"""
    bl_idname = "mesh.mirror_duplicate_edit_cursor"
    bl_label = "Mirror Duplicate to Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        name="Mirror Axis",
        items=[
            ('X', "Across YZ (flip X)", "Mirror across YZ plane (flip X)"),
            ('Y', "Across ZX (flip Y)", "Mirror across ZX plane (flip Y)"),
            ('Z', "Across XY (flip Z)", "Mirror across XY plane (flip Z)"),
        ],
        default='X'
    )

    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, "Must be in Edit Mode")
            return {'CANCELLED'}

        cursor = context.scene.cursor.location.copy()
        idx = {'X': 0, 'Y': 1, 'Z': 2}[self.axis]

        found = False

        for obj in context.selected_objects:
            if obj.type != 'MESH' or not obj.select_get():
                continue
            if obj.mode != 'EDIT':
                continue

            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()

            selected_geom = [e for e in bm.verts if e.select] + \
                            [e for e in bm.edges if e.select] + \
                            [e for e in bm.faces if e.select]

            if not selected_geom:
                continue

            found = True

            for v in bm.verts:
                v.select = False
            for e in bm.edges:
                e.select = False
            for f in bm.faces:
                f.select = False

            res = bmesh.ops.duplicate(bm, geom=selected_geom)
            new_verts = [ele for ele in res["geom"] if isinstance(ele, bmesh.types.BMVert)]

            for v in new_verts:
                world_co = obj.matrix_world @ v.co
                offset = world_co - cursor
                offset[idx] *= -1
                mirrored_world_co = cursor + offset
                v.co = obj.matrix_world.inverted() @ mirrored_world_co

            for elem in res["geom"]:
                if hasattr(elem, "select"):
                    elem.select = True

            bmesh.update_edit_mesh(obj.data, loop_triangles=True, destructive=False)

        if not found:
            self.report({'WARNING'}, "No selected mesh elements found")
            return {'CANCELLED'}

        return {'FINISHED'}


class MESH_MT_mirror_dup_edit_cursor_menu(bpy.types.Menu):
    bl_idname = "MESH_MT_mirror_dup_edit_cursor_menu"
    bl_label = "Mirror Duplicate to Cursor Plane"

    def draw(self, context):
        layout = self.layout
        for axis, label in [
            ('X', "Across YZ (flip X)"),
            ('Y', "Across ZX (flip Y)"),
            ('Z', "Across XY (flip Z)"),
        ]:
            op = layout.operator(MESH_OT_mirror_dup_edit_cursor.bl_idname, text=label, icon='MOD_MIRROR')
            op.axis = axis


def menu_func(self, context):
    if context.mode == 'EDIT_MESH':
        self.layout.menu(MESH_MT_mirror_dup_edit_cursor_menu.bl_idname, icon='MOD_MIRROR')


classes = (
    MESH_OT_mirror_dup_edit_cursor,
    MESH_MT_mirror_dup_edit_cursor_menu,
)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Mesh", space_type='EMPTY')
        kmi = km.keymap_items.new("mesh.mirror_duplicate_edit_cursor", type='M', value='PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
