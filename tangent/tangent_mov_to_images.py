# made in response to --
# The need to convert quicktime source stock footage to a format readable on linux
# Finish local selected objects code

bl_info = {
    "name": "Convert MOVs",
    "author": "conrad dueck",
    "version": (0,0,3),
    "blender": (3, 31, 0),
    "location": "View3D > Tool Shelf > Tangent",
    "description": "Convert Quicktimes found within a source folder to Image Sequences stored in parallel folders.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

import bpy, os, subprocess

# define variables
pathtoffmpeg = 'C:\\pipeline\\imagemagick\\ffmpeg.exe '

vsn='0.3'

#define functions
def make_path_absolute(self, context):
    if self.movtoimg_src:
        if self.movtoimg_src.startswith('//'):
            self.movtoimg_src = (os.path.abspath(bpy.path.abspath(self.movtoimg_src)))
    return None
        
def removedigits(thestring):
    for i in range(10):
        if str(i) in thestring:
            thestring = thestring.replace(str(i), '')
    return thestring

#define button operators
class BUTTON_OT_movtoimg_convert(bpy.types.Operator):
    '''Convert'''
    bl_idname = "movtoimg.convert"
    bl_label = "Convert"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('\n\nSTART CONVERT')
        theext = ('_%04d.'+bpy.context.scene.movtoimg_totype)
        thenewext = ('_0001.'+bpy.context.scene.movtoimg_totype)
        if bpy.context.scene.movtoimg_process == 'FOLDERS':
            if (len(bpy.context.scene.movtoimg_src) >= 1) and (os.path.exists(bpy.context.scene.movtoimg_src)):
                thepath = os.path.dirname(os.path.abspath(bpy.path.abspath(bpy.context.scene.movtoimg_src)))
                for dirpath, dirnames, filenames in os.walk (thepath, topdown=True):
                    for filename in filenames:
                        if filename[-4:] == '.mov':
                            if bpy.context.scene.movtoimg_cleanup:
                                tgtclean = filename[:-4].replace(' ','_')
                                tgtclean = tgtclean.lower()
                                thiscleanname = tgtclean
                            else:
                                thiscleanname = filename[:-4]
                            thispath = os.path.join(dirpath, filename)
                            thisfullpath = os.path.join(dirpath, thiscleanname)
                            newtgtpath=os.path.join(thisfullpath, thiscleanname)
                            newtgtbasename=os.path.join(newtgtpath, thiscleanname)
                            if not(os.path.exists(thisfullpath)):
                                print('output folder does not exist')
                                os.mkdir(thisfullpath)
                            if bpy.context.scene.movtoimg_totype == 'jpg':
                                tempcmd = (pathtoffmpeg+'-i '+thispath+' -qscale:v 2 '+newtgtpath+theext)
                            else:
                                tempcmd = (pathtoffmpeg+'-i '+thispath+' '+newtgtpath+theext)
                            print(tempcmd)
                            subprocess.call(tempcmd)
        elif bpy.context.scene.movtoimg_process == 'FILE':
            if (len(bpy.context.scene.movtoimg_src) >= 1) and (os.path.exists(bpy.context.scene.movtoimg_src)):
                if bpy.context.scene.movtoimg_src[-4:] == '.mov':
                    filename = os.path.basename(bpy.context.scene.movtoimg_src)
                    thepath = os.path.dirname(os.path.abspath(bpy.path.abspath(bpy.context.scene.movtoimg_src)))
                    if bpy.context.scene.movtoimg_cleanup:
                        tgtclean = filename[:-4].replace(' ','_')
                        tgtclean = tgtclean.lower()
                        thiscleanname = tgtclean
                    else:
                        thiscleanname = filename[:-4]
                    thispath = os.path.join(thepath, filename)
                    thisfullpath = os.path.join(thepath, thiscleanname)
                    newtgtpath=os.path.join(thisfullpath, thiscleanname)
                    newtgtbasename=os.path.join(newtgtpath, thiscleanname)
                    if not(os.path.exists(thisfullpath)):
                        print('output folder does not exist')
                        os.mkdir(thisfullpath)
                    if bpy.context.scene.movtoimg_totype == 'jpg':
                        tempcmd = (pathtoffmpeg+'-i '+thispath+' -qscale:v 2 '+newtgtpath+theext)
                    else:
                        tempcmd = (pathtoffmpeg+'-i '+thispath+' '+newtgtpath+theext)
                    print(tempcmd)
                    subprocess.call(tempcmd)
        elif bpy.context.scene.movtoimg_process == 'LOCAL':
            for img in bpy.data.images:
                if img.filepath[-4:] == '.mov':
                    filename = os.path.basename(img.filepath)
                    thepath = os.path.dirname(os.path.abspath(bpy.path.abspath(img.filepath)))
                    if bpy.context.scene.movtoimg_cleanup:
                        tgtclean = filename[:-4].replace(' ','_')
                        tgtclean = tgtclean.lower()
                        thiscleanname = tgtclean
                    else:
                        thiscleanname = filename[:-4]
                    thispath = os.path.join(thepath, filename)
                    thisfullpath = os.path.join(thepath, thiscleanname)
                    newtgtpath=os.path.join(thisfullpath, thiscleanname)
                    newtgtbasename=os.path.join(newtgtpath, thiscleanname)
                    if not(os.path.exists(thisfullpath)):
                        print('output folder does not exist')
                        os.mkdir(thisfullpath)
                    if bpy.context.scene.movtoimg_totype == 'jpg':
                        tempcmd = (pathtoffmpeg+'-i '+thispath+' -qscale:v 2 '+newtgtpath+theext)
                    else:
                        tempcmd = (pathtoffmpeg+'-i '+thispath+' '+newtgtpath+theext)
                    print(tempcmd)
                    subprocess.call(tempcmd)
                    if bpy.context.scene.movtoimg_repath:
                        thenewpath = (newtgtpath+thenewext)
                        img.filepath = thenewpath
                        img.source = 'SEQUENCE'
        elif bpy.context.scene.movtoimg_process == 'LOCALSEL':
            theimgs = []
            for ob in bpy.context.selected_objects:
                for mtl in ob.material_slots:
                    if mtl.material.use_nodes:
                        for node in mtl.material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                if (node.image is not None) and (len(node.image.filepath) >= 4) and (node.image.filepath[-4:] == '.mov'):
                                    if not(node.image in theimgs):
                                        theimgs.append(node.image)
            for img in theimgs:
                if img.filepath[-4:] == '.mov':
                    filename = os.path.basename(img.filepath)
                    thepath = os.path.dirname(os.path.abspath(bpy.path.abspath(img.filepath)))
                    if bpy.context.scene.movtoimg_cleanup:
                        tgtclean = filename[:-4].replace(' ','_')
                        tgtclean = tgtclean.lower()
                        thiscleanname = tgtclean
                    else:
                        thiscleanname = filename[:-4]
                    thispath = os.path.join(thepath, filename)
                    thisfullpath = os.path.join(thepath, thiscleanname)
                    newtgtpath=os.path.join(thisfullpath, thiscleanname)
                    newtgtbasename=os.path.join(newtgtpath, thiscleanname)
                    if not(os.path.exists(thisfullpath)):
                        print('output folder does not exist')
                        os.mkdir(thisfullpath)
                    if bpy.context.scene.movtoimg_totype == 'jpg':
                        tempcmd = (pathtoffmpeg+'-i '+thispath+' -qscale:v 2 '+newtgtpath+theext)
                    else:
                        tempcmd = (pathtoffmpeg+'-i '+thispath+' '+newtgtpath+theext)
                    print(tempcmd)
                    subprocess.call(tempcmd)
                    if bpy.context.scene.movtoimg_repath:
                        thenewpath = (newtgtpath+thenewext)
                        img.filepath = thenewpath
                        img.source = 'SEQUENCE'
                            
        print('COMPLETE CONVERT')
        return{'FINISHED'}

#define panel
class VIEW3D_OT_movtoimg(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = ("MOV to Images v "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "movtoimg_src", text="")
        layout.prop(scene, "movtoimg_process", text="")
        split = layout.split(percentage=0.5, align=True)
        col = split.column()
        col.prop(scene, "movtoimg_cleanup")
        col = split.column()
        col.prop(scene, "movtoimg_repath")
        layout.prop(scene, "movtoimg_totype", text="")
        layout.operator("movtoimg.convert", text=(BUTTON_OT_movtoimg_convert.bl_label))
        

#register

classes = [ BUTTON_OT_movtoimg_convert, VIEW3D_OT_movtoimg ]

def register():
    from bpy.utils import register_class
    for cls in classes:
        print(cls)
        register_class(cls)
    bpy.types.Scene.movtoimg_src = bpy.props.StringProperty(
        name="Source:",
        description="Source Directory",
        default="",
        maxlen=1024,
        update = make_path_absolute,
        subtype='FILE_PATH')
    
    bpy.types.Scene.movtoimg_cleanup = bpy.props.BoolProperty(
        name = "Clean Up Names",
        description = "Replace spaces with underscores and make the image names all lower case",
        default = True)
    
    bpy.types.Scene.movtoimg_repath = bpy.props.BoolProperty(
        name = "Repath to image sequence",
        description = "Repath image textures to use image sequences (only useful if ingoring path and converting from file or selected objects in the file)",
        default = True)
    
    bpy.types.Scene.movtoimg_process = bpy.props.EnumProperty(
        name = "Process",
        description = "Convert all .mov files in folder (and all subfolders) or only the file to parallel director(ies).",
        items=[('FILE','Only the QUICKTIME FILE selected above',''),
               ('LOCAL','All the .mov files in this BLENDER FILE (ignore path)',''),
               ('LOCALSEL','All the .mov files in materials on SELECTED OBJECTs in this Blender file (ignore path)','')],
        default=('FILE')
        )
    
    bpy.types.Scene.movtoimg_totype = bpy.props.EnumProperty(
        name = "To Type",
        description = "Output Filetype.",
        items=[('tif','Tiff (.tif)',''),
               ('jpg','Jpeg (.jpg)',''),
               ('dpx','DPX (.dpx)','')],
        default=('jpg')
        )

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.movtoimg_src
    del bpy.types.Scene.movtoimg_totype
    del bpy.types.Scene.movtoimg_process
    del bpy.types.Scene.movtoimg_cleanup
    
    
if __name__ == "__main__":
    register()
