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

bl_info = {
    "name" : "SimpleLattice",
    "author" : "benjamin.sauder",
    "location": "View3D",
    "description" : "A tool to simplify the workflow with lattice objects.",
    "blender" : (2, 80, 0),
    "wiki_url" : "https://github.com/BenjaminSauder/SimpleLattice",
    "warning" : "",
    "category" : "Object",
}


from . import op_LatticeCreate
from . import op_LatticeApply
from . import op_LatticeRemove
from . import preferences

classes = [
    op_LatticeCreate.Op_LatticeCreateOperator,
    op_LatticeApply.Op_LatticeApplyOperator,
    op_LatticeRemove.Op_LatticeRemoveOperator,
    #preferences.SimpleLatticePrefs,
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
    
    #lat = context.lattice
    selected_objects = context.selected_objects
    for obj in selected_objects:
        if obj.type == 'LATTICE':
            lat = bpy.data.lattices[obj.name]

            layout.label(text="Resolution:")
            col = layout.column()

            sub = col.column(align=True)
            sub.prop(lat, "points_u", text="       U")
            sub.prop(lat, "points_v", text="       V")
            sub.prop(lat, "points_w", text="       W")
    
    layout.separator()

def register():
    for menu in prepend_menus:
        menu.prepend(context_menu)

#    for menu in append_menus:
#        menu.append(context_menu)

    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    menus = prepend_menus
    #menus.extend(append_menus)

    for menu in menus:
        menu.remove(context_menu)

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()