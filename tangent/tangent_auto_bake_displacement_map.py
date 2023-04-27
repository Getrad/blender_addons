bl_info = {
    "name": "Bake Displacement Map",
    "author": "james paskaruk",
    "version": (0,0,3),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > Tangent",
    "description": "Auto-bake Displacement Map",
    "warning": "",
    #"wiki_url": "",
    "tracker_url": "",
    "category": "Tangent"}

import bpy
import os
import time
from mathutils import Vector

### Functions

#def make_path_absolute(self, context):
#    if self.dmap_outputdir:
#        if self.dmap_outputdir.startswith('//'):
#            self.dmap_outputdir = (os.path.abspath(bpy.path.abspath(self.dmap_outputdir)))
#    return None


### Classes

#   OPERATOR bakedisplacementmap BAKE
class BUTTON_OT_bakedisplacementmapbake(bpy.types.Operator):
    '''Import'''
    bl_idname = "bakedisplacementmap.bake"
    bl_label = "Bake"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        if len(bpy.context.selected_objects) < 1:
            self.report({'ERROR_INVALID_INPUT'}, 'At least one object must be selected.')
            return {'CANCELLED'}
        
        for obj in bpy.context.selected_objects:

            mat = obj.active_material

            try:
                testmul = obj.modifiers['Multires']
            except:
                self.report({'ERROR_INVALID_INPUT'}, 'No Multires Modifier on selected object, Operation cancelled.')
                return {'CANCELLED'}
            try:
                testsub = obj.modifiers['Subdivision']
            except:
                obj.modifiers.new('Subdivision', 'SUBSURF')
                self.report({'INFO'}, 'Added Subdivision Modifier to selected object.')

            ##### STEP 1 
            # Create _position Image and save
            nam = obj.name + '_Position'
            res = int(bpy.context.scene.dmap_resolution)
            bpy.ops.image.new(name=nam, width=res, height=res, alpha=False, float=True)
            img = bpy.data.images[nam]
            #filepathlist = bpy.path.abspath('//').split('\\')
            #img.filepath_raw = filepathlist[0] + '\\' + filepathlist[1] + '\\' + filepathlist[2] + '\\' + filepathlist[3] + '\\' + filepathlist[4] + '\\' + filepathlist[5] + '\\' +'texture\\sandbox\\' + nam + '.exr'
            #img.filepath_raw = 'T:\\Projects\\0063_maya\\rnd\\james.paskaruk\\20190911 - Displacement Map Bake Tool\\' + nam + '.exr'
            img.filepath_raw = bpy.path.abspath('//') + nam + '.exr'
            img.file_format = 'OPEN_EXR'
            img.colorspace_settings.name = 'Non-Color'
            bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
            bpy.context.scene.render.image_settings.color_depth = '32'
            bpy.context.scene.render.image_settings.color_mode = 'RGBA'
            bpy.context.scene.render.image_settings.exr_codec = 'ZIP'
            img.save()

            ##### STEP 2
            # Append Displacement_Bake node tree
            appendpath = "T:\\Projects\\0062_maya\\rnd\\surfacing\\Blender Displacement Extraction\\Cycles_Displacement_Bake_nudelZ.blend"
            with bpy.data.libraries.load(appendpath, link=False) as (data_src, data_dst):
                data_dst.node_groups = [x for x in data_src.node_groups if x == 'Displacement Bake']

            # Add and link nodes for step 2
            uvmapnode = mat.node_tree.nodes.new("ShaderNodeUVMap")
            uvmapnode.location = Vector((-564.5703, 505.4396))
            uvmapnode.uv_map = [x for x in obj.data.uv_layers if x.active == True][0].name
            positionnode = mat.node_tree.nodes.new("ShaderNodeTexImage")
            positionnode.location = Vector((-332.6461, 718.9214))
            positionnode.image = img
            nodegroupdisbake = mat.node_tree.nodes.new("ShaderNodeGroup")
            nodegroupdisbake.name = 'Displacement Bake'
            nodegroupdisbake.location = Vector((62.2615, 587.8329))
            nodegroupdisbake.node_tree = bpy.data.node_groups['Displacement Bake']
            matoutnode = mat.node_tree.nodes['Material Output']
            matoutnode.location = Vector((289.3938, 499.8480))
            if len(matoutnode.inputs['Surface'].links) > 0:
                for lnk in matoutnode.inputs['Surface'].links:
                    mat.node_tree.links.remove(lnk)

            pos_surf_link = mat.node_tree.links.new(nodegroupdisbake.outputs['Position'], matoutnode.inputs['Surface'])
            uv_vec_link = mat.node_tree.links.new(uvmapnode.outputs['UV'], positionnode.inputs['Vector'])

            ##### STEP 3 - setup and bake
            obj.modifiers['Multires'].show_render = True
            obj.modifiers['Multires'].show_viewport = True
            obj.modifiers['Multires'].levels = 0
            obj.modifiers['Multires'].sculpt_levels = 6
            obj.modifiers['Multires'].render_levels = 6

            obj.modifiers['Subdivision'].show_render = False
            obj.modifiers['Subdivision'].show_viewport = False
            obj.modifiers['Subdivision'].levels = 0
            obj.modifiers['Subdivision'].render_levels = 0

            img.file_format = 'OPEN_EXR'
            bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
            bpy.context.scene.render.image_settings.exr_codec = 'ZIP'
            bpy.context.scene.render.image_settings.color_mode = 'RGBA'
            bpy.context.scene.render.image_settings.color_depth = '32'

            bpy.context.scene.cycles.progressive = 'BRANCHED_PATH'
            bpy.context.scene.cycles.aa_samples = 1
            bpy.context.scene.cycles.preview_aa_samples = 1
            bpy.context.scene.cycles.bake_type = 'EMIT'
            bpy.context.scene.render.bake.margin = 16
            for nod in [x for x in mat.node_tree.nodes if x != positionnode]:
                nod.select = False
                
            positionnode.select = True
            mat.node_tree.nodes.active = positionnode

            print("baking Position...")
            bpy.ops.object.bake(type='EMIT')

            ##### STEP 4
            img.save()

            # (Repeat Step 1)
            nam2 = obj.name + '_Displacement'
            res = int(bpy.context.scene.dmap_resolution)
            bpy.ops.image.new(name=nam2, width=res, height=res, alpha=False, float=True)
            img2 = bpy.data.images[nam2]
            #filepathlist = bpy.path.abspath('//').split('\\')
            #img2.filepath_raw = filepathlist[0] + '\\' + filepathlist[1] + '\\' + filepathlist[2] + '\\' + filepathlist[3] + '\\' + filepathlist[4] + '\\' + filepathlist[5] + '\\' +'texture\\sandbox\\' + nam2 + '.exr'
            #img2.filepath_raw = 'T:\\Projects\\0063_maya\\rnd\\james.paskaruk\\20190911 - Displacement Map Bake Tool\\' + nam2 + '.exr'
            img2.filepath_raw = bpy.path.abspath('//') + nam2 + '.exr'
            img2.file_format = 'OPEN_EXR'
            img2.colorspace_settings.name = 'Non-Color'
            bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
            bpy.context.scene.render.image_settings.color_depth = '32'
            bpy.context.scene.render.image_settings.color_mode = 'RGBA'
            bpy.context.scene.render.image_settings.exr_codec = 'ZIP'
            img2.save()

            displacementnode = mat.node_tree.nodes.new("ShaderNodeTexImage")
            displacementnode.location = Vector((-314.7200, 383.8278))
            displacementnode.image = img2

            mat.node_tree.links.remove(pos_surf_link)
            scalar_surf_link = mat.node_tree.links.new(nodegroupdisbake.outputs['Scalar Displacement'], matoutnode.inputs['Surface'])
            color_pos_link = mat.node_tree.links.new(positionnode.outputs['Color'], nodegroupdisbake.inputs['Position (High Resolution)'])
            uv_displace_link = mat.node_tree.links.new(uvmapnode.outputs['UV'], displacementnode.inputs['Vector'])

            for nod in [x for x in mat.node_tree.nodes if x != displacementnode]:
                nod.select = False

            displacementnode.select = True
            mat.node_tree.nodes.active = displacementnode

            ##### Step 5
            obj.modifiers['Multires'].show_render = False
            obj.modifiers['Multires'].show_viewport = False

            obj.modifiers['Subdivision'].show_render = True
            obj.modifiers['Subdivision'].show_viewport = True
            obj.modifiers['Subdivision'].levels = 0
            obj.modifiers['Subdivision'].render_levels = obj.modifiers['Multires'].render_levels

            print("baking Displacement...")
            bpy.ops.object.bake(type='EMIT')
            img2.save()

            ##### STEP 6
            obj.modifiers.remove(obj.modifiers['Multires'])
            displacemod = obj.modifiers.new('Displace', 'DISPLACE')
            displacemod.mid_level = 0
            displacemod.texture = bpy.data.textures.new('displacebake_texture', 'IMAGE')
            displacemod.texture_coords = 'UV'
            displacemod.uv_layer = [x for x in obj.data.uv_layers if x.active == True][0].name
            displacemod.strength = 0.1
            displacemod.texture.image = img2
            displacemod.texture.use_clamp = False

            obj.modifiers['Subdivision'].levels = obj.modifiers['Subdivision'].render_levels

        
        
        
        return {'FINISHED'}


#   PANEL bakedisplacementmap
class VIEW3D_PT_bakedisplacementmap(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Bake Displacement Map")
    bl_context = "objectmode"
    bl_category = 'Tangent'
    #bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, 'dmap_resolution')
        #layout.prop(context.scene, 'dmap_outputdir')
        layout.operator("bakedisplacementmap.bake", text="Run Script")


### Registration
classes = ( BUTTON_OT_bakedisplacementmapbake, VIEW3D_PT_bakedisplacementmap )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.dmap_resolution = bpy.props.EnumProperty \
        (
            name = "Resolution",
            description = "Will be used as X and Y resolution in Displacement map",
            items={
            ('512', '512', '512'),
            ('1024', '102', '1024'),
            ('2048', '2048', '2048'),
            ('3072', '3072', '3072'),
            ('4096', '4096', '4096')},
            default='2048'
        )
    #bpy.types.Scene.dmap_outputdir = bpy.props.StringProperty \
    #    (
    #    name = "Output Directory",
    #    #default = "",
    #    description = "Path for baked Displacement map output file",
    #    update = make_path_absolute,
    #    subtype = 'DIR_PATH'
    #    )

    
    
    
    
        
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.dmap_resolution
    #del bpy.types.Scene.dmap_outputdir
    
    
    
    #del bpy.types.Scene.DirSample
        
if __name__ == "__main__":
    register()

