# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import FloatProperty
from bpy.types import PropertyGroup

bl_info = {
    "name" : "SimpleLattice",
    "author" : "benjamin.sauder, Eugene Dudavkin",
    "version": (0, 1, 1),
    "blender" : (2, 93, 0),
    "location": "View3D",
    "description" : "A tool to simplify the workflow with lattice objects.",
    "doc_url": "https://blenderartists.org/t/simplelattice-deform-with-pleasure/1321032",
    "tracker_url": "https://github.com/BenjaminSauder/SimpleLattice", 
    "category" : "Object",
}


from . import op_LatticeCreate
from . import op_LatticeApply
from . import op_LatticeRemove
#from . import preferences


def get_u(self):
    lattice = bpy.context.active_object
    res = bpy.data.lattices[lattice.name]
    return res.points_u
    
def set_u(self, value):
    lattice = bpy.context.active_object
    res = bpy.data.lattices[lattice.name] 
    res.points_u = value

def get_v(self):
    lattice = bpy.context.active_object
    res = bpy.data.lattices[lattice.name]
    return res.points_v

def set_v(self, value):
    lattice = bpy.context.active_object
    res = bpy.data.lattices[lattice.name] 
    res.points_v = value

def get_w(self):
    lattice = bpy.context.active_object
    res = bpy.data.lattices[lattice.name]
    return res.points_w

def set_w(self, value):
    lattice = bpy.context.active_object
    res = bpy.data.lattices[lattice.name] 
    res.points_w = value
    

class MODIFIERSTRENGTH_PG_main(PropertyGroup):
    
    def update_modifierstrength(self, context):
        lattice = context.active_object
        for o in bpy.data.objects:
            for modifier in o.modifiers:   
                if modifier.type == 'LATTICE' and "SimpleLattice" in modifier.name:
                    if modifier.object == lattice:
                        modifier.strength = self.str_obj
        
    str_obj: bpy.props.FloatProperty(
        description = "Change strength for Lattice modifier in objects affected by lattice",
        name        = "Strength",
        min         = 0.0,
        max         = 1.0,
        step        = 1,
        default     = 1,
        update      = update_modifierstrength
    ) 
    

class RESOLUTIONUVW_PG_main(PropertyGroup):    
        
    change_u: bpy.props.IntProperty(
        min         = 2,
        max         = 20,
        get=get_u,
        set=set_u
    )
    
    change_v: bpy.props.IntProperty(
        min         = 2,
        max         = 20,
        get=get_v,
        set=set_v
    ) 
       
    change_w: bpy.props.IntProperty(
        min         = 2,
        max         = 20,
        get=get_w,
        set=set_w
    )
    
        
classes = [
    op_LatticeCreate.Op_LatticeCreateOperator,
    op_LatticeApply.Op_LatticeApplyOperator,
    op_LatticeRemove.Op_LatticeRemoveOperator,
    #preferences.SimpleLatticePrefs,
    MODIFIERSTRENGTH_PG_main,
    RESOLUTIONUVW_PG_main
]


prepend_menus = [
    # removing this as it add top menu entry
    #bpy.types.VIEW3D_MT_edit_mesh,

    bpy.types.VIEW3D_MT_object_context_menu,
    
    bpy.types.VIEW3D_MT_edit_mesh_context_menu,
    
    bpy.types.VIEW3D_MT_edit_lattice_context_menu,
    
    bpy.types.VIEW3D_MT_edit_lattice,
]

#append_menus = [
#    # removing this as it add bottom menu entry
#    bpy.types.VIEW3D_MT_object,
#]

def context_menu(self, context):
    #selected_objects = context.selected_objects
    lattice = context.active_object
    layout = self.layout
    
    show_apply_op = op_LatticeApply.Op_LatticeApplyOperator.poll(context)
    show_remove_op = op_LatticeRemove.Op_LatticeRemoveOperator.poll(context)
    show_create_op = op_LatticeCreate.Op_LatticeCreateOperator.poll(context)
    do_show = show_apply_op or show_create_op

#    if do_show and type(self) in append_menus:
#        layout.separator()   

    if show_apply_op:
        layout.operator("object.op_lattice_apply")
        
    if show_remove_op:
        layout.operator("object.op_lattice_remove")
    
    if show_create_op and not show_apply_op:
        layout.operator("object.op_lattice_create")
    
    if do_show and type(self in prepend_menus):
        layout.separator()

    layout.separator()
   
    if (context.active_object is not None) and (context.active_object.type == 'LATTICE') and ("SimpleLattice" in context.active_object.name):
        layout.label(text="Resolution:")
        col = layout.column()
        sub = col.column(align=True)
        res  = context.scene.RESOLUTIONUVW_PG_main
        sub.prop(res, "change_u", text="       U")
        sub.prop(res, "change_v", text="       V")
        sub.prop(res, "change_w", text="       W")   
        
        layout.separator()
        
        props  = context.scene.MODIFIERSTRENGTH_PG_main
        layout.prop(props, "str_obj", text="       Lattice Strength")
   
    layout.separator()

def register():    
    for menu in prepend_menus:
        menu.prepend(context_menu)

#    for menu in append_menus:
#        menu.append(context_menu)

    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.MODIFIERSTRENGTH_PG_main = bpy.props.PointerProperty(type = MODIFIERSTRENGTH_PG_main)
    bpy.types.Scene.RESOLUTIONUVW_PG_main = bpy.props.PointerProperty(type = RESOLUTIONUVW_PG_main)

def unregister():
    menus = prepend_menus
    #menus.extend(append_menus)

    for menu in menus:
        menu.remove(context_menu)

    for c in classes:
        bpy.utils.unregister_class(c)
    
    del bpy.types.Scene.MODIFIERSTRENGTH_PG_main
    del bpy.types.Scene.RESOLUTIONUVW_PG_main

if __name__ == "__main__":
    register()
