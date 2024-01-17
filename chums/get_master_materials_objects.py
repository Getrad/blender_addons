import bpy
import os

iobjs = 1

source_file = "Y:\\projects\\CHUMS_Onsite\\_prod\\assets\\environments\\env_mooseRiver_01\\30_texture\\projects\\blender\\workfiles\\test\\env_mooseRiver_01_v108_river_labelled.blend"
target_objs = ["waterplane_main","waterplane_util"]
target_mtls = ["Ground_main","Water_util"]

if iobjs and os.path.exists(source_file):
    with bpy.data.libraries.load(source_file, link=False) as (data_src, data_dst):
        data_dst.objects = data_src.objects
    for ob in data_dst.objects:
        for obname in target_objs:
            if obname in ob.name:
                bpy.context.scene.collection.children.link(ob)
        
if imtls and os.path.exists(source_file):
    with bpy.data.libraries.load(source_file, link=False) as (data_src, data_dst):
        data_dst.materials = data_src.materials
    for ob in data_dst.materials:
        for obname in target_mtls:
            if obname in ob.name:
                bpy.context.scene.collection.children.link(ob)