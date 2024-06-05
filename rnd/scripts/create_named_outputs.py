# TODO - turn this script into an addon that can be accessed in the Node Editor UI
# TODO - support shaders in the shader node editor
# TODO - support compositing nodes in the compositor

import bpy

o = bpy.context.selected_objects[0]
otree = o.modifiers.active.node_group
otree_active = otree.nodes.active
the_outs = [ot.name for ot in otree_active.outputs if (len(ot.name) > 0)]

for ot in range(len(the_outs)):
    print(ot)
    
    newnode = otree.nodes.new('NodeReroute')
    newnode.parent = otree_active.parent
    locx = (otree_active.location[0] + (otree_active.width*2))
    print("locx:",locx)
    locy = (otree_active.location[1] - (20*ot))
    print("locy:",locy)
    newnode.location = (locx,locy)
    newnode.label = the_outs[ot]
    otree.links.new(otree_active.outputs[ot],newnode.inputs[0])
    
