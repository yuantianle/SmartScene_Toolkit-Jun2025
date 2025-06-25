bl_info = {
    "name": "Create ECP (Empty Coordinate Parent)",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "🧩 SmartScene Toolkit",
    "category": "Object",
}

import bpy

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
        bpy.ops.object.select_all(action='DESELECT')
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

def register():
    bpy.utils.register_class(OBJECT_OT_create_ecp)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_OT_create_ecp)

if __name__ == "__main__":
    register()
