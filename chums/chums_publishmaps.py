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
    "version": (0,5,3),
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
vsn='5.3'
imgignorelist = ['Render Result', 'Viewer Node', 'vignette.png']
grpignorelist = ['ZenUV_Override']
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
    print("    compare2files: ", absf1, absf2)
    hashlist = [(hashlib.sha256(open(fname, 'rb').read()).hexdigest()) for fname in (absf1, absf2)]
    #print("    compare2files: hashlist[0]: ", hashlist[0])
    #print("    compare2files: hashlist[1]: ", hashlist[1])
    if (hashlist[0] == hashlist[1]):
        replace_it = True
    else:
        replace_it = False
    print('    compare2files: sha256 hash comparison match = ', replace_it)
    return replace_it

def get_node_target(the_node):
    #print("ENTER get_node_target FUNCTION with: ", the_node)
    the_next_type = 'none'
    the_next_node = 'none'
    the_id = ''
    if the_node and (the_node is not 'none'):
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
    targetpath_file = ("autoconvert_" + os.path.basename(convert_cleanpath))
    convert_tgt_path = (targetpath_file[:-4] + ".exr")
    #print('convert_tgt_path = ',convert_tgt_path)
    convert_img_cmd = ("\"" + str(imagick) + "\" \"" + str(Path(convert_cleanpath)) + "\" -compress zip -depth 16 \"" + str(Path(convert_tgt_path)) + "\"")
    #print("convert_img_cmd = ", convert_img_cmd)
    running = subprocess.Popen(convert_img_cmd)
    running.wait()
    print(running.returncode)
    if os.path.exists(convert_tgt_path):
        print("convert_to_exr returning (success): ", convert_tgt_path)
        return convert_tgt_path
    else:
        print("convert_to_exr returning (failed): ", image)
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
    srcformat = packed_img.file_format
    print('srcformat: ', srcformat)
    curformat = bpy.context.scene.render.image_settings.file_format
    print('curformat: ', curformat)
    bpy.context.scene.render.image_settings.file_format = srcformat
    theext = imageformats[srcformat]
    print('theext: ', theext)
    srcfilebase = (packed_img.name).split(".")[0]
    print('srcfilebase: ', srcfilebase)
    srcfilename = (srcfilebase + theext)
    print('srcfilename: ', srcfilename)
    newpath = os.path.join(unpacktarget, srcfilename)
    print('newpath: ', newpath)
    thisversion = 0
    while os.path.exists(newpath):
        #print('      ITERATIVE existence check - newpath = ', newpath)
        tempname = (srcfilename[:-4] + '_' + str(thisversion).zfill(3) + theext)
        print('   tempname: ', tempname)
        newpath = os.path.join(unpacktarget, tempname)
        thisversion += 1
    print('UNPACK PATH (newpath) = ', newpath)
    packed_img.save_render(newpath, scene=bpy.context.scene)
    packed_img.filepath = newpath
    packed_img.unpack(method='USE_ORIGINAL')
    bpy.context.scene.render.image_settings.file_format = curformat

    return 0

def get_imgs_from_mtl(my_mtl, my_obj, my_imglist, my_sockets):
    #print("\nENTER get_imgs_from_mtl FUNCTION with: ", my_mtl.name, my_obj.name)
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
        elif node.type == 'GROUP' and not (node.name in grpignorelist):
            print("GROUP NODE: ", node.name)
            get_imgs_from_mtl(my_mtl,my_obj,my_imglist,local_sockets)
    #print("EXIT get_imgs_from_mtl FUNCTION with (my_imglist, my_sockets)")
    return (my_imglist, my_sockets)

def cleanup_string(my_string):
    my_string = my_string.replace(" ", "")
    my_string = my_string.replace(".", "")
    my_string = my_string.replace("_", "")
    
    return my_string

#   my_imgs : PUBLISH images in image dictionary, returning the list of published images
def publish_images_from_dict(my_dict,target_path):
    my_imgs = []
    thefilebase = os.path.basename(bpy.data.filepath)[:-6]
    #   theasset
    if len(thefilebase) >= 4 and len(thefilebase.split("_")) > 2:
        theasset = thefilebase[:-5]
    else:
        theasset = "unknown"
    print('theasset = ', theasset)
    #   PUBLISH images in image dictionary
    print("\n   The collected my_dict has the following ", len(my_dict.keys()), " image(s) to process")
    for bb in my_dict.keys():
        print("      ", bb.name) 
    for imgnum, img in enumerate(my_dict.keys()):
        print("   Commence processing: ", img.name)
        proc_img = bpy.data.images[img.name]
        srcfile = proc_img.filepath
        srcfilepath = os.path.dirname(srcfile)
        srcfilename = os.path.basename(srcfile)
        srcfilebase = srcfilename.split(".")[0]
        srcfiletype = srcfilename.split(".")[1]
        if (len(srcfilebase.split("_")[-1]) == 4) and srcfilebase.split("_")[-1][0] == "v":
            srcfileversion = srcfilebase.split("_")[-1]
        else:
            srcfileversion = "v000"
        srcformat = srcfilename.split(".")[-1]
        img_material = my_dict[img][1]
        img_socket = my_dict[img][2]
        if bpy.context.scene.publishmaps_convert == True:
            my_ext = clean_export_fileext
        else:
            my_ext = srcfiletype
        if bpy.context.scene.publishmaps_rename == True:
            # <asset name>_<material>_<map type>_<version#>.<ext>
            mtl_name = img_material.split(":")[-1].replace("_", "").lower()
            clean_mtl_name = cleanup_string(mtl_name)
            sock_name = (img_socket.replace("_", "")).lower()
            clean_sock_name = cleanup_string(sock_name)
            tgtfilename = (theasset+"_"+clean_mtl_name+"_"+clean_sock_name+"_"+srcfileversion)
        else:
            tgtfilename = srcfilebase
        #cleanname = cleanup_string(tgtfilename)
        #tgtfilename = (cleanname+"."+my_ext)
        tgtfilename = (tgtfilename+"."+my_ext)
        while "autoconvert_autoconvert_" in tgtfilename:
            tgtfilename = tgtfilename.replace("autoconvert_autoconvert_", "autoconvert_")
        print("   publishmaps_rename using: ", tgtfilename)
        #   if publish already exists
        dupfix = 0
        tgtpath = os.path.join(target_path, tgtfilename)
        tgtbase = os.path.basename(tgtpath)[:-4]
        need_new = True
        while os.path.exists(tgtpath):
            #   hash check tgtpath (check file)
            if compare2files(srcfile, tgtpath):
                print("      MATCHED with: ", tgtpath)
                need_new = False
                img.filepath = tgtpath
                break
            else:
                if tgtbase[-4] == "_":
                    tgtbase = tgtbase[:-4]
                tgtpath = os.path.join(os.path.dirname(tgtpath), (tgtbase + "_" + str(dupfix).zfill(3) + '.' + clean_export_fileext))
                need_new = True
                dupfix += 1
        srctype = img.source
        tgtfile = tgtpath
        print('      src: ', srcfile)
        print('      tgt: ', tgtfile)
        print('      new: ', need_new)
        if (need_new == True):
            if srctype == 'SEQUENCE':
                #   publish SEQUENCE
                theframecount = 0
                srcbasename = removedigits(srcfile)
                #print('\n    srcbasename = ', srcbasename)
                for fl in os.listdir(srcfilepath):
                    flfullpath = os.path.join(srcfilepath, fl)
                    #print('\n    flfullpath = ', flfullpath)
                    if (os.path.isfile(flfullpath)) and not('humbs.db' in fl):
                        if removedigits(fl) == srcbasename:
                            print('    will need to publish', flfullpath)
                            if bpy.context.scene.publishmaps_convert == True:
                                cleanfullpath = convert_to_exr(Path(srcfile))
                                shutil.copy2(cleanfullpath, target_path)
                            else:
                                shutil.copy2(flfullpath, target_path)
                            theframecount += 1
                img.filepath = tgtfile
            else:
                #   publish SINGLE
                if (need_new == True):
                    if bpy.context.scene.publishmaps_convert == True:
                        newfile = convert_to_exr(Path(srcfile))
                    else:
                        newfile = srcfile
                    shutil.copy2(newfile, tgtfile)
                    img.filepath = tgtfile
            my_imgs.append(img)
    return my_imgs

def get_mtls_from_objects(objs):
    obj_mtls = {}
    oblist = objs
    for ob in oblist:
        for mtl in ob.material_slots:
            if mtl.material.use_nodes:
                if not(mtl.material.name in obj_mtls.keys()):
                    #   gather the images used in this material and the sockets they drive
                    this_mtl_imgs = get_imgs_from_mtl(mtl.material, ob, [], [])
                    obj_mtls[mtl.material.name] = [ob.name, this_mtl_imgs[0], this_mtl_imgs[1]]
                    print(("mtl_objs["+mtl.material.name+"]: "), obj_mtls[mtl.material.name])
            else:
                print(mtl.material.name, " is INVALID - must use nodes")
    
    return obj_mtls

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
        #tgtpaths = []       # list of the new paths to which the images will be published
        imgdict = {}        # master dict where { image_name : object_user, material_user, socket_user}
        totalconfirmedpaths = 0
        theimgs = []
        
        #   ensure file paths are absolute
        #   switch to absolute paths
        print('Set all files to absolute...')
        bpy.ops.file.make_paths_absolute()

        #   thepath
        thepath = os.path.abspath(bpy.path.abspath(bpy.context.scene.publishmaps_to))
        if (len(bpy.context.scene.publishmaps_to) >= 1) and \
            (os.path.exists(bpy.context.scene.publishmaps_to)):
            thepath = os.path.abspath(bpy.path.abspath(bpy.context.scene.publishmaps_to))
            print('\nPublish folder found: ', thepath)
        else:
            print('\nPublish folder NOT found: ', thepath)
            thepath = ''
        
        if len(thepath) >= 1:
            #   oblist : get the objects to process
            if bpy.context.scene.publishmaps_selected:
                oblist = bpy.context.selected_objects
            else:
                oblist = bpy.data.objects
            
            #   mtl_objs : get the unique materials and their images for each object
            for ob in oblist:
                for mtl in ob.material_slots:
                    if mtl.material.use_nodes:
                        if not(mtl.material.name in mtl_objs.keys()):
                            #   gather the images used in this material and the sockets they drive
                            this_mtl_imgs = get_imgs_from_mtl(mtl.material, ob, [], [])
                            mtl_objs[mtl.material.name] = [ob.name, this_mtl_imgs[0], this_mtl_imgs[1]]
                            print(("mtl_objs["+mtl.material.name+"]: "), mtl_objs[mtl.material.name])
                    else:
                        print(mtl.material.name, " is INVALID - must use nodes")
            
            #   imgdict : get the unique images from the collected materials dictionary
            for mtl in mtl_objs.keys():
                for imgnum, img in enumerate(mtl_objs[mtl][1]):
                    if not(img in imgdict.keys()):
                        imgdict[img] = [mtl_objs[mtl][0], mtl, mtl_objs[mtl][2][imgnum]]
            
            #   theimgs : PUBLISHED images from the unique images collected in imgdict
            print("\nThe collected imgdict has ", len(imgdict.keys()), " image(s) to process")
            theimgs = publish_images_from_dict(imgdict,thepath)
                
            #   confirm all image file paths in file
            print("Checking for published images")
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
        layout.prop(scene, "publishmaps_convert")
        layout.prop(scene, "publishmaps_rename")
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
    
    bpy.types.Scene.publishmaps_to = bpy.props.StringProperty(
        name="Publish To:",
        description="Output Directory",
        default="",
        maxlen=1024,
        update = make_path_absolute,
        subtype='DIR_PATH')
    
    bpy.types.Scene.publishmaps_convert = bpy.props.BoolProperty(
        name = "Auro Convert (to EXR)",
        description = "Automatically convert to 16-bit, zip compressed EXR",
        default = True)
    
    bpy.types.Scene.publishmaps_rename = bpy.props.BoolProperty(
        name = "Auto Rename",
        description = "Automatically rename maps to follow abstraction <asset name>_<material>_<map type>_<version#>.<ext>",
        default = True)
    

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.publishmaps_selected
    del bpy.types.Scene.publishmaps_to
    del bpy.types.Scene.publishmaps_convert
    del bpy.types.Scene.publishmaps_rename
    
    
if __name__ == "__main__":
    register()
