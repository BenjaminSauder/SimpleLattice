import bpy
from mathutils import *

from . import util


class Op_LatticeCreateOperator(bpy.types.Operator):
    bl_idname = "object.op_lattice_create"
    bl_label = "Create Lattice"
    bl_description = "Creates and binds a lattice object to the current selection."
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {"REGISTER", "UNDO"}

    # presets =  (('2', '2x2x2', ''),
    #             ('3', '3x3x3', ''),
    #             ('4', '4x4x4', ''))

    # preset: bpy.props.EnumProperty(name="Presets", items=presets, default='2')

    orientation_types = (('GLOBAL', 'Global', ''),
                         ('LOCAL', 'Local', ''),
                         ('CURSOR', 'Cursor', ''))

    orientation: bpy.props.EnumProperty(
        name="Orientation", items=orientation_types, default='LOCAL')

    resolution_u: bpy.props.IntProperty(name="u", default=2, min=2)
    resolution_v: bpy.props.IntProperty(name="v", default=2, min=2)
    resolution_w: bpy.props.IntProperty(name="w", default=2, min=2)

    scale: bpy.props.FloatProperty(
        name="Scale", default=1.0, min=0.001, soft_min=0.1, soft_max=2.0)

    interpolation_types = (('KEY_LINEAR', 'Linear', ''),
                           ('KEY_CARDINAL', 'Cardinal', ''),
                           ('KEY_CATMULL_ROM', 'Catmull-Rom', ''),
                           ('KEY_BSPLINE', 'BSpline', ''))

    interpolation: bpy.props.EnumProperty(
        name="Interpolation", items=interpolation_types, default='KEY_LINEAR')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()

        col.prop(self, "orientation", text="Orientation")

        col.separator()

        col.prop(self, "resolution_u", text="Resolution U")
        col.prop(self, "resolution_v", text="V")
        col.prop(self, "resolution_w", text="W")

        col.separator()

        col.prop(self, "interpolation", text="Interpolation")
       
        col.separator()

        col.prop(self, "scale", text="Scale")

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

    def invoke(self, context, event):
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
            self.mapping = None
            self.group_mapping = None
            self.vert_mapping = None
            self.object_names = list(map(lambda x: x.name, objects))

            self.cleanup(objects)

            if self.vertex_mode:
                self.coords, self.vert_mapping = self.get_coords_from_verts(
                    objects)
                
                if len(self.coords) == 0:
                    return {'CANCELLED'} 

                self.group_mapping = self.set_vertex_group(objects,
                                                           self.vert_mapping)

            else:
                self.coords = self.get_coords_from_objects(objects)

            lattice = self.createLattice(context)
            self.lattice = lattice
            self.lattice_name = lattice.name

            self.matrix = context.active_object.matrix_world.copy()
            self.update_lattice_from_bbox(
                context, lattice, self.coords, self.matrix)

            self.add_ffd_modifier(objects, lattice, self.group_mapping)

            self.set_selection(context, lattice, objects)
          
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    # this whole invole/execute thing is a bit confusing..
    def execute(self, context):
        if not hasattr(self, "lattice"):
            result = self.invoke(context, None)
            if 'CANCELLED' in result:
                return result

        objects = map(lambda name: bpy.context.scene.objects[name],
                          self.object_names)

        # this is a bit weird, behaviour is different between
        # object and edit mode, as the undo result makes it so
        # that in edit mode objects persist, and in object mode not
        if self.lattice_name in bpy.context.scene.objects:
            lattice = bpy.context.scene.objects[self.lattice_name]
        else:
            lattice = self.createLattice(context)
            
            self.add_ffd_modifier(objects, lattice, self.group_mapping)
            

        self.update_lattice_from_bbox(context,
                                      lattice,
                                      self.coords,
                                      self.matrix)

        self.set_selection(context, lattice, objects)

        if lattice.mode == "EDIT":
            bpy.ops.object.editmode_toggle()

        return {'FINISHED'}

    def set_selection(self, context, lattice, other):
        for obj in other:
            obj.select_set(False)

        lattice.select_set(True)
        context.view_layer.objects.active = lattice

    def get_coords_from_verts(self, objects):
        worldspace_verts = []
        vert_mapping = {}

        for obj in objects:
            obj.select_set(False)

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
            rot = Matrix.Identity(4)
            bbox = util.bounds(bbox_world_coords)

        elif self.orientation == 'LOCAL':
            rot = matrix_world.to_quaternion().to_matrix().to_4x4()
            bbox = util.bounds(bbox_world_coords, rot.inverted())

        elif self.orientation == 'CURSOR':
            rot = context.scene.cursor_rotation.to_matrix().to_4x4()
            bbox = util.bounds(bbox_world_coords, rot.inverted())

        bound_min = Vector((bbox.x.min, bbox.y.min, bbox.z.min))
        bound_max = Vector((bbox.x.max, bbox.y.max, bbox.z.max))
        offset = (bound_min + bound_max) * 0.5

        # finally gather position/rotation/scaling for the lattice
        location = rot @ offset
        rotation = rot
        scale = Vector((abs(bound_max.x - bound_min.x),
                        abs(bound_max.y - bound_min.y),
                        abs(bound_max.z - bound_min.z)))

        self.updateLattice(lattice, location, rotation, scale)

    def createLattice(self, context):
        lattice_data = bpy.data.lattices.new('SimpleLattice')
        lattice_obj = bpy.data.objects.new('SimpleLattice', lattice_data)

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
            ffd.object = lattice
            if group_mapping != None:
                vertex_group_name = group_mapping[obj.name]
                ffd.name = vertex_group_name
                ffd.vertex_group = vertex_group_name

    def cleanup(self, objects):
        for obj in objects:
            used_vertex_groups = set()
            obsolete_modifiers = []
            for modifier in obj.modifiers:
                if modifier.type == 'LATTICE' and "SimpleLattice" in modifier.name:
                    if modifier.object == None:
                        obsolete_modifiers.append(modifier)
                    elif modifier.vertex_group == "":
                        used_vertex_groups.add(modifier.vertex_group)

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

            group_index = 0
            for grp in obj.vertex_groups:
                if "SimpleLattice." in grp.name:
                    index = int(grp.name.split(".")[-1])
                    group_index = max(group_index, index)

            group = obj.vertex_groups.new(name=f"SimpleLattice.{group_index}")

            group.add(vert_mapping[obj.name], 1.0, "REPLACE")
            group_mapping[obj.name] = group.name

            if mode != obj.mode:
                bpy.ops.object.editmode_toggle()

        return group_mapping
