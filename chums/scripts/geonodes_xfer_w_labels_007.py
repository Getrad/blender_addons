import bpy

print("\n\nSTART")
# node_types = ['OBJECT_INFO','COLLECTION_INFO','STORE_NAMED_ATTRIBUTE','INPUT_ATTRIBUTE']
node_types = ['OBJECT_INFO','COLLECTION_INFO','INPUT_ATTRIBUTE']

def gn_gather_deps(gntree):
    gn_deps = []
    for node in gntree.nodes:
        if node.type in node_types:
            if node.type == 'STORE_NAMED_ATTRIBUTE':
                print("\t", node.name, node.type)
                if (len(node.inputs[2].default_value) > 1):
                    print('\t',node.label, node.inputs[2].identifier, node.inputs[2].default_value)
                    gn_deps.append((node.name, node.inputs[2].default_value))
                    node.label = node.inputs[2].default_value
                    node.inputs[2].default_value = ''
            elif node.type == 'INPUT_ATTRIBUTE':
                if (len(node.inputs[0].default_value) > 1):
                    print('\t',node.label, node.inputs[0].identifier, node.inputs[0].default_value)
                    gn_deps.append((node.name, node.inputs[0].default_value))
                    node.label = str(node.inputs[0].default_value)
                    node.inputs[0].default_value = ''
            elif (node.inputs[0].default_value is not None):
                gn_deps.append((node.name, node.inputs[0].default_value.name))
                node.label = node.inputs[0].default_value.name
                node.inputs[0].default_value = None
            elif node.type == 'GROUP' and node.node_tree is not None:
                gn_gather_deps(node.node_tree)
            else:
                print('\t',node.name, ' not managed - skipping')
    return gn_deps

def gn_restore_deps(gntree):
    colls = []
    objs = []
    for node in gntree.nodes:
        if node.type in node_types:
            #print(gntree.name, node.name, node.type, node.label)
            if node.type == 'OBJECT_INFO':
                try:
                    node.inputs[0].default_value = bpy.data.objects[node.label]
                except:
                    #print("Failed to set:", gntree.name, node.name, node.inputs[0].identifier, "to:", node.label)
                    objs.append(node.label)
                    #print("OBJ:\t",node.label)
            elif node.type == 'COLLECTION_INFO':
                try:
                    node.inputs[0].default_value = bpy.data.collections[node.label]
                except:
                    #print("Failed to set:", gntree.name, node.name, "to:", node.label)
                    colls.append(node.label)
                    #print("COLL:\t", node.label)
            elif node.type == 'STORE_NAMED_ATTRIBUTE':
                node.inputs[2].default_value = node.label
            elif node.type == 'INPUT_ATTRIBUTE':
                node.inputs[0].default_value = node.label
            elif node.type == 'GROUP' and node.node_tree is not None:
                gn_restore_deps(node.node_tree)
                
    return (colls, objs)


for ob in bpy.context.selected_objects:
    mycolls = []
    myobjs = []
    for mod in ob.modifiers:
        if mod.type == 'NODES':
            print(mod.name, mod.node_group)
            #if mod.node_group.users > 1:
            #    mod.node_group = mod.node_group.copy()
            #break_dependency = gn_gather_deps(mod.node_group)
            restore_dependency = gn_restore_deps(mod.node_group)
            mycolls.extend(restore_dependency[0])
            myobjs.extend(restore_dependency[1])
    print(ob.name)
    print("\nmycolls:")
    for a in mycolls: print(a)
    print("\nmyobjs:")
    for a in myobjs: print(a)
    

print("FINISHED")