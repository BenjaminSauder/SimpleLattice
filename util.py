#Version 0.1.6

import bpy
from mathutils import * 
import collections

allowed_object_types = set(['MESH', 'CURVE', 'SURFACE',
                            'FONT', 'GPENCIL', 'LATTICE'])

# https://blender.stackexchange.com/questions/32283/what-are-all-values-in-bound-box
def bounds(local_coords, orientation=None):
    if orientation:
        def apply_orientation(p): return orientation @ Vector(p[:])
        coords = [apply_orientation(p).to_tuple() for p in local_coords]
    else:
        coords = [p[:] for p in local_coords]

    rotated = zip(*coords[::-1])

    push_axis = []
    for (axis, _list) in zip('xyz', rotated):
        def info(): return None
        info.max = max(_list)
        info.min = min(_list)
        info.distance = info.max - info.min
        push_axis.append(info)

    originals = dict(zip(['x', 'y', 'z'], push_axis))

    o_details = collections.namedtuple('object_details', 'x y z')
    return o_details(**originals)
