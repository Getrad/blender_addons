import bpy

print("\n\nSTART")
# node_types = ['OBJECT_INFO','COLLECTION_INFO','STORE_NAMED_ATTRIBUTE','INPUT_ATTRIBUTE']
node_types = ['OBJECT_INFO','COLLECTION_INFO','INPUT_ATTRIBUTE']

def gn_gather_deps(gntree):
    gn_deps = []
    for node in gntree.nodes:
        print(node.name, node.type)
        if node.type in node_types:
            print('\t',node.label, node.inputs[0].identifier)
            if node.type =='STORE_NAMED_ATTRIBUTE':
                gn_deps.append((node.name, node.inputs[2].default_value))
                node.label = node.inputs[2].default_value
                node.inputs[2].default_value = ''
            elif node.type =='INPUT_ATTRIBUTE':
                print(node.inputs[0].default_value)
                gn_deps.append((node.name, node.inputs[0].default_value))
                node.label = str(node.inputs[0].default_value)
                node.inputs[0].default_value = ''
            else:
                if (node.inputs[0].default_value is not None) and len(node.label) == 0:
                    gn_deps.append((node.name, node.inputs[0].default_value.name))
                    node.label = node.inputs[0].default_value.name
                    node.inputs[0].default_value = None
        
    return gn_deps

def gn_restore_deps(gntree):
    for node in gntree.nodes:
        if node.type in node_types:
            #print(gntree.name, node.name, node.type, node.label)
            if node.type == 'OBJECT_INFO':
                try:
                    node.inputs[0].default_value = bpy.data.objects[node.label]
                except:
                    print("Failed to set:", gntree.name, node.name, node.inputs[0].identifier, "to:", node.label)
            elif node.type == 'COLLECTION_INFO':
                try:
                    node.inputs[0].default_value = bpy.data.collections[node.label]
                except:
                    print("Failed to set:", gntree.name, node.name, "to:", node.label)
            elif node.type == 'STORE_NAMED_ATTRIBUTE':
                node.inputs[2].default_value = node.label
            elif node.type == 'INPUT_ATTRIBUTE':
                node.inputs[0].default_value = node.label
                
    return 0


for ob in bpy.context.selected_objects:
    for mod in ob.modifiers:
        if mod.type == 'NODES':
            break_dependency = gn_gather_deps(mod.node_group)
            #restore_dependency = gn_restore_deps(mod.node_group)

print("FINISHED")