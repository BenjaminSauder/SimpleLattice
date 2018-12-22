import bpy
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

classes = [
    op_LatticeCreate.Op_LatticeCreateOperator,
    op_LatticeApply.Op_LatticeApplyOperator,
]


menus = [
    bpy.types.VIEW3D_MT_edit_mesh,
    bpy.types.VIEW3D_MT_object_specials,
]

def context_menu(self, context):
    layout = self.layout
    
    show_apply_op = op_LatticeApply.Op_LatticeApplyOperator.poll(context)
    if show_apply_op:
        layout.operator("object.op_lattice_apply")

    show_create_op = op_LatticeCreate.Op_LatticeCreateOperator.poll(context)
    if show_create_op and not show_apply_op:
        layout.operator("object.op_lattice_create")
    
    if show_apply_op or show_create_op:
        layout.separator()


def register():
    for menu in menus:
        menu.prepend(context_menu)

    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for menu in menus:
        menu.remove(context_menu)

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()