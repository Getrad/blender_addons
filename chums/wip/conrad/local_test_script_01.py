import maya.cmds as cmds

def get_coordinates(object_name):
    if cmds.objExists(object_name):
        pos = cmds.xform(object_name, query=True, translation=True)
        rot = cmds.xform(object_name, query=True, rotation=True)
        scale = cmds.xform(object_name, query=True, scale=True)
        coordinates = {'pos': pos, 'rot': rot, 'scale': scale}
        return coordinates

selected = cmds.ls(sl=True, long=True)[0]
print(selected)
selco = get_coordinates(selected)
coords1 = {'pos': selco['pos'], 'rot': selco['rot']}
coords2 = {'pos': [-2740.248, 0.0, 458.348], 'rot': [0.0, 0.0, 0.0]}
print(coords1)
print(coords2)
#repo_test = {'pos': (selco['pos']-[-2740.248, 0.0, 458.348]), 'rot': (selco['rot']-[0.0, 0.0, 0.0])}
#print(repo_test)