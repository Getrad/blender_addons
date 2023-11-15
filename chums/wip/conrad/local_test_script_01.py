import maya.cmds as cmds

def get_coordinates(object_name):
    if cmds.objExists(object_name):
        pos = cmds.xform(object_name, query=True, translation=True)
        rot = cmds.xform(object_name, query=True, rotation=True)
        scale = cmds.xform(object_name, query=True, scale=True)
        coordinates = {'pos': pos, 'rot': rot, 'scale': scale}
        return coordinates

old_sel_obj = cmds.ls(sl=True, long=True)[0]
old_sel_name = old_sel_obj.split("|")[-1]
old_sel_namespace = old_sel_obj.split("|")[0]
print("old_sel_name: ", old_sel_name)
print("old_sel_namespace(length): ", old_sel_namespace, "(", len(old_sel_namespace), ")")
selco = get_coordinates(old_sel_obj)
sel_coords = selco
ANCHOR_COORDS = {'pos': sel_coords['pos'], 'rot': sel_coords['rot']}
print("ANCHOR_COORDS: ", ANCHOR_COORDS)

coords1 = {'pos': selco['pos'], 'rot': selco['rot']}
coords2 = {'pos': [-2740.248, 0.0, 458.348], 'rot': [0.0, 0.0, 0.0]}
print(coords1)
print(coords2)
repo_test = {'pos': [(coords1['pos'][0] - coords2['pos'][0]),\
                     (coords1['pos'][1] - coords2['pos'][1]),\
                     (coords1['pos'][2] - coords2['pos'][2])],\
             'rot': [(coords1['rot'][0] - coords2['rot'][0]),\
                     (coords1['rot'][1] - coords2['rot'][1]),\
                     (coords1['rot'][2] - coords2['rot'][2])]\
            }
print(repo_test)