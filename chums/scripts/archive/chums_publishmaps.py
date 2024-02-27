# made in response to --
# The eventual need to collect and repath image maps during the publishing process
# TARGETS v5.0
## completely remove Restore functionality; keep logging (for now)
# v5.0
#

bl_info = {
    "name": "Publish Maps",
    "author": "conrad dueck",
    "version": (0,5,1),
    "blender": (4, 1, 0),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Collect image maps to publish directory and back up any maps that already exist there.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

import bpy
import os
import shutil
import subprocess
from pathlib import Path

####    GLOBAL VARIABLES    ####
vsn='5.1b'
imgignorelist = ['Render Result', 'Viewer Node', 'vignette.png']
clean_export_fileformat = 'OPEN_EXR'
clean_export_fileext = 'exr'
clean_export_filedepth = '16'
clean_export_imagick = 'zip'
clean_export_filecodec = 'ZIP'
imagick = Path("C:/Program Files/ImageMagick-6.9.13-Q16-HDRI/convert.exe")
number_digits = "0123456789"

####    FUNCTIONS    ####
def make_path_absolute(self, context):
    if self.publishmaps_to:
        if self.publishmaps_to.startswith('//'):
            self.publishmaps_to = (os.path.abspath(bpy.path.abspath(self.publishmaps_to)))
    if self.publishmaps_restore:
        if self.publishmaps_restore.startswith('//'):
            self.publishmaps_restore = (os.path.abspath(bpy.path.abspath(self.publishmaps_restore)))
    return None

def removedigits(thestring):
    for i in range(10):
        if str(i) in thestring:
            thestring = thestring.replace(str(i), '')
    return thestring

# sha256 hash compare 2 files
def compare2files(f1, f2):
    import hashlib
    replaceold = False
    absf1 = os.path.abspath(bpy.path.abspath(f1))
    absf2 = os.path.abspath(bpy.path.abspath(f2))
    hashlist = [(hashlib.sha256(open(fname, 'rb').read()).hexdigest()) for fname in (absf1, absf2)]
    if (hashlist[0] == hashlist[1]):
        replaceold = False
    else:
        replaceold = True
    print('(compare2files) sha256 hash comparison = ', replaceold)
    return replaceold

def get_node_target(the_node):
    print("ENTER get_node_targetFUNCTION with: ", the_node)
    #if the_node is not 'none':
    the_next_type = 'none'
    the_next_node = 'none'
    the_id = ''
    if the_node and the_node is not 'none':
        for the_out in the_node.outputs:
            if the_out.is_linked:
                for link in the_out.links:
                    the_next_type = link.to_node.type
                    the_next_node = link.to_node
                    the_id = link.to_socket.identifier
        return the_next_type, the_next_node, the_id
    else:
        print("\"the_node\" is returning a string none")


def trace_to_shader(image,object):
    my_maptype = 'nonetype'
    for mt in object.material_slots:
        mtl = mt.material
        for node in mtl.node_tree.nodes:
            if node and node.type == 'TEX_IMAGE' and node.image == image:
                for the_out in node.outputs:
                    if the_out.is_linked:
                        for link in the_out.links:
                            tgt_link = get_node_target(node)
                            try:
                                while tgt_link[0] != 'BSDF_PRINCIPLED':
                                    tgt_link = get_node_target(tgt_link[1])
                                    my_maptype = tgt_link
                            except:
                                print("FAILED ON: ", node)
                            break
    print(image.name + "\n" + 'trace_to_shader returns (my_maptype): ', my_maptype)
    return my_maptype

def convert_to_exr(image):
    import os
    convert_cleanpath = image.replace('\\','/')
    cleanpath_dir = os.path.dirname(convert_cleanpath)
    cleanpath_file = (os.path.basename(convert_cleanpath))
    targetpath_file = ("autoconvert_" + os.path.basename(convert_cleanpath))
    convert_cleanpath = os.path.join(cleanpath_dir, cleanpath_file)
    convert_tgt_path = (targetpath_file[:-4] + ".exr")
    #print('convert_tgt_path = ',convert_tgt_path)
    convert_img_cmd = ("\"" + str(imagick) + "\" \"" + str(Path(convert_cleanpath)) + "\" -compress zip -depth 16 \"" + str(Path(convert_tgt_path)) + "\"")
    #print("convert_img_cmd = ", convert_img_cmd)
    running = subprocess.Popen(convert_img_cmd)
    running.wait()
    print(running.returncode)
    if os.path.exists(convert_tgt_path):
        print("convert_to_exr returning: ", convert_tgt_path)
        return convert_tgt_path
    else:
        print("convert_to_exr returning: ", image)
        return (image)

####    CLASSES    ####
#   OPERATOR publishmapspublish PUBLISH MAPS
class BUTTON_OT_publishmapspublish(bpy.types.Operator):
    '''Publish Maps'''
    bl_idname = "publishmaps.publish"
    bl_label = "Publish Maps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('\n\nSTART PUBLISH')
        #   set initial variables and empty lists
        theobjects = []     # dict of objects and materials
        theimgs = []     # list of images to process
        theimgtypes = [] # list of image types mapped to theimgs
        theoldpaths = [] # list of image paths used by theimgs
        tgtpaths = [] # list of the new paths to which the images will be published
        theimgnodes = {} # img_name: node_material, node_name, to_socket
        totalpubs = 0
        anypacks = 0
        totalconfirmedpaths = 0
        theFile = os.path.basename(bpy.data.filepath)[:-6]
        thefilepath = os.path.dirname(bpy.data.filepath)
        if len(theFile) >= 4 and len(theFile.split("_")) > 2:
            theasset = theFile[:-5]
        else:
            theasset = "unknown"
        unpacktarget = os.path.join(thefilepath, 'unpacked')
        imageformats = {'BMP':'.bmp','PNG':'.png','JPEG':'.jpg','JPEG2000':'.jpg',
                        'TARGA':'.tga','TARGA_RAW':'.tga','CINEON':'.cin','DPX':'.dpx',
                        'OpenEXR':'.exr','OPEN_EXR_MULTILAYER':'.exr','OPEN_EXR':'.exr',
                        'HDR':'.hdr','TIFF':'.tif','AVI_JPEG':'.avi','AVI_RAW':'.avi'}
        
        #   switch to absolute paths
        print('Set all files to absolute.')
        bpy.ops.file.make_paths_absolute()
        
        #   get the destination/publish path from the UI
        thepath = os.path.abspath(bpy.path.abspath(bpy.context.scene.publishmaps_to))
        if (len(bpy.context.scene.publishmaps_to) >= 1) and (os.path.exists(bpy.context.scene.publishmaps_to)):
            thepath = os.path.abspath(bpy.path.abspath(bpy.context.scene.publishmaps_to))
            print('\nPublish folder found: ', thepath)
        else:
            print('\nPublish folder NOT found: ', thepath)
            thepath = ''
        
        #   if the path is defined
        if len(thepath) >= 1:
            #   gather up a list of the images to process
            if bpy.context.scene.publishmaps_selected:
                oblist = bpy.context.selected_objects
            else:
                oblist = bpy.data.objects
            
            for ob in oblist:
                for mtl in ob.material_slots:
                    if mtl.material.use_nodes:
                        for node in mtl.material.node_tree.nodes:
                            print("NODE: ", node.name, " is TYPE: ",node.type)
                            if node.type == 'TEX_IMAGE':
                                if node.image.packed_file:
                                    print("FOUND PACKED: ", node.name, mtl.name)
                                    anypacks += 1
                                this_image = os.path.basename(node.image.filepath)
                                img = node.image
                                thismaptype = trace_to_shader(img,ob)
                                try:
                                    this_to_socket = thismaptype[2].replace(' ','_')
                                except:
                                    print("FAIL ON: ", thismaptype) 
                                if this_image in theimgnodes.keys():
                                    theimgnodes[this_image]['materials'].append(mtl.name)
                                    theimgnodes[this_image]['nodes'].append(node.name)
                                    theimgnodes[this_image]['objects'].append(ob.name)
                                    theimgnodes[this_image]['to_socket'].append(this_to_socket)
                                else:
                                    theimgnodes[this_image] = {'materials':[mtl.name],'nodes':[node.name], 'objects':[ob.name], 'to_socket':[this_to_socket]}
                                if not(node.image in theimgs) and not(node.image.name in imgignorelist):
                                    if node.image.packed_file or os.path.exists(node.image.filepath):
                                        theimgs.append(node.image)
                                        theoldpaths.append(node.image.filepath)
                                        theimgtypes.append(node.image.source)
                                        theobjects.append(ob.name)
                                    else:
                                        print('MISSING: ', node.image.filepath)
                            elif node.type == 'GROUP':
                                
            print('\nList to process:\n ', theimgs)
            print('anypacks = ', anypacks)
            
            #   handle missing unpack folder if there are any packed files
            if anypacks >= 1 and not(os.path.exists(unpacktarget)):
                os.mkdir(unpacktarget, 0o777)
                print('\nUnpack folder NOT found. Created: ' + unpacktarget)
            
            #   cycle thru images and collect original paths (theoldpaths) and generate the new image paths (tgtpaths)
            for imgnum, img in enumerate(theimgs):
                #img = theimgs[imgnum]
                thisobject = theobjects[imgnum]
                srcfile = theoldpaths[imgnum]
                srcpath = os.path.dirname(srcfile)
                srcfilename = os.path.basename(srcfile)
                srcfilebase = srcfilename.split(".")[0]
                clean_export_fileext = 'exr'
                
                print('imgnum = ', imgnum)
                print('img = ', img)
                print('commence processing ', img.name)
                
                tgtformat = img.file_format
                srcformat = img.file_format
                srctype = theimgtypes[imgnum]
                theoldname = os.path.basename(theoldpaths[imgnum])
                
                #   UNPACK if the image is PACKED into the file
                if img.packed_file:
                    curformat = bpy.context.scene.render.image_settings.file_format
                    bpy.context.scene.render.image_settings.file_format = srcformat
                    theext = imageformats[srcformat]
                    if len(srcfilename) < 1:
                        srcfilename = (img.name + theext)
                    newpath = os.path.join(unpacktarget, srcfilename)
                    thisversion = 0
                    print('FIRST existence check - newpath = ', newpath)
                    if os.path.exists(newpath):
                        print('EXISTS')
                    while os.path.exists(newpath):
                        print('ITERATIVE existence check - newpath = ', newpath)
                        tempname = (srcfilename[:-4] + '_' + str(thisversion).zfill(3) + theext)
                        newpath = os.path.join(unpacktarget, tempname)
                        thisversion += 1
                    theoldname = os.path.basename(newpath)
                    print('theoldname = ', theoldname)
                    print('postexistence check - newpath = ', newpath)
                    img.save_render(newpath, scene=bpy.context.scene)
                    theoldpaths[imgnum] = newpath
                    img.packed_files[0].filepath = newpath
                    img.filepath = newpath
                    img.unpack(method='USE_ORIGINAL')
                    srcfile = img.filepath
                    bpy.context.scene.render.image_settings.file_format = curformat
                
                #   handle clean up - file name
                #   <asset name>_<object name>_<map type>_<version#>.<ext>
                if bpy.context.scene.publishmaps_cleanup == True:
                    thismaptype = trace_to_shader(img,bpy.data.objects[thisobject])
                    customname = ("autoconvert_" + srcfilebase + "." + clean_export_fileext)
                    tgtfilename = customname.replace(' ', '_')
                    tgtfilename = tgtfilename.replace(":","_")
                    tgtfilename_ext = tgtfilename.split(".")[-1]
                    tgtfilename = tgtfilename.replace(tgtfilename_ext,clean_export_fileext)
                else:
                    tgtfilename = theoldname
                while "autoconvert_autoconvert_" in tgtfilename:
                    tgtfilename = tgtfilename.replace("autoconvert_autoconvert_", "autoconvert_")
                dupfix = 0
                tgtpath = os.path.join(thepath, tgtfilename)
                #   publish already exists
                while os.path.exists(tgtpath):
                    tgtbase = os.path.basename(tgtpath)[:-4]
                    while tgtbase[-1] in number_digits:
                        tgtbase = tgtbase[:-1]
                    tgtpath = os.path.join(os.path.dirname(tgtpath),(tgtbase + str(dupfix).zfill(3) + '.' + clean_export_fileext))
                    dupfix += 1
                tgtpaths.append(tgtpath)
                print('srcfile = ', srcfile,'\nsrcpath = ', srcpath,'\nsrcfilename = ', srcfilename,'\nsrcformat = ', srcformat,'\nsrctype = ', srctype, '\n')
                print('tgtfile = ', tgtfilename, '\ntgtpath = ', tgtpath,'\ntgtfilename = ', tgtfilename,'\ntgtformat = ', tgtformat,'\ntgttype = ', srctype, '\n')
                
                
            #   process the image list
            for imgnum, img in enumerate(theimgs):
                srcfile = theoldpaths[imgnum]
                print('srcfile:', srcfile)
                srcformat = img.file_format
                srctype = theimgtypes[imgnum]
                theoldname = os.path.basename(theoldpaths[imgnum])
                tgtfile = tgtpaths[imgnum]
                tgtfilename = os.path.basename(tgtpaths[imgnum])
                print('\nProcessing ', srcformat, ' image: ', theoldname)
                print('    src: ', srcfile)
                print('    tgt: ', tgtfile)
                
                #   SEQUENCE
                if srctype == 'SEQUENCE':
                    #   publish sequence
                    theframecount = 0
                    srcbasename = removedigits(theoldname)
                    print('\n    srcbasename = ', srcbasename)
                    for fl in os.listdir(srcpath):
                        flfullpath = os.path.join(srcpath, fl)
                        print('\n    flfullpath = ', flfullpath)
                        if (os.path.isfile(flfullpath)) and not('humbs.db' in fl):
                            if removedigits(fl) == srcbasename:
                                print('    will need to publish', flfullpath)
                                if bpy.context.scene.publishmaps_cleanup == True:
                                    cleanfullpath = convert_to_exr(Path(srcfile))
                                    shutil.copy2(cleanfullpath, thepath)
                                else:
                                    shutil.copy2(flfullpath, thepath)
                                theframecount += 1
                    img.filepath = tgtfile
                    totalpubs += 1
                #   SINGLE
                else:
                    #   publish single
                    if bpy.context.scene.publishmaps_cleanup == True:
                        newfile = convert_to_exr(srcfile)
                    else:
                        newfile = srcfile
                    shutil.copy2(newfile, tgtfile)
                    img.filepath = tgtfile
                    totalpubs += 1
                
            #   ensure file paths are absolute
            bpy.ops.file.make_paths_absolute()
                
            #   confirm all image file paths in file
            for imgnum, img in enumerate(theimgs):
                img = theimgs[imgnum]
                if not(img.name in imgignorelist):
                    thisrealpath = os.path.realpath(bpy.path.abspath(img.filepath))
                    if not(os.path.exists(os.path.realpath(bpy.path.abspath(img.filepath)))):
                        print('\n    FAILED to find: ' + os.path.realpath(bpy.path.abspath(img.filepath)))
                    else:
                        print('\n    FOUND: ' + thisrealpath)
                        totalconfirmedpaths += 1
                
            print('Done.')
        print('COMPLETE PUBLISH')
        return{'FINISHED'}
   
#   PANEL publishmaps
class VIEW3D_PT_publishmaps(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Publish Maps v "+vsn)
    bl_context = "objectmode"
    bl_category = "Chums"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "publishmaps_selected")
        layout.prop(scene, "publishmaps_to", text="")
        layout.prop(scene, "publishmaps_cleanup")
        layout.operator("publishmaps.publish", text=(BUTTON_OT_publishmapspublish.bl_label))
        

####    REGISTRATION    ####

classes = ( BUTTON_OT_publishmapspublish, VIEW3D_PT_publishmaps )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    bpy.types.Scene.publishmaps_selected = bpy.props.BoolProperty(
        name = "Only Selected",
        description = "Uses object selection to determine maps to publish.",
        default = True)
    
    bpy.types.Scene.relative_paths = bpy.props.BoolProperty(
        name = "Relative Paths",
        description = "Use file relative paths for images.",
        default = False)
    
    bpy.types.Scene.publishmaps_to = bpy.props.StringProperty(
        name="Publish To:",
        description="Output Directory",
        default="",
        maxlen=1024,
        update = make_path_absolute,
        subtype='DIR_PATH')
    
    bpy.types.Scene.publishmaps_cleanup = bpy.props.BoolProperty(
        name = "Clean Up (exr)",
        description = "Replace spaces with underscores and convert to EXR",
        default = True)
    
    bpy.types.Scene.publishmaps_restore = bpy.props.StringProperty(
        name="Restore From:",
        description="Log File",
        default="",
        maxlen=1024,
        update = make_path_absolute,
        subtype='FILE_PATH')

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.publishmaps_selected
    del bpy.types.Scene.publishmaps_to
    del bpy.types.Scene.publishmaps_cleanup
    del bpy.types.Scene.publishmaps_restore
    
    
if __name__ == "__main__":
    register()
