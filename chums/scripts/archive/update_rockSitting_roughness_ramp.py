import bpy

def dry_wetrocks(mtl):
    print(mtl.name)
    ramp_node = mtl.node_tree.nodes["ColorRamp.001"].color_ramp
    ramp_node.elements[0].color = (0,0,0,1)
    ramp_node.elements[0].position = 0.0375
    ramp_node.elements[1].color = (0.95,0.95,0.95,1)
    range_node = mtl.node_tree.nodes["Map Range.001"]
    range_node.inputs[4].default_value = 0.25
    return 0

for m in bpy.data.materials:
    if "prx_rockSitting_01:rock" in m.name:
        dry_wetrocks(m)
        