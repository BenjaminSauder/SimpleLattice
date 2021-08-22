import bpy


class SimpleLatticePrefs(bpy.types.AddonPreferences):
    bl_idname = __package__
    
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
   
    default_orientation: bpy.props.EnumProperty(
        name="Default Orientation", 
        items=orientation_types, 
        default='GLOBAL'
    )

    default_position: bpy.props.EnumProperty(
        name="Default Position", 
        items=position_types, 
        default='bottom'
    )

    default_resolution_u: bpy.props.IntProperty(
        #name="Default U", 
        default=2, 
        min=2
    )
    
    default_resolution_v: bpy.props.IntProperty(
        #name="Default V", 
        default=2, 
        min=2
    )
    
    default_resolution_w: bpy.props.IntProperty(
        #name="Default W", 
        default=2, 
        min=2
    )

    default_interpolation: bpy.props.EnumProperty(
        name="Default Interpolation", 
        items=interpolation_types, 
        default='KEY_LINEAR'
    )
    
    default_scale: bpy.props.FloatProperty(
        name="Scale", 
        default=1.0, 
        min=0.001, 
        soft_min=0.1, 
        soft_max=2.0
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        box = layout.box()
        col = box.column()
        sub = col.row()
        sub.prop(self, "default_orientation", expand=True)
        
        col.separator()        
        sub = col.row()
        sub.prop(self, "default_position", expand=True)
        
        col.separator()
        sub = col.row()
        sub2 = sub.column(align=True)
        sub2.prop(self, "default_resolution_u", text="Default  U")
        sub2.prop(self, "default_resolution_v", text="V")
        sub2.prop(self, "default_resolution_w", text="W")

        col.separator()
        sub = col.row()        
        sub.prop(self, "default_interpolation")
        
        col.separator()
        sub = col.row()        
        sub.prop(self, "default_scale")
