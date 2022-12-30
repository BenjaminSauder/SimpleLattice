#Version 0.1.5

import bpy

from . import util


class Op_LatticeRemoveOperator(bpy.types.Operator):
    bl_idname = "object.op_lattice_remove"
    bl_label = "Simple Lattice Remove"
    bl_description = "Remove the lattice for all objects whose FFD modifiers are targeting it"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        lattice = context.active_object

        if lattice.mode == "EDIT":
            bpy.ops.object.editmode_toggle()

        vertex_groups = []

        for obj in context.view_layer.objects:
            if obj.type in util.allowed_object_types:
                vertex_groups.clear()

                if obj.type == "MESH":
                    for modifier in obj.modifiers:
                        if modifier.type == 'LATTICE' and "SimpleLattice" in modifier.name:
                            if modifier.object == lattice:
                                vertex_group = self.kill_lattice_modifer(context, modifier, lattice)
                                if vertex_group:
                                    vertex_groups.append(vertex_group)

                                    # Clear any selection
                                    for f in obj.data.polygons:
                                        f.select = False
                                    for e in obj.data.edges:
                                        e.select = False
                                    for v in obj.data.vertices:
                                        v.select = False
                                    # Get verts in vertex group
                                    verts = [v for v in obj.data.vertices if obj.vertex_groups[vertex_group].index in [i.group for i in v.groups]]
                                    # Select verts in vertex group
                                    for v in verts:
                                        v.select = True
                
                                    # if apply with vertex groups 
                                    # then select all objects and switch to EDIT mode
                                    obj.select_set(True)
                                    bpy.ops.object.editmode_toggle()
                                    bpy.ops.mesh.select_mode(type="VERT")

                                if not vertex_group:
                                    # if apply without vertex groups 
                                    # then select all objects and stay in OBJECT mode
                                    obj.select_set(True)

                if obj.type == "GPENCIL":
                    for modifier in obj.grease_pencil_modifiers:   
                        if modifier.type == 'GP_LATTICE' and "SimpleLattice" in modifier.name:
                            if modifier.object == lattice:
                                # checking for lattice on top of the grease_pencil_modifiers stack (for any reason)
                                # https://blender.stackexchange.com/questions/233357/how-to-get-modifier-position
                                if obj.grease_pencil_modifiers[0].type == "GP_LATTICE" and obj.grease_pencil_modifiers[0].object == lattice:
                                    self.report({'INFO'}, 'Modifier applied')
                                else:
                                    self.report({'INFO'}, 'Applied modifier was not first, result may not be as expected')
                                
                                vertex_group = self.kill_lattice_gpencil_modifer(context, modifier, lattice)
                                ''' NOT IMPLEMENTED IN API YET
                                if vertex_group:
                                    vertex_groups.append(vertex_group)

                                    # Clear any selection
                                    for layer in obj.data.layers:
                                        for frame in layer.frames:
                                            for stroke in frame.strokes:
                                                for point in stroke.points:
                                                    point.select = False

                                    # Get points in vertex group
                                    all_points = []
                                    for layer in obj.data.layers:
                                        for frame in layer.frames:
                                            for stroke in frame.strokes:
                                                for point in stroke.points:
                                                    all_points.append(point)
                                    points = [v for v in all_points if obj.vertex_groups[vertex_group].index in [i.group for i in v.groups]]
                                    # Select points in vertex group
                                    for point in points:
                                        point.select = True
                
                                    # if apply with vertex groups 
                                    # then select all objects and switch to EDIT mode
                                    obj.select_set(True)
                                    bpy.ops.object.editmode_toggle()
                                    bpy.ops.mesh.select_mode(type="VERT")
                                '''

                                if not vertex_group:
                                    # if apply without vertex groups 
                                    # then select all objects and stay in OBJECT mode
                                    obj.select_set(True)
                
                self.kill_vertex_groups(obj, vertex_groups)
                
#        try:
#            self.kill_custom_orientation()
#        except:
#            pass
        
        # removing Lattice object with its data
        # https://blender.stackexchange.com/questions/233204/how-can-i-purge-recently-deleted-objects
        lattice_obs = [o for o in context.selected_objects if o.type == 'LATTICE']
        purge_data = set(o.data for o in lattice_obs)
        bpy.data.batch_remove(lattice_obs)
        bpy.data.batch_remove([o for o in purge_data if not o.users])
        self.report({'INFO'}, 'Lattice was removed')

        context.view_layer.update()
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return (len(context.selected_objects) == 1 and
                context.active_object and
                context.active_object.type == 'LATTICE' and
                context.active_object.select_get())

    def set_active(self, context, object):
        context.view_layer.objects.active = object

    def kill_lattice_modifer(self, context, modifier, target):
        vertex_group = ""

        if modifier.type != "LATTICE" or modifier.object != target:
            return vertex_group

        if context.active_object != modifier.id_data:
            self.set_active(context, modifier.id_data)

        if modifier.vertex_group != None:
            vertex_group = modifier.vertex_group

        if modifier.show_viewport:

            if modifier.id_data.mode != 'OBJECT':
                bpy.ops.object.editmode_toggle()

            bpy.ops.object.modifier_remove(modifier=modifier.name)

        return vertex_group

    def kill_lattice_gpencil_modifer(self, context, modifier, target):
        vertex_group = ""

        if modifier.type != "GP_LATTICE" or modifier.object != target:
            return vertex_group

        if context.active_object != modifier.id_data:
            self.set_active(context, modifier.id_data)

        if modifier.vertex_group != None:
            vertex_group = modifier.vertex_group

        if modifier.show_viewport:

            if modifier.id_data.mode != 'OBJECT':
                bpy.ops.object.editmode_toggle()

            bpy.ops.object.gpencil_modifier_remove(modifier=modifier.name)

        return vertex_group

    def kill_vertex_groups(self, obj, vertex_groups):
        if len(vertex_groups) == 0:
            return

        modifiers = filter(lambda modifier: hasattr(modifier, "vertex_group")
                           and modifier.vertex_group, obj.modifiers)
        used_vertex_groups = set(
            map(lambda modifier: modifier.vertex_group, modifiers))

        obsolete = filter(
            lambda group: group not in used_vertex_groups, vertex_groups)

        for group in obsolete:
            print(f"removed vertex_group: {group}")
            vg = obj.vertex_groups.get(group)
            obj.vertex_groups.remove(vg)

#    def kill_custom_orientation(self):
#        orig_transform = bpy.context.scene.transform_orientation_slots[0].type
#        bpy.context.scene.transform_orientation_slots[0].type = 'SimpleLattice_Orientation'
#        bpy.ops.transform.delete_orientation()
#        bpy.data.scenes[0].transform_orientation_slots[0].type = orig_transform
