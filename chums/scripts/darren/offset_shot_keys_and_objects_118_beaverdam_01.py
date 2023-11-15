import maya.cmds as cmds

#ANCHOR_COORDS = {'pos': [-11.939, 0, 12.117], 'rot': [0, 53.041, 0]}
REPO_COORDS = {'pos': [-11.939, 0, 12.117], 'rot': [0, 53.041, 0]}

# Function to get the coordinates of an object by its name
def get_coordinates(object_name):
    if cmds.objExists(object_name):
        pos = cmds.xform(object_name, query=True, worldSpace=True, translation=True)
        rot = cmds.xform(object_name, query=True, worldSpace=True, rotation=True)
        scale = cmds.xform(object_name, query=True, worldSpace=True, scale=True)
        coordinates = {'pos': pos, 'rot': rot, 'scale': scale}
        return coordinates

# Remove Reference by Name
def removeRef(reference_name): 
    try:
        reference_node = cmds.referenceQuery(reference_name, referenceNode=True)
        if reference_node:
            cmds.file(referenceNode=reference_node, removeReference=True)
    except RuntimeError:
        pass

# Import new reference based HARDCODED PATH FOR NOW 
def importRef():
    # grossly hardcoded for the moment :(
    newEnvPath = r"Y:/projects/CHUMS/_prod/_shotgrid/chums_season_1/sequences/chm_ep118_sc13/chm_ep118_sc13_sh000/LAY/publish/maya/scene.v003.ma"
    # Replace with the desired namespace
    namespace = "chm_ep118_sc13_sh000_scene_ma"
    # Import the reference
    cmds.file(newEnvPath, r=True, ns=namespace, f=True)

# Match two object transforms - target to source
def match_transforms(source_object, target_object):
    try:
        # Get the translation, rotation, and scale of the source object
        translation = cmds.xform(source_object, query=True, translation=True, worldSpace=True)
        rotation = cmds.xform(source_object, query=True, rotation=True, worldSpace=True)
        scale = cmds.xform(source_object, query=True, scale=True, relative=True)
        # Set the translation, rotation, and scale of the target object to match the source object
        cmds.xform(target_object, translation=translation, worldSpace=True)
        cmds.xform(target_object, rotation=rotation, worldSpace=True)
    except Exception as e:
        print(f"An error occurred: {e}")

# Get REPO_COORDS by comparing 2 object pos and rot values
def get_offsets(coords1, coords2):
    diff_coords = {'pos': [abs(abs(coords1['pos'][0]) - abs(coords2['pos'][0])),\
                         abs(abs(coords1['pos'][1]) - abs(coords2['pos'][1])),\
                         abs(abs(coords1['pos'][2]) - abs(coords2['pos'][2]))],\
                 'rot': [abs(abs(coords1['rot'][0]) - abs(coords2['rot'][0])),\
                         abs(abs(coords1['rot'][1]) - abs(coords2['rot'][1])),\
                         abs(abs(coords1['rot'][2]) - abs(coords2['rot'][2]))]\
                }
    print("diff_coords = ", diff_coords)
    repo_coords = {'pos': [((diff_coords['pos'][0]) if (coords1['pos'][0] >= coords2['pos'][0]) else (diff_coords['pos'][0]*-1)),\
                         ((diff_coords['pos'][1]) if (coords1['pos'][1] >= coords2['pos'][1]) else (diff_coords['pos'][1]*-1)),\
                         ((diff_coords['pos'][2]) if (coords1['pos'][2] >= coords2['pos'][2]) else (diff_coords['pos'][2]*-1))],\
                 'rot': [((diff_coords['rot'][0]) if (coords1['rot'][0] >= coords2['rot'][0]) else (diff_coords['rot'][0]*-1)),\
                         ((diff_coords['rot'][1]) if (coords1['rot'][1] >= coords2['rot'][1]) else (diff_coords['rot'][1]*-1)),\
                         ((diff_coords['rot'][2]) if (coords1['rot'][2] >= coords2['rot'][2]) else (diff_coords['rot'][2]*-1))]\
                }
    print("repo_coords = ", repo_coords)
    return repo_coords

# Get current old_sel_obj object to set base source object andget ANCHOR_COORDS
old_sel_obj = cmds.ls(sl=True, long=True)[0]
old_sel_name = old_sel_obj.split("|")[-1]
old_sel_namespace = old_sel_obj.split("|")[0]
print("old_sel_name: ", old_sel_name)
print("old_sel_namespace: ", old_sel_namespace)
selco = get_coordinates(old_sel_obj)
old_sel_coords = selco
ANCHOR_COORDS = {'pos': old_sel_coords['pos'], 'rot': old_sel_coords['rot']}
print("ANCHOR_COORDS: ", ANCHOR_COORDS)


# Remove env and import zero shot
removeRef("env_beaverdam_scene_maRN")
importRef()

# Get new objects/coords
print("old_sel_name: ", old_sel_name)
new_sel_name = ("chm_ep118_sc13_sh000_scene_ma:" + old_sel_name)
new_sel = cmds.ls(new_sel_name, long=True)
cmds.select(new_sel)
new_sel_obj = cmds.ls(sl=True, long=True)[0]
print("new_sel_obj: ", new_sel_obj)
new_sel_namespace = new_sel_obj.split("|")[0]
print("new_sel_namespace: ", new_sel_namespace)
new_sel_coords = get_coordinates(new_sel_obj)
NEW_OBJ_COORDS = {'pos': new_sel_coords['pos'], 'rot': new_sel_coords['rot']}
print("NEW_OBJ_COORDS: ", NEW_OBJ_COORDS)
#REPO_COORDS = get_offsets(NEW_OBJ_COORDS, ANCHOR_COORDS)
REPO_COORDS = NEW_OBJ_COORDS
print("REPO_COORDS: ", REPO_COORDS)

# Create a new empty group
xformGrpName = "grp_repo_xform_tmp"
xformGrp = cmds.group(empty=True, name=xformGrpName)
cmds.xform(xformGrp, translation=ANCHOR_COORDS['pos'], worldSpace=True)
cmds.xform(xformGrp, rotation=ANCHOR_COORDS['rot'], worldSpace=True)

# List all nodes that contain the string "CNT_GOD" and are of type "nurbsCurve"
allcurves = cmds.ls(type="nurbsCurve")
curves = [curve for curve in allcurves if 'GOD' in curve and not 'env_' in curve and not 'chm_ep118_sc13_sh000' in curve]
# Find the transform nodes connected to these curves.
curve_transforms = [cmds.listRelatives(curve, parent=True, fullPath=True)[0] for curve in curves if cmds.listRelatives(curve, parent=True, fullPath=True)]

# Get all cameras in the scene
all_cameras = cmds.ls(type='camera')
# Filter the list to include only those containing 'cam' or 'chm' in their name
filtered_cameras = [camera for camera in all_cameras if 'cam' in camera or 'chm' in camera and not()]
for cam_shape in filtered_cameras:
    # Get the transform node associated with the shape node
    cam = cmds.listRelatives(cam_shape, parent=True)[0]
    print(cam)
    coords = get_coordinates(cam)
    cube = cmds.polyCube(name=f"XFORMBUFFER_{cam}")
    cmds.xform(cube[0], translation=coords['pos'])
    cmds.xform(cube[0], rotation=coords['rot'])
    cmds.xform(cube[0], scale=coords['scale'])
    cmds.parent(cube, xformGrp)
    

# place a cube at the current xform of each god ctrl (avoid changing rigging hierarchy)
for i, cnt in enumerate(curve_transforms):
    print(cnt)
    name=curves[i]
    coords = get_coordinates(cnt)
    cube = cmds.polyCube(name=f"XFORMBUFFER_{name}")
    cmds.xform(cube[0], translation=coords['pos'])
    cmds.xform(cube[0], rotation=coords['rot'])
    cmds.xform(cube[0], scale=coords['scale'])
    cmds.parent(cube, xformGrp) 
    
# repo the xform grp
cmds.xform(xformGrp, translation=REPO_COORDS['pos'], worldSpace=True)
cmds.xform(xformGrp, rotation=REPO_COORDS['rot'], worldSpace=True)

# delete the parent to put buffer geo into absolute xforms
children = cmds.listRelatives(xformGrpName, children=True, fullPath=True)
if children:
    cmds.parent(children, world=True)
cmds.delete(xformGrpName)

# match the xform of the god ctrls to the xformbuffer cubes
for i, cnt in enumerate(curve_transforms):
    print("cnt: ", cnt)
    name=curves[i]
    source_object = f'XFORMBUFFER_{name}'
    target_object = cnt
    print("source_object: ", source_object)
    print("target_object: ", target_object)
    match_transforms(source_object, target_object)

# repo the camera
for cam_shape in filtered_cameras:
    print(cam_shape)
    cam = cmds.listRelatives(cam_shape, parent=True)[0]
    source_object = f'XFORMBUFFER_{cam_shape[:-5]}'
    print("source_object: ", source_object)
    target_object = cam
    print("target_object: ", target_object)
    cmds.setAttr(f'{target_object}.translateX', lock=False)
    cmds.setAttr(f'{target_object}.translateY', lock=False)
    cmds.setAttr(f'{target_object}.translateZ', lock=False)
    cmds.setAttr(f'{target_object}.rotateX', lock=False)
    cmds.setAttr(f'{target_object}.rotateY', lock=False)
    cmds.setAttr(f'{target_object}.rotateZ', lock=False)
    match_transforms(source_object, target_object)
    cmds.setAttr(f'{target_object}.translateX', lock=True)
    cmds.setAttr(f'{target_object}.translateY', lock=True)
    cmds.setAttr(f'{target_object}.translateZ', lock=True)
    cmds.setAttr(f'{target_object}.rotateX', lock=True)
    cmds.setAttr(f'{target_object}.rotateY', lock=True)
    cmds.setAttr(f'{target_object}.rotateZ', lock=True)
'''
# delete tmp work
selected_objects = cmds.ls(selection=True)
if selected_objects:
    cmds.delete(selected_objects)
    '''