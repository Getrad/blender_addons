# made in response to:
# The eventual need to collect and repath image maps during the publishing process
# v5.5
# need to properly handle all scene images when only selected is not enabled
# need to test functionality of skipping images when the image node can't find a shader connection

bl_info = {
    "name": "Publish Maps",
    "author": "conrad dueck",
    "version": (0,5,8),
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
vsn='5.8a'
imgignorelist = ['Render Result', 'Viewer Node', 'vignette.png', 'lsTex']
nodeignorelist = ['Render Result', 'Viewer Node', 'lsTex']
grpignorelist = ['ZenUV_Override']
clean_export_fileformat = 'OPEN_EXR'
clean_export_fileext = 'exr'
clean_export_filedepth = '16'
clean_export_imagick = 'zip'
clean_export_filecodec = 'ZIP'
imagick = Path("C:/Program Files/ImageMagick-6.9.13-Q16-HDRI/convert.exe")

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
    #print("    compare2files: ", f1, f2)
    matched = False
    absf1 = os.path.abspath(bpy.path.abspath(f1))
    absf2 = os.path.abspath(bpy.path.abspath(f2))
    #print("    compare2files: ", absf1, absf2)
    hashlist = [(hashlib.sha256(open(fname, 'rb').read()).hexdigest()) for fname in (absf1, absf2)]
    if (hashlist[0] == hashlist[1]):
        matched = True
    else:
        matched = False
    print('    compare2files:  sha256 hash comparison match = ', matched)
    return matched

def convert_to_exr(image):
    import os
    #print("convert_to_exr(image): ", image)
    convert_cleanpath = image
    targetpath_file = ("autoconvert_" + os.path.basename(convert_cleanpath))
    convert_tgt_path = (targetpath_file[:-4] + ".exr")
    convert_img_cmd = ("\"" + str(imagick) + "\" \"" + str(Path(convert_cleanpath)) + "\" -compress zip -depth 16 \"" + str(Path(convert_tgt_path)) + "\"")
    running = subprocess.Popen(convert_img_cmd)
    running.wait()
    #print(running.returncode)
    if os.path.exists(convert_tgt_path):
        #print("convert_to_exr returning (success): ", convert_tgt_path)
        return convert_tgt_path
    else:
        #print("convert_to_exr returning (failed): ", image)
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
    curformat = bpy.context.scene.render.image_settings.file_format
    bpy.context.scene.render.image_settings.file_format = srcformat
    theext = imageformats[srcformat]
    srcfilebase = (packed_img.name).split(".")[0]
    srcfilename = (srcfilebase + theext)
    newpath = os.path.join(unpacktarget, srcfilename)
    thisversion = 0
    while os.path.exists(newpath):
        #print('      ITERATIVE existence check - newpath = ', newpath)
        tempname = (srcfilename[:-4] + '_' + str(thisversion).zfill(3) + theext)
        #print('   tempname: ', tempname)
        newpath = os.path.join(unpacktarget, tempname)
        thisversion += 1
    packed_img.save_render(newpath, scene=bpy.context.scene)
    packed_img.filepath = newpath
    packed_img.unpack(method='USE_ORIGINAL')
    bpy.context.scene.render.image_settings.file_format = curformat

    return 0

def cleanup_string(my_string):
    my_string = my_string.replace(" ", "")
    my_string = my_string.replace(".", "")
    my_string = my_string.replace("_", "")
    
    return my_string

def get_imgs_from_mtl(my_mtl, my_imglist):
    for node in my_mtl.node_tree.nodes:
        print("node.name = ", node.name)
        if node.name in nodeignorelist:
            print("SKIPPING ignore list node: ", node.name)
        else:
            if node.type == 'TEX_IMAGE' and node.image.source in ['SEQUENCE', 'FILE']:
                img = node.image
                if img.packed_file:
                    unpack_image(img)
                if not(img in my_imglist):
                    my_imglist.append(img)
            elif node.type == 'GROUP' and not(node.name in grpignorelist):
                get_imgs_from_mtl(node,my_imglist)
    #print("fn get_imgs_from_mtl (my_imglist): ", my_imglist)
    return (my_imglist)

def get_node_target(the_node):
    the_id = None
    theouts = [a for a in the_node.outputs if a.is_linked == True]
    target_found = False
    for thisout in theouts:
        if target_found:
            break  # Break out of the outer loop if target is found
        for link in thisout.links:
            if link.to_node.type == 'BSDF_PRINCIPLED':
                the_id = link.to_socket.name
                target_found = True  # Set the flag to True
                break  # Break out of the inner loop
            else:
                the_id = get_node_target(link.to_node)  # Recursively call the function
                if the_id:  # If the_id is not None, target is found
                    target_found = True
                    break  # Break out of the inner loop
    #print("fn get_node_target (the_id): ", the_id)
    return the_id

def trace_to_shader(image, mtl):
    #print("fn trace_to_shader - get (this_shader_input) from (image, mtl): ", image, mtl)
    target_found = False
    this_shader_input = None
    for node in bpy.data.materials[mtl].node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image == image:
            for the_out in node.outputs:
                if target_found:
                    break  # Break out of the outer loop if target is found
                if the_out.is_linked:
                    this_shader_input = get_node_target(node)
                    print("this output: ", the_out, "is linked to", this_shader_input)
                    #print("my_shader_input: ", this_shader_input)
                    target_found = True
                    break
            break
    #print("\nfn trace_to_shader (this_shader_input) returns: ", this_shader_input)
    if this_shader_input == None:
        this_shader_input = "NotConnected"
    return this_shader_input

def get_asset_from_filename():
    my_version = ""
    number_digits = "0123456789_"
    thefilebase = os.path.basename(bpy.data.filepath)[:-6]
    if len(thefilebase) >= 4 and len(thefilebase.split("_")) > 2:
        my_asset = thefilebase.split("_")[0]
        my_version = thefilebase.split("_")[-1]
        for tkn in thefilebase.split("_")[1:]:
            if tkn[0] == "v" and (tkn[1] in number_digits):
                my_version = tkn
                break
            else:
                my_asset += ("_" + tkn)
                my_version = "000"
    else:
        my_asset = "unknown"
        my_version = "000"
    return my_asset, my_version

def collect_materials(objlist):
    my_mtls = []
    for ob in objlist:
        for mtl in ob.material_slots:
            if mtl.material.use_nodes:
                if not(mtl.material.name in my_mtls):
                    #   build list of unique materials
                    my_mtls.append(mtl.name)
    return my_mtls

def build_image_dict(my_mtls):
    my_mtl_imgs = {}
    for mtl in my_mtls:
        this_mtl_imgs = get_imgs_from_mtl(bpy.data.materials[mtl], [])
        for img in this_mtl_imgs:
            if not(mtl in my_mtl_imgs.keys()):
                my_mtl_imgs[mtl] = [[img], []]
            else:
                my_mtl_imgs[mtl][0].append(img)
        #print("my_mtl_imgs[mtl]: ", my_mtl_imgs[mtl])
    return my_mtl_imgs

def build_image_socket_dict(my_mtl_imgs):
    for mtl in my_mtl_imgs.keys():
        for img in my_mtl_imgs[mtl][0]:
            tgt_socket = trace_to_shader(img, mtl)
            my_mtl_imgs[mtl][1].append(tgt_socket)
        #print("my_mtl_imgs[mtl]: ", my_mtl_imgs[mtl])
    return my_mtl_imgs

def build_imgdict(my_mtl_imgs,map_skip):
    my_imgdict = {}
    for mtl in my_mtl_imgs.keys():
        print("\nIN mtl my_mtl_imgs[", mtl, "] : ", my_mtl_imgs[mtl])
        for imgnum, img in enumerate(my_mtl_imgs[mtl][0]):
            if not(img in my_imgdict.keys()):
                if map_skip:
                    if (my_mtl_imgs[mtl][1][imgnum] == "NotConnected"):
                        print("SKIPPED not connected: ", img)
                    else:
                        my_imgdict[img.name] = [mtl, my_mtl_imgs[mtl][1][imgnum]]
                else:
                    my_imgdict[img.name] = [mtl, my_mtl_imgs[mtl][1][imgnum]]
                #print("my_imgdict[",img.name, "]: ", my_imgdict[img.name])
    return my_imgdict

def automatic_publish_path(assetname, assetversion):
    thetexroot = ''
    thefiledir = os.path.dirname(bpy.data.filepath)
    for tkn in thefiledir.split("\\"):
        if not(tkn == "30_texture"):
            if tkn[-1] == ":":
                tkn += "\\"
            thetexroot = os.path.join(thetexroot, tkn)
            #print("thetexroot: ", thetexroot, os.path.exists(thetexroot))
        else:
            thetexroot = os.path.join(thetexroot, tkn, "textures", "production", assetversion)
            break
    return thetexroot

def publish_images_from_dict(my_dict,target_path,map_convert,map_rename,map_skip):
    my_imgs = []
    thefilebase = os.path.basename(bpy.data.filepath)[:-6]
    theasset = get_asset_from_filename()[0]
    print('   theasset = ', theasset)

    #   PUBLISH images in image dictionary
    print("\n   collected my_dict has the following ", len(my_dict.keys()), " image(s) to process")
    for bb in my_dict.keys():
        print("      ", bb)
    for imgnum, img in enumerate(my_dict.keys()):
        print("   Commence processing: ", img)
        proc_img = bpy.data.images[img]
        srcfile = proc_img.filepath
        srcfilepath = os.path.dirname(srcfile)
        srcfilename = os.path.basename(srcfile)
        print("               srcfile: ", srcfile)
        srcfilebase = srcfilename.split(".")[0]
        srcfiletype = srcfilename.split(".")[1]
        if (len(srcfilebase.split("_")[-1]) == 4) and srcfilebase.split("_")[-1][0] == "v":
            srcfileversion = srcfilebase.split("_")[-1]
        else:
            srcfileversion = "v000"
        #srcformat = srcfilename.split(".")[-1]
        img_material = my_dict[img][0]
        img_socket = my_dict[img][1]
        if map_convert:
            my_ext = clean_export_fileext
        else:
            my_ext = srcfiletype
        if map_rename:
            # <asset name>_<material>_<map type>_<version#>.<ext>
            mtl_name = img_material.split(":")[-1].replace("_", "").lower()
            clean_mtl_name = cleanup_string(mtl_name)
            sock_name = (img_socket.replace("_", "")).lower()
            clean_sock_name = cleanup_string(sock_name)
            tgtfilename = (theasset+"_"+clean_mtl_name+"_"+clean_sock_name+"_"+srcfileversion)
        else:
            tgtfilename = srcfilebase
        tgtfilename = (tgtfilename+"."+my_ext)
        while "autoconvert_autoconvert_" in tgtfilename:
            tgtfilename = tgtfilename.replace("autoconvert_autoconvert_", "autoconvert_")
        print("   publishmaps_rename using: ", tgtfilename, "\n      on: ", srcfilename)
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
                proc_img.filepath = tgtpath
                break
            else:
                if tgtbase[-4] == "_":
                    tgtbase = tgtbase[:-4]
                tgtpath = os.path.join(os.path.dirname(tgtpath), (tgtbase + "_" + str(dupfix).zfill(3) + '.' + clean_export_fileext))
                need_new = True
                dupfix += 1
        srcscope = proc_img.source
        tgtfile = tgtpath
        print('      src: ', srcfile)
        print('      tgt: ', tgtfile)
        print('      new: ', need_new)
        if (need_new == True):
            if srcscope == 'SEQUENCE':
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
                            if map_convert:
                                cleanfullpath = convert_to_exr(Path(srcfile))
                                shutil.copy2(cleanfullpath, target_path)
                            else:
                                shutil.copy2(flfullpath, target_path)
                            theframecount += 1
                proc_img.filepath = tgtfile
            else:
                if srcscope == 'FILE':
                    if (need_new == True):
                        if map_convert:
                            newfile = convert_to_exr(Path(srcfile))
                        else:
                            newfile = srcfile
                        shutil.copy2(newfile, tgtfile)
                        proc_img.filepath = tgtfile
                else:
                    print("NOT SUPPORTEED IMAGE TYPE: ", srcscope, " - SKIPPED")
            my_imgs.append(proc_img)
    return my_imgs

def headless_publish(pmap_selected,pmap_path,pmap_convert,pmap_rename,pmap_skiphangers):
    #   initialize operational variables and empty lists
    oblist = []         # list of objects to process
    mtl_imgs = {}       # dict of materials - [material name]:[object_user, images_list, socket_list]
    mtls = []           # list of unique materials to process
    theimgs = []        # list of unique images to process
    imgdict = {}        # master dict where { image_name : object_user, material_user, socket_user}
    #   switch to absolute paths
    bpy.ops.file.make_paths_absolute()
    #   thepath
    if len(pmap_path) < 1:
        assetname = get_asset_from_filename()[0]
        assetversion = get_asset_from_filename()[1]
        thepath = automatic_publish_path(assetname, assetversion)
    else:
        thepath = pmap_path
    if not(os.path.exists(thepath)):
        os.mkdir(thepath)
    #   objects (oblist)
    if pmap_selected:
        oblist = [o for o in bpy.data.collections['asset_prod'].objects if o.type == 'MESH']
    else:
        oblist = [o for o in bpy.data.objects if o.type == 'MESH']
    #   mtls: get the unique materials
    mtls = collect_materials(oblist)
    #   mtl_imgs : get the unique images for each material (first mtl array)
    mtl_imgs = build_image_dict(mtls)
    #   mtl_imgs : get the sockets used by each unique image (second socket array)
    mtl_imgs = build_image_socket_dict(mtl_imgs)
    #   imgdict : get the unique images from the collected materials dictionary
    imgdict = build_imgdict(mtl_imgs,pmap_skiphangers)
    #   theimgs : PUBLISH images from the unique images collected in imgdict
    theimgs = publish_images_from_dict(imgdict,thepath,pmap_convert,pmap_rename,pmap_skiphangers)

    return theimgs

def confirm_publish(pmap_imgs):
    found = 0
    failed = 0
    for imgnum, img in enumerate(pmap_imgs):
        img = pmap_imgs[imgnum]
        if not(img.name in imgignorelist):
            thisrealpath = os.path.realpath(bpy.path.abspath(img.filepath))
            if not(os.path.exists(thisrealpath)):
                print('    FAILED to find: ' + thisrealpath)
                failed += 1
            else:
                print('    FOUND: ' + thisrealpath)
                found += 1
    return found, failed

####    CLASSES    ####
#   OPERATOR publishmapspublish PUBLISH MAPS
class BUTTON_OT_publishmapspublish(bpy.types.Operator):
    '''Publish Maps'''
    bl_idname = "publishmaps.publish"
    bl_label = "Publish Maps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('\n\n\n********** START PUBLISH **********')
    #   initialize operational variables and empty lists
        oblist = []         # list of objects to process
        mtl_imgs = {}       # dict of materials - [material name]:[object_user, images_list, socket_list]
        mtls = []           # list of unique materials to process
        theimgs = []        # list of unique images to process
        imgdict = {}        # master dict where { image_name : object_user, material_user, socket_user}
        
    #   switch to absolute paths
        bpy.ops.file.make_paths_absolute()
        theimgs = headless_publish(bpy.context.scene.publishmaps_selected,
                                   bpy.context.scene.publishmaps_to,
                                   bpy.context.scene.publishmaps_convert,
                                   bpy.context.scene.publishmaps_rename,
                                   bpy.context.scene.publishmaps_skiphangers)
        print('COMPLETE PUBLISH')
        #   confirm all image file paths in file
        confirm_publish(theimgs)
        print('COMPLETE PUBLISH CHECK')
        
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
        layout.prop(scene, "publishmaps_skiphangers")
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
        name = "Auto Convert (to EXR)",
        description = "Automatically convert to 16-bit, zip compressed EXR",
        default = True)
    bpy.types.Scene.publishmaps_rename = bpy.props.BoolProperty(
        name = "Auto Rename",
        description = "Automatically rename maps to follow abstraction <asset name>_<material>_<map type>_<version#>.<ext>",
        default = True)
    bpy.types.Scene.publishmaps_skiphangers = bpy.props.BoolProperty(
        name = "Skip Hanging Maps",
        description = "Skip maps that appear to not be connected to the material output, but remain in the material node tree.",
        default = True)
    

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.publishmaps_selected
    del bpy.types.Scene.publishmaps_to
    del bpy.types.Scene.publishmaps_convert
    del bpy.types.Scene.publishmaps_rename
    del bpy.types.Scene.publishmaps_skiphangers
    
    
if __name__ == "__main__":
    register()
