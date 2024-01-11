import bpy

print("\n\nSTART")

def gn_gather_deps(gntree):
    gn_deps = []
    for node in gntree.nodes:
        if node.type in ['OBJECT_INFO','COLLECTION_INFO','STORE_NAMED_ATTRIBUTE']:
            print(node.name)
            #print('\t',node.label, node.inputs[0].default_value.name)
            if node.type == 'STORE_NAMED_ATTRIBUTE':
                gn_deps.append((node.name, node.inputs[2].default_value))
                node.label = node.inputs[2].default_value
                node.inputs[2].default_value = ''
            else:
                gn_deps.append((node.name, node.inputs[0].default_value.name))
                node.label = node.inputs[0].default_value.name
                node.inputs[0].default_value = None
    return gn_deps

def gn_restore_deps(gntree):
    gn_deps = []
    for node in gntree.nodes:
        if node.type in ['OBJECT_INFO','COLLECTION_INFO','STORE_NAMED_ATTRIBUTE']:
            #print(node.name, node.label, node.inputs[0].default_value)
            if node.type == 'OBJECT_INFO':
                node.inputs[0].default_value = bpy.data.objects[node.label]
            if node.type == 'COLLECTION_INFO':
                node.inputs[0].default_value = bpy.data.collections[node.label]
            if node.type == 'STORE_NAMED_ATTRIBUTE':
                node.inputs[2].default_value = node.label
    return 0


for gn_tree in bpy.data.node_groups:
    #my_deps = gn_gather_deps(gn_tree)
    #print(my_deps)
    gn_restore_deps(gn_tree)

    

    