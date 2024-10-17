# from ChatGPT

import maya.cmds as cmds

def reference_align_constrain_bake(reference_path, target_namespace, target_object_name):
    selected = cmds.ls(selection=True)

    if not selected:
        cmds.error("Please select an object in the current scene.")
        return

    selected_object = selected[0]

    try:
        ref_node = cmds.file(reference_path, reference=True, namespace=target_namespace)
        print(f"Referenced file: {reference_path}")
    except Exception as e:
        cmds.error(f"Failed to reference file: {str(e)}")
        return

    target_object = f'{target_namespace}:{target_object_name}'

    # Verify if the object exists in the referenced file
    if not cmds.objExists(target_object):
        cmds.error(f"Target object '{target_object}' not found in referenced file.")
        return
    print(f"Target object found: {target_object}")

    # Align the target object to the selected object
    cmds.delete(cmds.pointConstraint(selected_object, target_object))  # Align position
    cmds.delete(cmds.orientConstraint(selected_object, target_object))  # Align orientation
    cmds.delete(cmds.scaleConstraint(selected_object, target_object))   # Align scale
    print(f"Aligned {target_object} to {selected_object}")

    # Constrain the target object to the selected object
    cmds.parentConstraint(selected_object, target_object, mo=False)
    cmds.scaleConstraint(selected_object, target_object, mo=False)
    print(f"Constrained {target_object} to {selected_object}")

    # Define the frame range for baking (adjust as needed)
    start_frame = cmds.playbackOptions(query=True, minTime=True)
    end_frame = cmds.playbackOptions(query=True, maxTime=True)

    # Bake the target object (translation, rotation, and scale)
    #cmds.bakeResults(target_object, simulation=True, time=(start_frame, end_frame), 
    #                 sampleBy=1, oversamplingRate=1, disableImplicitControl=True, 
    #                 preserveOutsideKeys=True, sparseAnimCurveBake=False, 
    #                 removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False, 
    #                 minimizeRotation=True, at=['translate', 'rotate', 'scale'])

    # OVERRIDE: For the prp_salt_01 asset in epP211_sc03 override SCALE, so skip baking and set later
    cmds.bakeResults(target_object, simulation=True, time=(start_frame, end_frame), 
                     sampleBy=1, oversamplingRate=1, disableImplicitControl=True, 
                     preserveOutsideKeys=True, sparseAnimCurveBake=False, 
                     removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False, 
                     minimizeRotation=True, at=['translate', 'rotate'])

    # Clean up by removing the constraints after baking
    cmds.delete(target_object, constraints=True)
    print(f"Successfully baked the simulation for {target_object}.")

    # Set scale that was NOT baked
    set_object_scale(target_object, scale_values=(1.4566, 1.4566, 1.4566))

    # Remove selected objects reference
    remove_reference_by_selection(selected_object)
# Example usage:
# reference_align_constrain_bake('C:/path/to/reference_file.mb', 'target_object_name')


def remove_reference_by_selection(input_selection):
    # Step 1: Get the current selection
    #selected = cmds.ls(selection=True)
    selected = input_selection
    
    if not input_selection:
        cmds.error("Please select an object that is part of a reference.")
        return

    # Step 2: Check if the selected object is part of a reference
    if not cmds.referenceQuery(input_selection, isNodeReferenced=True):
        cmds.error(f"The selected object '{selected_object}' is not part of a reference.")
        return

    # Step 3: Get the reference node from the selected object
    try:
        reference_node = cmds.referenceQuery(input_selection, referenceNode=True)
        print(f"Reference node for selected object: {reference_node}")
    except Exception as e:
        cmds.error(f"Failed to find reference node for the selected object: {str(e)}")
        return

    # Step 4: Get the file path associated with the reference node
    reference_path = cmds.referenceQuery(reference_node, filename=True)
    print(f"Reference file path: {reference_path}")

    # Step 5: Remove the reference
    try:
        cmds.file(reference_path, removeReference=True)
        print(f"Successfully removed reference: {reference_path}")
    except Exception as e:
        cmds.error(f"Failed to remove reference: {str(e)}")
# Example usage:
#remove_reference_by_selection()


def set_object_scale(object_name=None, scale_values=(1, 1, 1)):
    """
    Sets the scale for a given object in the scene.

    :param object_name: Name of the object to scale. If None, uses the currently selected object.
    :param scale_values: A tuple with 3 values representing the X, Y, and Z scales (default is (1, 1, 1)).
    """
    # If no object is provided, use the currently selected object
    if object_name is None:
        selected = cmds.ls(selection=True)
        if not selected:
            cmds.error("No object selected or provided. Please select an object or pass its name.")
            return
        object_name = selected[0]

    # Check if the object exists
    if not cmds.objExists(object_name):
        cmds.error(f"Object '{object_name}' does not exist in the scene.")
        return

    # Set the scale for the object
    cmds.scale(scale_values[0], scale_values[1], scale_values[2], object_name)
    print(f"Set scale of {object_name} to {scale_values}")
# Example usage:
# Set the scale of the currently selected object to (2, 2, 2)
# set_object_scale(scale_values=(2, 2, 2))
# Or set the scale of a specific object by name (e.g., 'pCube1') to (3, 3, 3)
# set_object_scale('pCube1', scale_values=(3, 3, 3))


def remove_reference_by_name(reference_node_name):
    # Check if the reference node exists
    if not cmds.objExists(reference_node_name):
        cmds.error(f"Reference node '{reference_node_name}' does not exist.")
        return

    # Check if the node is a valid reference
    if not cmds.referenceQuery(reference_node_name, isNodeReferenced=True):
        cmds.error(f"'{reference_node_name}' is not a valid reference node.")
        return

    # Get the reference file path
    reference_path = cmds.referenceQuery(reference_node_name, filename=True)
    print(f"Removing reference: {reference_path}")

    # Remove the reference
    try:
        cmds.file(reference_path, removeReference=True)
        print(f"Successfully removed reference: {reference_node_name}")
    except Exception as e:
        cmds.error(f"Failed to remove reference: {str(e)}")
# Example usage:
# remove_reference_by_name('yourReferenceNodeName')

reference_align_constrain_bake("X:/projects/chums_season2/anim/_prod/_shotgrid/chums_season2/assets/Prop/prp_salt_01/RIG/publish/maya/scene.v004.ma", 'prp_salt_01_scene_ma', 'CNT_GROUND')
