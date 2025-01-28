#Remove parents and apply xforms

import bpy
from mathutils import *

ob = bpy.context.selected_objects[0]


def collectFamTree(ob,famTree):
    while ob.parent is not None:
        if not(ob.parent in famTree):
            famTree.insert(0, ob.parent)
        ob = ob.parent
        collectFamTree(ob,famTree)
    return famTree
        
famTree = []

ft = collectFamTree(ob,famTree)
ft = ft.append(ob)


for o in famTree:
    wld = o.matrix_world
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
    o.parent = None
    o.matrix_world = wld
    bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
    