import maya.cmds as cmds

ANCHOR_COORDS = {'pos': [-11.939, 0, 12.117], 'rot': [0, 53.041, 0]}
REPO_COORDS = {'pos': [-11.939, 0, 12.117], 'rot': [0, 53.041, 0]}

# Function to get the coordinates of an object by its name
def get_coordinates(object_name):
    if cmds.objExists(object_name):
        pos = cmds.xform(object_name, query=True, translation=True)
        rot = cmds.xform(object_name, query=True, rotation=True)
        scale = cmds.xform(object_name, query=True, scale=True)
        coordinates = {'pos': pos, 'rot': rot, 'scale': scale}
        return coordinates

# Get current selected_obj object to set base source object andget ANCHOR_COORDS
selected_obj = cmds.ls(sl=True, long=True)[0]
selco = get_coordinates(selected_obj)
ANCHOR_COORDS = {'pos': selco['pos'], 'rot': selco['rot']}


def removeRef(reference_name): 
    try:
        reference_node = cmds.referenceQuery(reference_name, referenceNode=True)
        if reference_node:
            cmds.file(referenceNode=reference_node, removeReference=True)
    except RuntimeError:
        pass
        
removeRef("env_beaverdam_scene_maRN")
        
def importRef():
    # grossly hardcoded for the moment :(
    newEnvPath = r"Y:/projects/CHUMS/_prod/_shotgrid/chums_season_1/sequences/chm_ep118_sc13/chm_ep118_sc13_sh000/LAY/publish/mayascene.v003.ma"
    # Replace with the desired namespace
    namespace = "chm_ep118_sc13_sh000"
    # Import the reference
    cmds.file(newEnvPath, r=True, ns=namespace, f=True)

importRef()

# If selected_obj to capture diff_coords
selected_obj = cmds.ls(sl=True, long=True)[0]
selco = get_coordinates(selected_obj)
DIFF_COORDS = {'pos': selco['pos'], 'rot': selco['rot']}
prin(DIFF_CCORDS)


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

# Create a new empty group
xformGrpName = "grp_repo_xform_tmp"
xformGrp = cmds.group(empty=True, name=xformGrpName)
cmds.xform(xformGrp, translation=ANCHOR_COORDS['pos'], worldSpace=True)
cmds.xform(xformGrp, rotation=ANCHOR_COORDS['rot'], worldSpace=True)

# List all nodes that contain the string "CNT_GOD" and are of type "nurbsCurve"
curves = cmds.ls(type="nurbsCurve")
curves = [curve for curve in curves if 'GOD' in curve and not 'env_' in curve]
# Find the transform nodes connected to these curves.
curve_transforms = [cmds.listRelatives(curve, parent=True, fullPath=True)[0] for curve in curves if cmds.listRelatives(curve, parent=True, fullPath=True)]

# Get all cameras in the scene
all_cameras = cmds.ls(type='camera')
# Filter the list to include only those containing 'cam' or 'chm' in their name
filtered_cameras = [camera for camera in all_cameras if 'cam' in camera or 'chm' in camera]
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
    print(cnt)
    name=curves[i]
    source_object = f'XFORMBUFFER_{name}'
    target_object = cnt
    match_transforms(source_object, target_object)

# repo the camera
for cam_shape in filtered_cameras:
    print(cam_shape)
    cam = cmds.listRelatives(cam_shape, parent=True)[0]
    source_object = f'XFORMBUFFER_{cam_shape[:-5]}'
    print(source_object)
    target_object = cam
    cmds.setAttr(f'{cam}.translateX', lock=False)
    cmds.setAttr(f'{cam}.translateY', lock=False)
    cmds.setAttr(f'{cam}.translateZ', lock=False)
    cmds.setAttr(f'{cam}.rotateX', lock=False)
    cmds.setAttr(f'{cam}.rotateY', lock=False)
    cmds.setAttr(f'{cam}.rotateZ', lock=False)
    match_transforms(source_object, target_object)
    cmds.setAttr(f'{cam}.translateX', lock=True)
    cmds.setAttr(f'{cam}.translateY', lock=True)
    cmds.setAttr(f'{cam}.translateZ', lock=True)
    cmds.setAttr(f'{cam}.rotateX', lock=True)
    cmds.setAttr(f'{cam}.rotateY', lock=True)
    cmds.setAttr(f'{cam}.rotateZ', lock=True)
    
# delete tmp work
selected_objects = cmds.ls(selection=True)
if selected_objects:
    cmds.delete(selected_objects)