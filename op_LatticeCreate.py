import bpy
from mathutils import *

from . import util


# Recursivly transverse layer_collection for a particular name
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

class Op_LatticeCreateOperator(bpy.types.Operator):
    bl_idname = "object.op_lattice_create"
    bl_label = "Create Lattice"
    bl_description = "Creates and binds a lattice object to the current selection."
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {"REGISTER", "UNDO"}


    init = False

    # presets =  (('2', '2x2x2', ''),
    #             ('3', '3x3x3', ''),
    #             ('4', '4x4x4', ''))

    # preset: bpy.props.EnumProperty(name="Presets", items=presets, default='2')
    orientation_types = (('GLOBAL', 'Global', ''),
                         ('LOCAL', 'Local', ''),
                         ('CURSOR', 'Cursor', ''),
                         ('NORMAL', 'Normal', ''))
                         
    position_types = (('on_top','On Top',''),
                      ('bottom','Bottom',''))

    interpolation_types = (('KEY_LINEAR', 'Linear', ''),
                           ('KEY_CARDINAL', 'Cardinal', ''),
                           ('KEY_CATMULL_ROM', 'Catmull-Rom', ''),
                           ('KEY_BSPLINE', 'BSpline', ''))

    orientation: bpy.props.EnumProperty(
        name="Orientation", 
        items=orientation_types, 
        default='NORMAL'
    )

    #on_top: bpy.props.BoolProperty (name="On Top", default = False, description="Move modifier on top of stack")
    modifier_position: bpy.props.EnumProperty (
        name="Modifier", 
        items=position_types,
        default="bottom", 
        description="Move modifier on top or bottom in the stack"
    )

    resolution_u: bpy.props.IntProperty(
        name="u", 
        default=2, 
        min=2
    )
    
    resolution_v: bpy.props.IntProperty(
        name="v", 
        default=2, 
        min=2
    )
    
    resolution_w: bpy.props.IntProperty(
        name="w", 
        default=2, 
        min=2
    )
    
    interpolation: bpy.props.EnumProperty(
        name="Interpolation", 
        items=interpolation_types, 
        default='KEY_LINEAR'
    )
        
    scale: bpy.props.FloatProperty(
        name="Scale", 
        default=1.0, 
        min=0.001, 
        soft_min=0.1, 
        soft_max=2.0
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        sub = col.row()
        sub.prop(self, "orientation")
        
        col.separator()        
        sub = col.row()
        sub.prop(self, "modifier_position", expand=True)
        
        col.separator()
        sub = col.row()
        sub2 = sub.column(align=True)
        sub2.prop(self, "resolution_u", text="Resolution U")
        sub2.prop(self, "resolution_v", text="V")
        sub2.prop(self, "resolution_w", text="W")

        col.separator()
        sub = col.row()        
        sub.prop(self, "interpolation")
        
        col.separator()
        sub = col.row()  
        sub.prop(self, "scale")

    @classmethod
    def poll(self, context):
        if (context.active_object.type in util.allowed_object_types and
                context.active_object.mode == 'EDIT'):
            return True

        has_selection = len(context.selected_objects) != 0
        if has_selection:
            for obj in context.selected_objects:
                if obj.type in util.allowed_object_types:
                    return True

        return False

    def execute(self, context):
        # if add lattice in Edit mode, 
        # preventing undo objects data if settings in "Adjust last action" panel was changed
        self.for_edit_mode(context) 
    
        # Defaults from Addon preferences
        if not Op_LatticeCreateOperator.init:
            prefs = bpy.context.preferences.addons[__package__].preferences

            self.orientation = prefs.default_orientation
            self.modifier_position = prefs.default_position
            self.resolution_u = prefs.default_resolution_u
            self.resolution_v = prefs.default_resolution_v
            self.resolution_w =  prefs.default_resolution_w            
            self.interpolation = prefs.default_interpolation
            self.scale = prefs.default_scale

            Op_LatticeCreateOperator.init = True

        objects = []
        all_objecst_are_meshes = True
        
        for obj in context.selected_objects:            
            if obj.type in util.allowed_object_types:
                objects.append(obj)

                if all_objecst_are_meshes and obj.type != 'MESH':
                    all_objecst_are_meshes = False

        # for the shitty case when the active object is in edit mode,
        # but is not selected..
        if len(objects) == 0:
            objects.append(context.active_object)

        self.vertex_mode = all_objecst_are_meshes and objects[0].mode == 'EDIT'

        if len(objects) > 0:
            #self.mapping = None
            self.group_mapping = None
            self.vert_mapping = None
            #self.object_names = list(map(lambda x: x.name, objects))

            self.cleanup(objects)

            if self.vertex_mode:
                self.coords, self.vert_mapping = self.get_coords_from_verts(objects)

                if len(self.coords) == 0:
                    bpy.ops.object.mode_set(mode='EDIT')
                    self.report({'INFO'}, 'Need to be at least 1 vertex selected')
                    return {'CANCELLED'}

                self.group_mapping = self.set_vertex_group(objects, self.vert_mapping)

            else:
                self.coords = self.get_coords_from_objects(objects)

            lattice = self.createLattice(context)
            #self.lattice = lattice
            #self.lattice_name = lattice.name

            self.matrix = context.active_object.matrix_world.copy()
            
            self.update_lattice_from_bbox(context, lattice, self.coords, self.matrix)
            
            self.add_ffd_modifier(objects, lattice, self.group_mapping)

            self.set_selection(context, lattice, objects)

            context.view_layer.update()
            
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def set_selection(self, context, lattice, other):        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        lattice.select_set(True)
        context.view_layer.objects.active = lattice 
        bpy.ops.object.editmode_toggle()

    def get_coords_from_verts(self, objects):
        worldspace_verts = []
        vert_mapping = {}

        for obj in objects:
            bpy.ops.object.editmode_toggle()          
            #obj.select_set(False)

            vert_indices = []
            vertices = obj.data.vertices
            for vert in vertices:
                if vert.select == True:
                    index = vert.index
                    vert_indices.append(index)
                    worldspace_verts.append(obj.matrix_world @ vert.co)

            vert_mapping[obj.name] = vert_indices

        return worldspace_verts, vert_mapping

    def get_coords_from_objects(self, objects):
        bbox_world_coords = []
        for obj in objects:
            coords = obj.bound_box[:]
            coords = [(obj.matrix_world @ Vector(p[:])).to_tuple()
                      for p in coords]
            bbox_world_coords.extend(coords)

        return bbox_world_coords

    def update_lattice_from_bbox(self, context, lattice, bbox_world_coords, matrix_world):  
        if self.orientation == 'GLOBAL':
            rotation = Matrix.Identity(4)
            bbox = util.bounds(bbox_world_coords)
            bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
            
        elif self.orientation == 'NORMAL':
            orig_transform = bpy.context.scene.transform_orientation_slots[0].type
            bpy.context.scene.transform_orientation_slots[0].type = 'SimpleLattice_Orientation'
            co = bpy.context.scene.transform_orientation_slots[0].custom_orientation
            bpy.data.scenes[0].transform_orientation_slots[0].type = orig_transform
            
            rotation = co.matrix.to_quaternion().to_matrix().to_4x4()            
            bbox = util.bounds(bbox_world_coords, rotation.inverted())                        
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            
            # removing custom orientation
            orig_transform = bpy.context.scene.transform_orientation_slots[0].type
            bpy.context.scene.transform_orientation_slots[0].type = 'SimpleLattice_Orientation'
            bpy.ops.transform.delete_orientation()
            bpy.data.scenes[0].transform_orientation_slots[0].type = orig_transform

        elif self.orientation == 'LOCAL':
            rotation = matrix_world.to_quaternion().to_matrix().to_4x4()
            bbox = util.bounds(bbox_world_coords, rotation.inverted())
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'

        elif self.orientation == 'CURSOR':
            mode = context.scene.cursor.rotation_mode
            if mode == "QUATERNION":
                rotation = context.scene.cursor.rotation_quaternion.to_matrix().to_4x4()
            elif mode == "AXIS_ANGLE":
                axis_angle = context.scene.cursor.rotation_axis_angle
                rotation = Quaternion(axis_angle[1:], axis_angle[0])
                rotation = rotation.to_matrix().to_4x4()
            else:
                rotation = context.scene.cursor.rotation_euler.to_matrix().to_4x4()
    
            bbox = util.bounds(bbox_world_coords, rotation.inverted())
            bpy.context.scene.transform_orientation_slots[0].type = 'CURSOR'
            
        bound_min = Vector((bbox.x.min, bbox.y.min, bbox.z.min))
        bound_max = Vector((bbox.x.max, bbox.y.max, bbox.z.max))
        offset = (bound_min + bound_max) * 0.5

        # finally gather position/rotation/scaling for the lattice
        location = rotation @ offset        
        scale = Vector((abs(bound_max.x - bound_min.x),
                        abs(bound_max.y - bound_min.y),
                        abs(bound_max.z - bound_min.z)))

        self.updateLattice(lattice, location, rotation, scale)

    def createLattice(self, context):
        object_active = bpy.context.view_layer.objects.active
        lattice_data = bpy.data.lattices.new(object_active.name + '_SimpleLattice')
        lattice_obj = bpy.data.objects.new(object_active.name + '_SimpleLattice', lattice_data)
        
        # create Lattice in the collection with the active selected object
        obj = bpy.context.object
        ucol = obj.users_collection
        try:
            for i in ucol:
                layer_collection = bpy.context.view_layer.layer_collection
                layerColl = recurLayerCollection(layer_collection, i.name)
                bpy.data.collections[layerColl.name].objects.link(lattice_obj)
        except:
            context.scene.collection.objects.link(lattice_obj)
            
        return lattice_obj

    def updateLattice(self, lattice, location, rotation, scale):
        lattice.data.points_u = self.resolution_u
        lattice.data.points_v = self.resolution_v
        lattice.data.points_w = self.resolution_w

        lattice.data.interpolation_type_u = self.interpolation
        lattice.data.interpolation_type_v = self.interpolation
        lattice.data.interpolation_type_w = self.interpolation

        lattice.location = location
        lattice.rotation_euler = rotation.to_euler()
        lattice.scale = Vector((scale.x * self.scale,
                                scale.y * self.scale,
                                scale.z * self.scale))

    def add_ffd_modifier(self, objects, lattice, group_mapping):
        for obj in objects:
            ffd = obj.modifiers.new("SimpleLattice", "LATTICE")
            
            # good to see modified vertices if add more than one Lattice to the mesh/es
            obj.modifiers[ffd.name].show_in_editmode = True
            obj.modifiers[ffd.name].show_on_cage = True

            # Move Lattice modifier to the top of modifiers stack (if needed)
            # https://blender.stackexchange.com/questions/223134/adding-a-modifier-to-the-top-of-the-stack-of-multiple-objects-without-overwritin
#            if self.on_top == True:
#                obj.select_set(True)
#                bpy.context.view_layer.objects.active = obj                
#                bpy.ops.object.modifier_move_to_index(modifier=ffd.name, index=0)            
            if self.modifier_position == 'on_top':
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj                
                bpy.ops.object.modifier_move_to_index(modifier=ffd.name, index=0)
            if self.modifier_position == 'bottom':
                pass
            
            ffd.object = lattice
            if group_mapping != None:
                vertex_group_name = group_mapping[obj.name]
                ffd.name = vertex_group_name
                ffd.vertex_group = vertex_group_name

            obj.update_tag()

    def cleanup(self, objects):
        for obj in objects:
            used_vertex_groups = set()
            obsolete_modifiers = []
            for modifier in obj.modifiers:
                if modifier.type == 'LATTICE' and "SimpleLattice" in modifier.name:
                    if modifier.vertex_group != "":
                        used_vertex_groups.add(modifier.vertex_group)
                    elif (modifier.object == None or (modifier.vertex_group == "" and modifier.vertex_group not in obj.vertex_groups)):
                        #a,b,c = modifier.object == None, modifier.vertex_group == "", modifier.vertex_group not in obj.vertex_groups
                        #print(f"obj:{a} - vertexgrp empty: {b} - not in groups: {c}" )
                        obsolete_modifiers.append(modifier)


            obsolete_groups = []
            for grp in obj.vertex_groups:
                if "SimpleLattice" in grp.name:
                    if grp.name not in used_vertex_groups:
                        obsolete_groups.append(grp)

            for group in obsolete_groups:
                print(f"removed vertex_group: {group.name}")
                obj.vertex_groups.remove(group)
            for modifier in obsolete_modifiers:
                print(f"removed modifier: {modifier.name}")
                obj.modifiers.remove(modifier)

    def set_vertex_group(self, objects, vert_mapping):
        group_mapping = {}
        for obj in objects:

            mode = obj.mode
            if obj.mode == "EDIT":
                bpy.ops.object.editmode_toggle()

            #group_index = 0
            #for grp in obj.vertex_groups:
                #if "SimpleLattice." in grp.name:
                    #index = int(grp.name.split(".")[-1])
                    #group_index = max(group_index, index)

            #group = obj.vertex_groups.new(name=f"SimpleLattice.{group_index}")
            group = obj.vertex_groups.new(name=f"SimpleLattice")

            group.add(vert_mapping[obj.name], 1.0, "REPLACE")
            group_mapping[obj.name] = group.name

            if mode != obj.mode:
                bpy.ops.object.editmode_toggle()

        return group_mapping
        
    def for_edit_mode(self, context):
        try:
            bpy.ops.transform.create_orientation(name="SimpleLattice_Orientation", use=False, overwrite=True)
        except:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.transform.create_orientation(name="SimpleLattice_Orientation", use=False, overwrite=True)
                          
        active_object = context.view_layer.objects.active
        if active_object.mode == "EDIT":            
            objects_originals = context.selected_objects

            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.empty_add()

#            bpy.ops.object.duplicate()

            objects_created = context.selected_objects

            # removing objects with its data
            # https://blender.stackexchange.com/questions/233204/how-can-i-purge-recently-deleted-objects
            for obj in objects_created:
                purge_data = [o.data for o in context.selected_objects if o.data]
                bpy.data.batch_remove(context.selected_objects)
                bpy.data.batch_remove([o for o in purge_data if not o.users])
                
            # selecting original objects with active
            for obj in objects_originals:
                obj.select_set(True)
                context.view_layer.objects.active = active_object

            bpy.ops.object.mode_set(mode = 'EDIT')
            
        bpy.ops.ed.undo_push()
