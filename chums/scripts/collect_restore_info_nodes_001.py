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


for ob in bpy.context.selected_objects:
    for mod in ob.modifiers:
        if mod.type == 'NODES':
            my_deps = gn_gather_deps(mod.node_group)
            print(my_deps)
            gn_restore_deps(mod.node_group)

    

    