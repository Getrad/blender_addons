import bpy

bpy.collections['sh000_env'].override_create(remap_local_usages=True)
bpy.collections['sh000_env'].override_hierarchy_create(bpy.context.scene, bpy.context.view_layer)
bpy.collections['sh000_env'].all_objects['env.loonbeach:ground'].override_create(remap_local_usages=True)
bpy.collections['sh000_env'].all_objects['env.loonbeach:ground'].material_slots[0].material.override_create(remap_local_usages=True)

print('complete')