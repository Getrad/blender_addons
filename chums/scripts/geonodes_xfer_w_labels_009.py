import bpy

gather_restore = 0  #gather(0) restore(1) update(2)

print("\n\nSTART")
# node_types = ['OBJECT_INFO','COLLECTION_INFO','STORE_NAMED_ATTRIBUTE','INPUT_ATTRIBUTE']
node_types = ['OBJECT_INFO','COLLECTION_INFO','INPUT_ATTRIBUTE']

def gn_update_labels(gntree):
    gn_deps = []
    colls = []
    objs = []
    for node in gntree.nodes:
        if node.type in node_types:
            if node.type == 'STORE_NAMED_ATTRIBUTE':
                print("\t", node.name, node.type)
                if (len(node.inputs[2].default_value) > 1):
                    print('\t',node.label, node.inputs[2].identifier, node.inputs[2].default_value)
                    gn_deps.append((node.name, node.inputs[2].default_value))
                    node.label = node.inputs[2].default_value
                    print("UPDATE:\t", node.name, " \tto\t", node.inputs[2].default_value)
            elif node.type == 'INPUT_ATTRIBUTE':
                if (len(node.inputs[0].default_value) > 1):
                    print('\t',node.label, node.inputs[0].identifier, node.inputs[0].default_value)
                    gn_deps.append((node.name, node.inputs[0].default_value))
                    node.label = str(node.inputs[0].default_value)
                    print("UPDATE:\t", node.name, " \tto\t", node.inputs[0].default_value)
            elif (node.inputs[0].default_value is not None):
                gn_deps.append((node.name, node.inputs[0].default_value.name))
                #node.label = node.inputs[0].default_value.name
                if node.type == node_types[1]:
                    if not(node.label == 'heatmapCollection'):
                        node.label = node.inputs[2].default_value
                    else:
                        node.label = 'heatmapCollection'
                    colls.append(node.label)
                elif node.type == node_types[0]:
                    node.label = node.inputs[0].default_value.name
                    objs.append(node.label)
                print("UPDATE:\t", node.name, " \tto\t", node.label)
            elif node.type == 'GROUP' and node.node_tree is not None:   #recursive
                gn_gather_deps(node.node_tree)
            else:
                print('\t',node.name, ' not managed - skipping')
    return (colls, objs)

def gn_gather_deps(gntree):
    gn_deps = []
    colls = []
    objs = []
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
                print("\t", node.name, node.type)
                if (len(node.inputs[0].default_value) > 1):
                    #print('\t',node.label, node.inputs[0].identifier, node.inputs[0].default_value)
                    gn_deps.append((node.name, node.inputs[0].default_value))
                    node.label = str(node.inputs[0].default_value)
                    node.inputs[0].default_value = ''
            elif (node.inputs[0].default_value is not None):
                print("\t", node.name, node.type)
                gn_deps.append((node.name, node.inputs[0].default_value.name))
                #node.label = node.inputs[0].default_value.name
                if node.type == node_types[1]:
                    if not(node.label == 'heatmapCollection'):
                        node.label = node.inputs[0].default_value.name
                    else:
                        node.label = 'heatmapCollection'
                    colls.append(node.label)
                elif node.type == node_types[0]:
                    node.label = node.inputs[0].default_value.name
                    objs.append(node.label)
                node.inputs[0].default_value = None
            elif node.type == 'GROUP' and node.node_tree is not None:
                gn_gather_deps(node.node_tree)
            else:
                print('\t',node.name, ' not managed or empty and unused - skipping')
    return (colls, objs)

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
                    objs.append(node.label)
            elif node.type == 'COLLECTION_INFO':
                if node.label == 'heatmapCollection':
                    if bpy.data.collections['sh000_heatmaps_base']:
                        node.inputs[0].default_value = bpy.data.collections['sh000_heatmaps_base']
                    colls.append('sh000_heatmaps_base')
                else:
                    try:
                        node.inputs[0].default_value = bpy.data.collections[node.label]
                    except:
                        colls.append(node.label)
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
            print(mod.name, mod.node_group.name)
            if gather_restore == 0:
                break_dependency = gn_gather_deps(mod.node_group)
                mycolls.extend(break_dependency[0])
                myobjs.extend(break_dependency[1])
            elif gather_restore == 1:
                restore_dependency = gn_restore_deps(mod.node_group)
                mycolls.extend(restore_dependency[0])
                myobjs.extend(restore_dependency[1])
            else:
                update_dependency = gn_update_labels(mod.node_group)
                mycolls.extend(update_dependency[0])
                myobjs.extend(update_dependency[1])
                
    print(ob.name)
    print("\nmycolls:")
    for a in mycolls: print(a)
    print("\nmyobjs:")
    for a in myobjs: print(a)
    

print("FINISHED")