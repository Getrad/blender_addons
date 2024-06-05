# TODO - turn this script into an addon that can be accessed in the Node Editor UI
# TODO - support shaders in the shader node editor
# TODO - support compositing nodes in the compositor

import bpy

bl_info = {
    "name": "Outs Reroute",
    "author": "Conrad Dueck",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "Node Editor",
    "description": "Make a new named Reroute node for each of the selected node's outputs",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Node",
    }


# --------   FUNCTIONS   --------
def make_node_outputs():
    o = bpy.context.selected_objects[0]
    otree = o.modifiers.active.node_group
    otree_active = otree.nodes.active
    the_outs = [ot.name for ot in otree_active.outputs if (len(ot.name) > 0)]
    for ot in range(len(the_outs)):
        newnode = otree.nodes.new('NodeReroute')
        newnode.parent = otree_active.parent
        locx = (otree_active.location[0] + (otree_active.width*2))
        print("locx:",locx)
        locy = (otree_active.location[1] - (20*ot))
        print("locy:",locy)
        newnode.location = (locx,locy)
        newnode.label = the_outs[ot]
        otree.links.new(otree_active.outputs[ot],newnode.inputs[0])
    return 0



# --------    CLASSES    --------
class NODE_OT_MakeOuputs(bpy.types.Operator):
    bl_idname = 'node.rerouteouts'
    bl_label = 'Reroute Outs'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        make_node_outputs()
        return {'FINISHED'}

class NODE_PT_ChumsPanel(bpy.types.Panel):
    bl_label       = "Convenence Tools"
    bl_idname      = "NODE_PT_ChumsPanel"
    bl_space_type  = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category    = "Chums"
    
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("node.rerouteouts")

# -------- REGISTRATION ---------
classes = ( NODE_OT_MakeOuputs,
            NODE_PT_ChumsPanel,
          )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
if __name__ == "__main__":
    register()