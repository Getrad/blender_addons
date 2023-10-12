import bpy

scn = bpy.context.scene
vlyr = bpy.context.view_layer

bpy.data.collections['sh000_env'].override_create(remap_local_usages=True)
bpy.data.collections['sh000_env'].override_hierarchy_create(scn, vlyr)
bpy.data.collections['sh000_env'].all_objects['env.loonbeach:ground'].data.override_create(remap_local_usages=True)
bpy.data.collections['sh000_env'].all_objects['env.loonbeach:ground'].data.override_hierarchy_create(scn, vlyr)
my_lib = bpy.data.collections['sh000_env'].all_objects['env.loonbeach:ground'].material_slots[0].material.override_create(remap_local_usages=True)
my_mtl = bpy.data.collections['sh000_env'].all_objects['env.loonbeach:ground'].material_slots[0].material.make_local()
#bpy.data.collections['sh000_env'].all_objects['env.loonbeach:ground'].material_slots[0].material = my_mtl

def set_override_frames(mat, frame_count, offset):
    #bpy.data.materials["env_loonbeach_01:ground_footprints"].node_tree.nodes["env_loonbeach_01:comp_sequence"].image_user.frame_duration = frame_count
    mat.node_tree.nodes["Image Texture.001"].image_user.frame_duration = frame_count
    mat.node_tree.nodes["Image Texture.001"].image_user.frame_start = (1 - offset)

set_override_frames(my_mtl, 100, 321)

print('complete')