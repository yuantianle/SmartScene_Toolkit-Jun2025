import bpy

bl_info = {
    "name": "SmartScene Toolkit - Hierarchy Duplicate (multi-parent)",
    "author": "Tianle Yuan",
    "version": (1, 0, 0),
    "blender": (4, 4, 3),
    "location": "🧩 SmartScene Toolkit",
    "category": "Object",
    "description": "Duplicate selected parent hierarchies with their descendants (works with multiple parents)"
}


class OBJECT_OT_DuplicateHierarchyMulti(bpy.types.Operator):
    """Duplicate selected parent hierarchies (works with multiple parents)"""
    bl_idname = "object.hierarchy_dup_multi"
    bl_label = "Duplicate Hierarchy (Multi)"
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

        bpy.ops.object.select_all(action='DESELECT')
        for root in root_parents:
            root.select_set(True)
            self.tag_and_unhide_children(root)

        bpy.ops.object.duplicate()

        new_roots = [obj for obj in context.selected_objects if obj.parent is None]

        for root in (root_parents + new_roots):
            self.restore_hidden_state(root)

        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}


def menu_entry(self, context):
    self.layout.operator(OBJECT_OT_DuplicateHierarchyMulti.bl_idname, icon='OUTLINER_OB_EMPTY')


addon_keymaps = []


def register():
    bpy.utils.register_class(OBJECT_OT_DuplicateHierarchyMulti)
    bpy.types.VIEW3D_MT_object.append(menu_entry)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            OBJECT_OT_DuplicateHierarchyMulti.bl_idname,
            type='D', value='PRESS', ctrl=True, shift=True
        )
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_object.remove(menu_entry)
    bpy.utils.unregister_class(OBJECT_OT_DuplicateHierarchyMulti)


if __name__ == "__main__":
    register()
