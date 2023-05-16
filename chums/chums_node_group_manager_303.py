import bpy, os
from shutil import copyfile, copy

##############################
######### Change Log #########
##############################
# v1.1.0 is the version we used on 7723; Justin's original
# v2.0.0 is Conrad Dueck's update
# v3
# v3.0.1 - removed user driven categories which also removes some security
# v3.0.3 - reintroduce limited delete access
bl_info = {
    "name":        "Node Group Manager",
    "description": "Convienient tools for appending, linking, and saving node groups",
    "author":      "Justin Goran, Conrad Dueck",
    "version":     (3, 0, 3),
    "blender":     (3, 30, 1),
    "wiki_url": "",
    "tracker_url": "",
    "location":    "Node Editor > Tool Shelf",
    "category":    "Node"
    }

vrsn = '3.0.3'
dev_local = True

##############################
#### Master Path Settings ####
##############################
if dev_local:
    theserverroot = 'P'
else:
    theserverroot = 'Y'

#base_path = (theserverroot+':\\projects\\CHUMS_Onsite\\pipeline\\software\\tools\\blender\\node_groups')
base_path = ""
empty_blend = os.path.join(base_path, 'empty.blend')

user = os.getlogin()
superusers = ['dplace','cdueck','conrad']

###################
#### Functions ####
###################

def update_node_list(self, context):
    
    # Clear the node list to repopulate it
    self.node_list.clear()
    
    selected = self.cat_lst
    base_path = bpy.context.scene.custom_nodes_library
    #empty_blend = os.path.join(base_path, 'empty.blend')
    cat_path = os.path.join(base_path, selected)
    
    files = os.listdir(cat_path)
    
    for file in files:
        if os.path.isfile(os.path.join(cat_path, file)):
            
            if os.path.splitext(file)[-1] == '.blend':
                node = self.node_list.add()
                node.name = os.path.splitext(file)[0]
                
                node.node_name = node.name
                
                if os.path.isfile(os.path.join(cat_path, '{}_desc.txt'.format(node.name))):
                    with open(os.path.join(cat_path, '{}_desc.txt'.format(node.name)), 'r') as txtfile:
                        lines = txtfile.readlines()
                        node.desc = lines[0].strip()
                        if len(lines) > 2:
                            node.type = lines[2].strip()


def update_cat_lst(self, context):
    user = os.getlogin()
    base_path = bpy.context.scene.custom_nodes_library
    cat_folder = os.listdir(base_path)
    
    categories = [(user,user, '')]
    
    for cat in cat_folder:
        if os.path.isdir(os.path.join(base_path,cat)) and not(cat == user):
            categories.append((cat, cat, ''))
    
    return categories

#########################
#### Control Classes ####
#########################

class GetNodeName(bpy.types.Operator):
    bl_idname = 'nodes.name'
    bl_label = 'Get Name'
    
    def execute(self, context):
        
        bpy.context.scene.custom_nodes.ng_name = context.active_node.node_tree.name
        
        return {'FINISHED'}
      
class ExportNodes(bpy.types.Operator):
    
    bl_idname = 'nodes.save'
    bl_label = 'Save'
    
    def execute(self, context):
        # Get path for the node to import
        base_path = bpy.context.scene.custom_nodes_library
        empty_blend = os.path.join(base_path, 'empty.blend')
        sel_cat = bpy.context.scene.custom_nodes.cat_lst        
        print("sel_cat: ", sel_cat)
        cat_path = os.path.join(base_path, sel_cat)
        print("cat_path: ", cat_path)
        
        # Get the selected node name
        node_props = bpy.context.scene.custom_nodes
        
        ng_name = bpy.context.scene.custom_nodes.ng_name
        print("ng_name: ", ng_name)
        sel = context.active_node.node_tree.name
        print("sel: ", sel)
        
        node_group = bpy.data.node_groups[sel]
        print("node_group: ", node_group)
        base_path = bpy.context.scene.custom_nodes_library
        empty_blend = os.path.join(base_path, 'empty.blend')
        user_path = os.path.join(base_path, user)
        print("user_path: ", user_path)
        arch_path = os.path.join(cat_path, 'archive')
        print("arch_path: ", arch_path)
        new_file = '{}\\{}.blend'.format(cat_path, ng_name)
        
        ### Check if file and folders exist ###
        
        if not os.path.exists(cat_path):
            os.mkdir(cat_path)
        
        if not os.path.exists(arch_path):
            os.mkdir(arch_path)
        
        if os.path.exists(new_file):
            exists = True
            version = 1
            while exists:
                arch_file = '{0}\\{1}_V{2:04d}.blend'.format(arch_path, ng_name, version)
                if os.path.exists(arch_file):
                    version +=1
                else:
                    copy(new_file, arch_file)
                    exists = False        
                
            copy(new_file, arch_path)
        
        ### Copy empty blender file and write the node_group to that file ###
        copyfile(empty_blend, new_file)
        bpy.data.libraries.write(new_file, {node_group}, fake_user=True, compress=True)
        
        #with open('{}\\{}_desc.txt'.format(user_path, ng_name), 'w') as txtfile:
        with open('{}\\{}_desc.txt'.format(base_path, ng_name), 'w') as txtfile:
            txtfile.write(bpy.context.scene.custom_nodes.ng_desc + '\n' + sel + '\n' + node_group.type)
        
        ### Update node list ###
        self = bpy.context.scene.custom_nodes
        update_node_list(self, context)
               
        return {'FINISHED'}
    
class ImportNodes(bpy.types.Operator):
    
    bl_idname = 'nodes.append'
    bl_label = 'Append'
    create : bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        
        # Get path for the node to import
        base_path = bpy.context.scene.custom_nodes_library
        empty_blend = os.path.join(base_path, 'empty.blend')
        sel_cat = bpy.context.scene.custom_nodes.cat_lst        
        cat_path = os.path.join(base_path, sel_cat)
        
        # Get the selected node name
        node_props = bpy.context.scene.custom_nodes
        node_name = node_props.node_list[node_props.index].name
        
        if os.path.isfile(os.path.join(cat_path, '{}_desc.txt'.format(node_name))):
            with open(os.path.join(cat_path, '{}_desc.txt'.format(node_name)), 'r') as txtfile:
                lines = txtfile.readlines()
                if len(lines) <= 1:
                    realname = node_name
                else:
                    realname = lines[1].strip()
            txtfile.close()
        else:
            realname = node_name
            
        # Append the selected node group 
        with bpy.data.libraries.load('{}\\{}.blend'.format(cat_path, node_name), link=False) as (data_from, data_to):
            data_to.node_groups = [node for node in data_from.node_groups if node == realname]   
        
        # If the user clicked append and create
        if self.create:
            
            # Is this a shader node group or a compositing node group
            if bpy.data.node_groups[realname].type == 'SHADER': 
                if context.active_object.type == 'MESH':
                    nodetree = context.active_object.active_material.node_tree
                else:
                    nodetree = context.active_object.data.node_tree
                    
                node = nodetree.nodes.new("ShaderNodeGroup")
                node.node_tree = bpy.data.node_groups[realname]
                    
            elif bpy.data.node_groups[realname].type == 'COMPOSITING':
            
                nodetree = bpy.context.scene.node_tree
                node = nodetree.nodes.new("CompositorNodeGroup")
                node.node_tree = bpy.data.node_groups[realname]
                
            elif bpy.data.node_groups[realname].type == 'GEOMETRY':
            
                #nodetree = bpy.context.scene.node_tree
                if context.active_object.type == 'MESH':
                    nodetree = context.active_object.modifiers.active.node_group
                else:
                    nodetree = context.active_object.data.node_tree
                node = nodetree.nodes.new("GeometryNodeGroup")
                node.node_tree = bpy.data.node_groups[realname]
            
        return {'FINISHED'}
        
class DeleteNodes(bpy.types.Operator):
    
    bl_idname = 'nodes.del'
    bl_label = 'Delete'
    
    def execute(self, context):
    
        base_path = bpy.context.scene.custom_nodes_library
        sel_cat = bpy.context.scene.custom_nodes.cat_lst        
        cat_path = os.path.join(base_path, sel_cat)
        
        # Get the selected node name
        node_props = bpy.context.scene.custom_nodes
        node_name = node_props.node_list[node_props.index].name
        
        node_file = os.path.join(cat_path, '{}.blend'.format(node_name))
        node_desc = os.path.join(cat_path, '{}_desc.txt'.format(node_name))
        
        
        if not(user in superusers):
            if sel_cat == user:
                if os.path.isfile(node_file):
                    os.remove(node_file)
                if os.path.isfile(node_desc):
                    os.remove(node_desc)
        else:
            if os.path.isfile(node_file):
                os.remove(node_file)
            if os.path.isfile(node_desc):
                os.remove(node_desc)
        
        ### Update node list ###
        self = bpy.context.scene.custom_nodes
        update_node_list(self, context)
        
        return {'FINISHED'}
            
#########################
#### Property Groups ####
#########################

def rename_name(self, context):
    sel_cat = bpy.context.scene.custom_nodes.cat_lst
    if sel_cat == user:
     
        base_path = bpy.context.scene.custom_nodes_library
        empty_blend = os.path.join(base_path, 'empty.blend')
        cat_path = os.path.join(base_path, sel_cat)
            
        node_file = os.path.join(cat_path, '{}.blend'.format(self.name))
        node_desc = os.path.join(cat_path, '{}_desc.txt'.format(self.name))
                    
        if self.name != self.node_name:
            if os.path.isfile(node_file):
                os.rename(node_file, os.path.join(cat_path, '{}.blend'.format(self.node_name)))
                
            if os.path.isfile(node_desc):
                with open(node_desc, 'r') as txtfile:
                    lines = txtfile.readlines()
                txtfile.close()
            
                if len(lines) == 1:
                    lines[0] = '{}\n'.format(lines[0])
                    lines.append(self.name)
            
                    with open(node_desc, 'w') as txtfile:
                        txtfile.writelines(lines)
                    txtfile.close()
                    
                os.rename(node_desc, os.path.join(cat_path, '{}_desc.txt'.format(self.node_name)))
            else:
                with open(os.path.join(cat_path, '{}_desc.txt'.format(self.node_name)), 'w') as descfile:
                    lines = ['\n', self.name]
                    descfile.writelines(lines)
                descfile.close()
                    
            self.name = self.node_name
        
def rename_desc(self, context):

    sel_cat = bpy.context.scene.custom_nodes.cat_lst
    if sel_cat == user:
        base_path = bpy.context.scene.custom_nodes_library
        empty_blend = os.path.join(base_path, 'empty.blend')
        cat_path = os.path.join(base_path, sel_cat)
        node_desc = os.path.join(cat_path, '{}_desc.txt'.format(self.name))
        
        if os.path.isfile(node_desc):
            
            with open(node_desc, 'r') as txtfile:
                lines = txtfile.readlines()
            txtfile.close()
                
            if lines[0].strip() != self.desc.strip():
                lines[0] = self.desc + '\n'

                with open(node_desc, 'w') as txtfile:
                    txtfile.writelines(lines)
                txtfile.close()
        else:
            with open(node_desc, 'w') as txtfile:
                lines = [self.desc + '\n', self.name]
                txtfile.writelines(lines)
            txtfile.close()
    
class CUSTOMNODES_UL_customnodes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
    
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            firstclmn = layout.split(factor=0.3, align=True)

            firstclmn.prop(item, "node_name", text="", emboss=False)

            desc_clmn = firstclmn.split(factor=0.3, align=True)

            desc_clmn.prop(item, "type", text="", emboss=False)
            
            desc_clmn.prop(item, "desc", text="", emboss=False)
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'LEFT'
            layout.label("")
            
class CustomNodeGroups(bpy.types.PropertyGroup):
    
    node_name : bpy.props.StringProperty(update=rename_name)
    desc : bpy.props.StringProperty(update=rename_desc)
    type : bpy.props.StringProperty()
    
class CustomNodeProperties(bpy.types.PropertyGroup):
    
    index : bpy.props.IntProperty(default = -1, min=-1)
    
    node_list : bpy.props.CollectionProperty(type=CustomNodeGroups)
    
    # Generate it's items from the Node Group Directory (update_cat_lst), and when the value changes
    # run update_node_list to populate node_list
    
    cat_lst : bpy.props.EnumProperty(name = 'Categories', items = update_cat_lst, update = update_node_list)
    
    ### ng saver settings, ng = Node Group ###
    ng_name : bpy.props.StringProperty()
    ng_desc : bpy.props.StringProperty()


###############
#### Panel ####
###############
      
class CUSTOMNODES_PT_NodeImporter(bpy.types.Panel):
    
    bl_category = 'Custom Nodes'
    bl_label = ('Node Group Appender ' + vrsn)
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    
        
    def draw(self, context):
        
        layout = self.layout
        np = bpy.context.scene.custom_nodes
        
        #### Library Location
        layout.prop(bpy.context.scene, "custom_nodes_library")

        #### Category drop-down ####
        layout.prop(np, 'cat_lst')
        
        #### Node List ####
        layout.template_list('CUSTOMNODES_UL_customnodes', '', np, 'node_list', np, 'index')

        #### Controls ####
        layout.operator('nodes.append').create = False
        layout.operator('nodes.append', text='Append and Create').create = True
        if not(user in superusers):
            sel_cat = bpy.context.scene.custom_nodes.cat_lst
            if sel_cat == user:
                layout.operator('nodes.del')
        else:
            layout.operator('nodes.del')
        
class CUSTOMNODES_PT_NodeExporter(bpy.types.Panel):
    bl_category = 'Custom Nodes'
    bl_label = 'Node Group Saver'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(self, context):
        
        try:
            if context.active_node.node_tree:
                has_nodetree = True
        except AttributeError:
            has_nodetree = False
            
        return (context.active_node is not None and has_nodetree)
        
    
    def draw(self, context):
        layout = self.layout
        np = bpy.context.scene.custom_nodes
        
        namerow = layout.row(align=True)
        namerowsplit = namerow.split(factor=0.8, align=True)
        
        namerowsplit.prop(np, 'ng_name', text='Name')
        namerowsplit.operator('nodes.name')
        
        layout.prop(np, 'ng_desc', text='Description')
        layout.operator('nodes.save')
            
######################
#### Registration ####
######################


classes = (GetNodeName,
           ExportNodes,
           ImportNodes,
           DeleteNodes,
           CUSTOMNODES_UL_customnodes,
           CustomNodeGroups,
           CustomNodeProperties, 
           CUSTOMNODES_PT_NodeImporter, 
           CUSTOMNODES_PT_NodeExporter)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.custom_nodes = bpy.props.PointerProperty(type=CustomNodeProperties)
    bpy.types.Scene.custom_nodes_library = bpy.props.StringProperty(
        name="Library:",
        description="Path to Node Group Library",
        default=base_path,
        maxlen=1024,
        subtype='DIR_PATH')
    

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.custom_nodes

if __name__ == "__main__":
    register() 