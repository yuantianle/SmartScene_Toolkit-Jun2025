bl_info = {
    "name": "Mirror-Duplicate to Cursor (Plane Style)",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "🧩 SmartScene Toolkit",
    "category": "Object",
    "description": "Mirror-duplicate selected hierarchies across the 3D-cursor XY/YZ/ZX plane"
}

import bpy
from mathutils import Matrix


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

    def execute(self, context):
        sel = context.selected_objects
        if not sel:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        roots = find_roots(sel)
        all_targets = collect_recursive(roots)

        bpy.ops.object.select_all(action='DESELECT')
        for o in all_targets:
            o.select_set(True)
        bpy.ops.object.duplicate()
        dups = context.selected_objects.copy()


        root_dups = [o for o in dups if o.parent not in dups]

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
