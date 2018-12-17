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
    "description" : "",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


from . import operator

classes = [
    operator.Op_LatticeCreateOperator,
]


def register():
    print("register")
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    print("unregister")

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()