import bpy

interpolation_types = (('KEY_LINEAR', 'Linear', ''),
                       ('KEY_CARDINAL', 'Cardinal', ''),
                       ('KEY_CATMULL_ROM', 'Catmull-Rom', ''),
                       ('KEY_BSPLINE', 'BSpline', ''))


class SimpleLatticePrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    default_resolution_u: bpy.props.IntProperty(
        name="Default u", default=2, min=2)
    default_resolution_v: bpy.props.IntProperty(
        name="Default v", default=2, min=2)
    default_resolution_w: bpy.props.IntProperty(
        name="Default w", default=2, min=2)

    default_interpolation: bpy.props.EnumProperty(
        name="Default Interpolation", items=interpolation_types, default='KEY_LINEAR')

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        col = row.column()

        col.prop(self, "default_resolution_u")
        col.prop(self, "default_resolution_v")
        col.prop(self, "default_resolution_w")

        col.prop(self, "default_interpolation")