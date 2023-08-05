######################## NOTES ##############################
# v0.0.1 - first pass at addon to provide listing of file or selection images

bl_info = {
    "name": "Show Image Paths",
    "author": "Conrad Dueck",
    "version": (0,1,0),
    "blender": (3, 3, 1),
    "location": "View3D > Tool Shelf > Chums",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}


import bpy
import os
from pathlib import Path

# GLOBAL VARIABLES
vsn = '0.1.0'

# FUNCTIONS
def get_object_images(obj):
    obj_imgs = {}

    return obj_imgs

# CLASSES
# OPERATOR BUTTON_OT_imagepathsshow
class BUTTON_OT_imagepathsshow(bpy.types.Operator):
    '''Show Image Paths'''
    bl_idname = "imagepaths.show"
    bl_label = "Show Paths"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("************  START SHOW PATHS ************")
        output_text = ""
        if bpy.context.scene.imagepaths_selected:
            the_objs = bpy.context.selected_objects
        else:
            the_objs = bpy.data.objects
        for o in the_objs:
            for ms in o.material_slots:
                m = ms.material
                if m and m.use_nodes:
                    for node in m.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            print('\nObject Name:', o.name, '\nMaterial Name:', m.name, '\nNode Name:', node.name, '\nImage Filepath:', node.image.filepath)
        print("************  DONE SHOW PATHS ************")
        return{'FINISHED'}
   
# PANEL VIEW3D_PT_imagepathspanel
class VIEW3D_PT_imagepathspanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Show Image Paths "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(bpy.context.scene, "imagepaths_selected")
        layout.operator("imagepaths.show", text=(BUTTON_OT_imagepathsshow.bl_label))
        
        

# REGISTER
classes = [ VIEW3D_PT_imagepathspanel,
           BUTTON_OT_imagepathsshow ]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.imagepaths_selected = bpy.props.BoolProperty(
        name = "Only Selected",
        description = "Show only images used in MATERIALS on SELECTED objects.",
        default = True)
    
    


# UNREGISTER
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.imagepaths_selected


if __name__ == "__main__":
    register()
