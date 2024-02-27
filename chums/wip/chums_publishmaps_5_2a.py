# made in response to --
# The eventual need to collect and repath image maps during the publishing process
# TARGETS v5.0
## completely remove Restore functionality; keep logging (for now)
# v5.2
# significant cleanup to remove legacy features
# reintroduced hash checks and cleaned up duplicate incrementation code

bl_info = {
    "name": "Publish Maps",
    "author": "conrad dueck",
    "version": (0,5,2),
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
vsn='5.2'
imgignorelist = ['Render Result', 'Viewer Node', 'vignette.png']
clean_export_fileformat = 'OPEN_EXR'
clean_export_fileext = 'exr'
clean_export_filedepth = '16'
clean_export_imagick = 'zip'
clean_export_filecodec = 'ZIP'
imagick = Path("C:/Program Files/ImageMagick-6.9.13-Q16-HDRI/convert.exe")
number_digits = "0123456789_"

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
    print("    compare2files: ", f1, f2)
    replace_it = False
    absf1 = os.path.abspath(bpy.path.abspath(f1))
    absf2 = os.path.abspath(bpy.path.abspath(f2))
    hashlist = [(hashlib.sha256(open(fname, 'rb').read()).hexdigest()) for fname in (absf1, absf2)]
    if (hashlist[0] == hashlist[1]):
        replace_it = True
    else:
        replace_it = False
    print('    (compare2files) sha256 hash comparison match = ', replace_it)
    return replace_it

def get_node_target(the_node):
    #print("ENTER get_node_target FUNCTION with: ", the_node)
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
                break
    #print("EXIT get_node_target FUNCTION returning (the_next_type, the_next_node, the_id): ", the_next_type, the_next_node, the_id)
    return the_next_type, the_next_node, the_id

def trace_to_shader(image, object):
    #print("ENTER trace_to_shader FUNCTION with: ", image, object)
    my_shader_input = ''
    for mt in object.material_slots:
        mtl = mt.material
        for node in mtl.node_tree.nodes:
            if node and node.type == 'TEX_IMAGE' and node.image == image:
                for the_out in node.outputs:
                    if the_out.is_linked:
                        tgt_link = get_node_target(node)
                        my_shader_input = tgt_link[2]
                        break
    #print("EXIT trace_to_shader returns (my_shader_input): ", my_shader_input)
    return my_shader_input

def convert_to_exr(image):
    import os
    print("convert_to_exr(image): ", image)
    convert_cleanpath = image
    cleanpath_dir = os.path.dirname(convert_cleanpath)
    cleanpath_file = (os.path.basename(convert_cleanpath))
    targetpath_file = ("autoconvert_" + os.path.basename(convert_cleanpath))
    convert_tgt_path = (targetpath_file[:-4] + ".exr")
    #print('convert_tgt_path = ',convert_tgt_path)
    convert_img_cmd = ("\"" + str(imagick) + "\" \"" + str(Path(convert_cleanpath)) + "\" -compress zip -depth 16 \"" + str(Path(convert_tgt_path)) + "\"")
    #print("convert_img_cmd = ", convert_img_cmd)
    running = subprocess.Popen(convert_img_cmd)
    running.wait()
    print(running.returncode)
    if os.path.exists(convert_tgt_path):
        print("convert_to_exr returning (successs): ", convert_tgt_path)
        return convert_tgt_path
    else:
        print("convert_to_exr returning (original): ", image)
        return (image)

def unpack_image(packed_img):
    thefilepath = os.path.dirname(bpy.data.filepath)
    unpacktarget = os.path.join(thefilepath, 'unpacked')
    imageformats = {'BMP':'.bmp','PNG':'.png','JPEG':'.jpg','JPEG2000':'.jpg',
                    'TARGA':'.tga','TARGA_RAW':'.tga','CINEON':'.cin','DPX':'.dpx',
                    'OpenEXR':'.exr','OPEN_EXR_MULTILAYER':'.exr','OPEN_EXR':'.exr',
                    'HDR':'.hdr','TIFF':'.tif','AVI_JPEG':'.avi','AVI_RAW':'.avi'}
    #   handle missing unpack folder if there are any packed files
    if not(os.path.exists(unpacktarget)):
        os.mkdir(unpacktarget, 0o777)
        #print('\n      Unpack folder NOT found. Created: ' + unpacktarget)
    srcformat = packed_img.file_format
    curformat = bpy.context.scene.render.image_settings.file_format
    bpy.context.scene.render.image_settings.file_format = srcformat
    theext = imageformats[srcformat]
    srcfilename = (packed_img.name + theext)
    newpath = os.path.join(unpacktarget, srcfilename)
    #print('      FIRST existence check - newpath = ', newpath)
    thisversion = 0
    while os.path.exists(newpath):
        #print('      ITERATIVE existence check - newpath = ', newpath)
        tempname = (srcfilename[:-4] + '_' + str(thisversion).zfill(3) + theext)
        newpath = os.path.join(unpacktarget, tempname)
        thisversion += 1
    print('      FINAL UNPACK PATH (newpath) = ', newpath)
    packed_img.save_render(newpath, scene=bpy.context.scene)
    packed_img.filepath = newpath
    packed_img.unpack(method='USE_ORIGINAL')
    bpy.context.scene.render.image_settings.file_format = curformat

    return 0

def images_from_node_tree(my_mtl, my_obj, my_imglist, my_sockets):
    #print("\nENTER images_from_node_tree FUNCTION with: ", my_mtl.name, my_obj.name)
    local_sockets = my_sockets
    for node in my_mtl.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            img = node.image
            if img.packed_file:
                #print("   FOUND PACKED: ", node.name, my_mtl.name)
                unpack_image(img)
            thismaps_shader = trace_to_shader(img, my_obj)
            shader_socket = thismaps_shader.replace(' ','_')
            if not(img in my_imglist):
                my_imglist.append(img)
                local_sockets.append(shader_socket)
            my_sockets = local_sockets
        elif node.type == 'GROUP':
            print("GROUP NODE: ", node.name)
            images_from_node_tree(my_mtl,my_obj,my_imglist,local_sockets)
    #print("EXIT images_from_node_tree FUNCTION with (my_imglist, my_sockets)")
    return (my_imglist, my_sockets)
    
####    CLASSES    ####
#   OPERATOR publishmapspublish PUBLISH MAPS
class BUTTON_OT_publishmapspublish(bpy.types.Operator):
    '''Publish Maps'''
    bl_idname = "publishmaps.publish"
    bl_label = "Publish Maps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('\n\nSTART PUBLISH')
        #   initialize operational variables and empty lists
        oblist = []         # list of objects to process
        mtl_objs = {}       # dict of materials - [material name]:[object_user, images_list, sockets_list]
        tgtpaths = []       # list of the new paths to which the images will be published
        imgdict = {}        # master dict where { image_name : object_user, material_user, socket_user}
        totalconfirmedpaths = 0
        theimgs = []

        #   switch to absolute paths
        print('Set all files to absolute...')
        bpy.ops.file.make_paths_absolute()
        
        #   initialize context dependent variables (theFile, theasset)
        theFile = os.path.basename(bpy.data.filepath)[:-6]
        if len(theFile) >= 4 and len(theFile.split("_")) > 2:
            theasset = theFile[:-5]
        else:
            theasset = "unknown"
        print('theasset = ', theasset)
        
        #   get the destination/publish path from the UI (thepath)
        thepath = os.path.abspath(bpy.path.abspath(bpy.context.scene.publishmaps_to))
        if (len(bpy.context.scene.publishmaps_to) >= 1) and (os.path.exists(bpy.context.scene.publishmaps_to)):
            thepath = os.path.abspath(bpy.path.abspath(bpy.context.scene.publishmaps_to))
            print('\nPublish folder found: ', thepath)
        else:
            print('\nPublish folder NOT found: ', thepath)
            thepath = ''
        
        if len(thepath) >= 1:
            #   get the objects to process (oblist)
            if bpy.context.scene.publishmaps_selected:
                oblist = bpy.context.selected_objects
            else:
                oblist = bpy.data.objects
            
            #   gather a dict of the unique materials to process and their object assignments (mtl_objs)
            for ob in oblist:
                for mtl in ob.material_slots:
                    if mtl.material.use_nodes:
                        if not(mtl.material.name in mtl_objs.keys()):
                            #   gather the images used in this material and the sockets they drive
                            this_mtl_imgs = images_from_node_tree(mtl.material, ob, [], [])
                            mtl_objs[mtl.material.name] = [ob.name, this_mtl_imgs[0], this_mtl_imgs[1]]
                    else:
                        print(mtl.material.name, " is INVALID - must use nodes")
            
            #   gather the unique images from the mtl_objs dict (imgdict)
            for mtl in mtl_objs.keys():
                for imgnum, img in enumerate(mtl_objs[mtl][1]):
                    if not(img in imgdict.keys()):
                        imgdict[img] = [mtl_objs[mtl][0], mtl, mtl_objs[mtl][2][imgnum]]
            
            #   PUBLISH images in image dictionary
            print("The collected imgdict has ", len(imgdict.keys()), " images to process")
            
            for imgnum, img in enumerate(imgdict.keys()):
                print("\nCommence processing:")
                print("    img.name: ", img.name)
                proc_img = bpy.data.images[img.name]
                srcfile = proc_img.filepath
                srcfilepath = os.path.dirname(srcfile)
                srcfilename = os.path.basename(srcfile)
                srcfilebase = srcfilename.split(".")[0]
                srcformat = srcfilename.split(".")[-1]
                img_socket = imgdict[img][2]
                
                if bpy.context.scene.publishmaps_cleanup == True:
                    #thismaptype = trace_to_shader(img,bpy.data.objects[thisobject])
                    customname = (srcfilebase + "." + clean_export_fileext)
                    tgtfilename = customname.replace(' ', '_')
                    tgtfilename = tgtfilename.replace(":","_")
                    tgtfilename_ext = tgtfilename.split(".")[-1]
                    tgtfilename = tgtfilename.replace(tgtfilename_ext,clean_export_fileext)
                else:
                    tgtfilename = srcfilename
                while "autoconvert_autoconvert_" in tgtfilename:
                    tgtfilename = tgtfilename.replace("autoconvert_autoconvert_", "autoconvert_")
                dupfix = 0
                tgtpath = os.path.join(thepath, tgtfilename)
                tgtbase = os.path.basename(tgtpath)[:-4]
                need_new = True
                #   publish already exists
                while os.path.exists(tgtpath):
                    # hash check tgtpath (check file)
                    if compare2files(srcfile, tgtpath):
                        print("    MATCHED with: ", tgtpath)
                        need_new = False
                        break
                    else:
                        if tgtbase[-4] == "_":
                            tgtbase = tgtbase[:-4]
                        tgtpath = os.path.join(os.path.dirname(tgtpath),(tgtbase + "_" + str(dupfix).zfill(3) + '.' + clean_export_fileext))
                        need_new = True
                        dupfix += 1
                if need_new:
                    tgtpaths.append(tgtpath)
                #print('\nsrcfile = ', srcfile,'\nsrcpath = ', srcfilepath,'\nsrcfilename = ', srcfilename,'\nsrcformat = ', srcformat)
                #print('\ntgtfile = ', tgtfilename, '\ntgtpath = ', tgtpath,'\ntgtfilename = ', tgtfilename,'\ntgtformat = ', clean_export_fileext)
                
                srctype = img.source
                tgtfile = tgtpath
                tgtfilename = os.path.basename(tgtpath)
                print('    src: ', srcfile)
                print('    tgt: ', tgtfile)
                print('    new: ', need_new)
                
                #   SEQUENCE
                if (need_new == True) and srctype == 'SEQUENCE':
                    #   publish sequence
                    theframecount = 0
                    srcbasename = removedigits(srcfile)
                    #print('\n    srcbasename = ', srcbasename)
                    for fl in os.listdir(srcfilepath):
                        flfullpath = os.path.join(srcfilepath, fl)
                        #print('\n    flfullpath = ', flfullpath)
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
                #   SINGLE
                else:
                    #   publish single
                    if (need_new == True):
                        if bpy.context.scene.publishmaps_cleanup == True:
                            newfile = convert_to_exr(Path(srcfile))
                        else:
                            newfile = srcfile
                        shutil.copy2(newfile, tgtfile)
                        img.filepath = tgtfile
                theimgs.append(img)
                    
                
            #   ensure file paths are absolute
            bpy.ops.file.make_paths_absolute()
                
            #   confirm all image file paths in file
            for imgnum, img in enumerate(theimgs):
                img = theimgs[imgnum]
                if not(img.name in imgignorelist):
                    thisrealpath = os.path.realpath(bpy.path.abspath(img.filepath))
                    if not(os.path.exists(thisrealpath)):
                        print('\n    FAILED to find: ' + thisrealpath)
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
