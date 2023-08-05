# made in response to --
# The eventual need to collect and repath image maps during the publishing process
## gather information about file
## move all existing published maps and logs into an 'archive' subfolder; create if needed
## copy all maps from the file to the publish directory
## repath all references to the image within the file to the new location
## save the restore of what just happened to the publish directory
## toying with the idea of renaming image files and updating paths during the publish process

# started work to make a new, proper log file, saved to same location as restore file
# proper log should only list maps that were missed because they couldn't be found
# v1.7
## * need to handle packed images; extract and repath
# v1.8
## * update restore code to skip ignored list images
## * update restore to handle previous images that no longer exist where expected
# v1.9
## * implement filecmp module instead of th custom hash test function
# v2.0
## * change paradigm to use lists to handle image paths to get around conflicts on the use of same maps
## * need to update code for sequences
## * v2.2 added a basename comparison to files that already exist (worked with naming clean up issues prior to this update)
## * need to update this check so that the filecmp confirms the data is correct, and then just rename file ONLY if clean names is on
## * need to update so packed files with missing paths get processed; unpacked and published; this should be possible easily with the current code rewrite
## - v2.3
## * added LOCAL vs ORIGINAL location options for unpacking
## * v2.4
## * unpacking is still an issue...can't seem to unpack without generating an image on disk.
## - v2.5
## * resolved unpacking mechanism so file is ALWAYS updacked to parallel unpacked folder
## - removed LOCAL vs ORIGINAL location options for unpacking
## - v2.6
## * added the rest of the property clean up code to the unregister block
# v3.0
## * update for Blender 2.8
## * still need to debug the extra unpacked file that appears in the same location as the blender file
## - check restore logging - seems to be missing - test in 2.7x version too
# v4.0
## * port to Chums using Blender LTS 3.3.1
## ** remove/replace chums specific code
# v4.2
## clean file format to 16 bit floatt EXR in linear space
# v4.3
## see about autonaming new image: <asset name>_<object name>_<map type>_<version#>.<ext>
## switch imagemagick for img conversion
## comment Restore code out; keep logging (for now)
# TARGETS v5.0
## completely remove Restore functionality; keep logging (for now)

bl_info = {
    "name": "Publish Maps",
    "author": "conrad dueck",
    "version": (0,4,3),
    "blender": (3, 30, 1),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Collect image maps to publish directory and back up any maps that already exist there.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

import bpy, os, sys, shutil, datetime, time, filecmp
import subprocess
from pathlib import Path

####    GLOBAL VARIABLES    ####
vsn='4.3h'
imgignorelist = ['Render Result', 'Viewer Node', 'vignette.png']
clean_export_fileformat = 'OPEN_EXR'
clean_export_fileext = 'exr'
clean_export_filedepth = '16'
clean_export_imagick = 'zip'
clean_export_filecodec = 'ZIP'
imagick = Path("C:/Program Files/ImageMagick-7.1.1-Q16-HDRI\convert.exe")

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
    the_next_type = 'none'
    the_next_node = 'none'
    the_id = ''
    for the_out in the_node.outputs:
        if the_out.is_linked:
            for link in the_out.links:
                the_next_type = link.to_node.type
                the_next_node = link.to_node
                the_id = link.to_socket.identifier
    return the_next_type, the_next_node, the_id

def trace_to_shader(image,object):
    my_maptype = 'nonetype'
    for mt in object.material_slots:
        mtl = mt.material
        for node in mtl.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image == image:
                for the_out in node.outputs:
                    if the_out.is_linked:
                        for link in the_out.links:
                            tgt_link = get_node_target(node)
                            while tgt_link[0] != 'BSDF_PRINCIPLED':
                                tgt_link = get_node_target(tgt_link[1])
                                my_maptype = tgt_link
                            break
    print('my_maptype = ', my_maptype)
    return my_maptype

    
    print(image.name + "\n" + 'trace_to_shader returns (my_maptype): ', my_maptype)
    return my_maptype

def convert_to_exr(image):
    import os
    cleanpath = image.replace('\\','/')
    #img_path = image.filepath
    img_name = os.path.basename(cleanpath)
    img_dir = os.path.dirname(cleanpath)
    tgt_path = (cleanpath[:-4] + "_converted_" + ".exr")
    print('tgt_path = ',tgt_path)
    #img_cmd = (str(imagick) + " " + str(Path(image)) + " -compress zip -depth 16 " + str(Path(tgt_path)) + "")
    img_cmd = (str(imagick) + " \"" + str(Path(cleanpath)) + "\" -compress zip -depth 16 \"" + str(Path(tgt_path)) + "\"")
    print("img_cmd = ", img_cmd)
    running = subprocess.Popen(img_cmd)
    running.wait()
    print(running.returncode)
    if os.path.exists(tgt_path):
        return tgt_path
    else:
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
        totalimgs = 0
        totalpubs = 0
        totalbaks = 0
        totalpubskps = 0
        totalarcskps = 0
        anypacks = 0
        totalpacks = 0
        totalmissing = 0
        totalconfirmedpaths = 0
        theFile = os.path.basename(bpy.data.filepath)[:-6]
        thefilepath = os.path.dirname(bpy.data.filepath)
        if len(theFile) >= 4 and len(theFile.split("_")) > 2:
            theasset = theFile[:-5]
        else:
            theasset = "unknown"
        unpacktarget = os.path.join(thefilepath, 'unpacked')
        myalphanum = 'abcdefghijklmnopqrstuvwxyz1234567890'
        imageformats = {'BMP':'.bmp','PNG':'.png','JPEG':'.jpg','JPEG2000':'.jpg',
                        'TARGA':'.tga','TARGA_RAW':'.tga','CINEON':'.cin','DPX':'.dpx',
                        'OpenEXR':'.exr','OPEN_EXR_MULTILAYER':'.exr','OPEN_EXR':'.exr',
                        'HDR':'.hdr','TIFF':'.tif','AVI_JPEG':'.avi','AVI_RAW':'.avi'}
        
        #   set up restore and log files; get date and time and filename and filepath
        now = datetime.datetime.now()
        theDate = (str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2))
        theTime = (str(now.hour).zfill(2)+'.'+str(now.minute).zfill(2))
        thistype = ('texture_publish_restore_' + theFile + '_' + theDate + '_' + theTime + '.txt')
        thislog = ('texture_publish_log_' + theFile + '_' + theDate + '_' + theTime + '.txt')
        #therestorefile = os.path.join(thefilepath, thistype)
        #therestore = open(therestorefile, 'w')
        thelogfile = os.path.join(thefilepath, thislog)
        thelog = open(thelogfile, 'w')
        logmsg = ('chums_publishmaps    version: ' + vsn)
        
        #   temporarily switch to absolute paths
        print('Temporarily set all files to absolute.')
        logmsg += ('\n\nTemporarily set all files to absolute.')
        bpy.ops.file.make_paths_absolute()
        
        #   get the destination/publish path from the UI
        thepath = os.path.abspath(bpy.path.abspath(bpy.context.scene.publishmaps_to))
        if (len(bpy.context.scene.publishmaps_to) >= 1) and (os.path.exists(bpy.context.scene.publishmaps_to)):
            thepath = os.path.abspath(bpy.path.abspath(bpy.context.scene.publishmaps_to))
            print('\nPublish folder found: ', thepath)
            logmsg += ('\nPublish folder found: ' + thepath)
        else:
            print('\nPublish folder NOT found: ', thepath)
            logmsg += ('\nPublish folder NOT found: ' + thepath)
            thepath = ''
        
        #   if the path is defined
        if len(thepath) >= 1:
            #   gather up a list of the images to process
            if bpy.context.scene.publishmaps_selected:
                oblist = bpy.context.selected_objects
                logmsg += ('\nPublishing images from selection only.')
            else:
                oblist = bpy.data.objects
                logmsg += ('\nPublishing all images in all materials on all objects.')
            
            for ob in oblist:
                for mtl in ob.material_slots:
                    if mtl.material.use_nodes:
                        for node in mtl.material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                if node.image.packed_file:
                                    anypacks += 1
                                this_image = os.path.basename(node.image.filepath)
                                img = node.image
                                thismaptype = trace_to_shader(img,ob)
                                this_to_socket = thismaptype[2].replace(' ','_')
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
                                        totalmissing += 1
                                        logmsg += ('\nMISSING SOURCE: ' + node.image.filepath)
            print('\nList to process:\n ', theimgs)
            
            #   handle missing unpack folder if there are any packed files
            if anypacks >= 1 and not(os.path.exists(unpacktarget)):
                os.mkdir(unpacktarget, 0o777)
                print('\nUnpack folder NOT found. Created: ' + unpacktarget)
                logmsg += ('\nUnpack folder NOT found. Created: ' + unpacktarget)
            else:
                print('\nUnpack folder FOUND: ', unpacktarget)
            
            #   log name cleaning option
            if bpy.context.scene.publishmaps_cleanup == True:
                print('Clean up is ON')
                logmsg += ('\nClean up is ON')
            else:
                print('Clean up is OFF')
                logmsg += ('\nClean up is OFF')
            
            #   cycle thru images and collect original paths (theoldpaths) and generate the new image paths (tgtpaths)
            for imgnum in range(len(theimgs)):
                totalimgs += 1
                img = theimgs[imgnum]
                thisobject = theobjects[imgnum]
                srcfile = theoldpaths[imgnum]
                srcpath = os.path.dirname(srcfile)
                srcfilename = os.path.basename(srcfile)
                clean_export_fileext = 'exr'
                
                print('imgnum = ', imgnum)
                print('img = ', img)
                print('commence processing ', img.name)
                
                #   handle clean up - file format
                if bpy.context.scene.publishmaps_cleanup == True:
                    tgtformat = clean_export_fileformat
                else:
                    tgtformat = img.file_format
                
                srcformat = img.file_format
                srctype = theimgtypes[imgnum]
                theoldname = os.path.basename(theoldpaths[imgnum])
                
                #   UNPACK if the image is PACKED into the file
                if img.packed_file:
                    totalpacks += 1
                    logmsg += ('\n\nPACKED FILE:        ' + img.name)
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
                    logmsg += ('\nfile unpacked to:   ' + newpath)
                    logmsg += ('\nexists:             ' + str(os.path.exists(newpath)))
                    img.unpack(method='USE_ORIGINAL')
                    curpath = img.filepath
                    srcfile = img.filepath
                    bpy.context.scene.render.image_settings.file_format = curformat
                
                #   handle clean up - file name
                #   <asset name>_<object name>_<map type>_<version#>.<ext>
                if bpy.context.scene.publishmaps_cleanup == True:
                    thismaptype = trace_to_shader(img,bpy.data.objects[thisobject])
                    customname = (theasset + "_" + thisobject + "_" + thismaptype[2].replace(' ','_') + "." + clean_export_fileext)
                    tgtfilename = customname.replace(' ', '_')
                    tgtfilename = tgtfilename.replace(":","_")
                    tgtfilename_ext = tgtfilename.split(".")[-1]
                    tgtfilename = tgtfilename.replace(tgtfilename_ext,clean_export_fileext)
                else:
                    tgtfilename = theoldname
                dupfix = 0
                tgtpath = os.path.join(thepath, tgtfilename)
                #   publish already exists
                while os.path.exists(tgtpath):
                    tgtpath = tgtpath.replace(('.'+clean_export_fileext),('_' + str(dupfix).zfill(3) + '.' + clean_export_fileext))
                    dupfix += 1
                tgtpaths.append(tgtpath)
                print('srcfile = ', srcfile,'\nsrcpath = ', srcpath,'\nsrcfilename = ', srcfilename,'\nsrcformat = ', srcformat,'\nsrctype = ', srctype, '\n')
                print('tgtfile = ', (thepath + tgtfilename),'\ntgtpath = ', tgtpath,'\ntgtfilename = ', tgtfilename,'\ntgtformat = ', tgtformat,'\ntgttype = ', srctype, '\n')
                
                
            #   process the image list
            for imgnum in range(len(theimgs)):
                print('imgnum:', imgnum)
                img = theimgs[imgnum]
                print('img:', img)
                srcfile = theoldpaths[imgnum]
                print('srcfile:', srcfile)
                srcformat = img.file_format
                srcext = srcfile[-3:]
                srctype = theimgtypes[imgnum]
                theoldname = os.path.basename(theoldpaths[imgnum])
                realsrcpath = os.path.realpath(bpy.path.abspath(srcfile))
                tgtfile = tgtpaths[imgnum]
                tgtfilename = os.path.basename(tgtpaths[imgnum])
                print('\nProcessing ', srcformat, ' image: ', theoldname)
                print('    src: ', srcfile)
                print('    tgt: ', tgtfile)
                logmsg += ('\n\nProcessing image:       ' + theoldname + '\n    source file:        ' + srcfile + '\n    exists:             ' + str(os.path.exists(srcfile)) + '\n    type:               ' + srctype + '\n    new image path:     ' + tgtfile)
                
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
                    logmsg += ('\n    published new:      ' + str(theframecount) + ' frame sequence: ' + tgtfile)
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
                    logmsg += ('\n    published new:      ' + tgtfile)
            
                themsg = ('\n' + img.name)
                themsg += (',' + srcfile)
                themsg += (',' + tgtfile)
                
            #   user driven option make all paths relative again
            if bpy.context.scene.relative_paths:
                logmsg += ('\n\nSetting all file paths back to relative.')
                bpy.ops.file.make_paths_relative()
            else:
                logmsg += ('\n\nSetting all file paths to absolute.')
                bpy.ops.file.make_paths_absolute()
                
            #   confirm all image file paths in file
            logmsg += ('\n\nConfirming all new path integrity')
            for imgnum in range(len(theimgs)):
                img = theimgs[imgnum]
                if not(img.name in imgignorelist):
                    thisrealpath = os.path.realpath(bpy.path.abspath(img.filepath))
                    logmsg += ('\n    confirming: ' + img.filepath + '\n                ' + thisrealpath)
                    if not(os.path.exists(os.path.realpath(bpy.path.abspath(img.filepath)))):
                        print('\nFAILED to find: ' + os.path.realpath(bpy.path.abspath(img.filepath)))
                        logmsg += ('\n       MISSING: ' + thisrealpath)
                    else:
                        print('\n    FOUND: ' + thisrealpath)
                        logmsg += ('\n         FOUND: ' + thisrealpath)
                        totalconfirmedpaths += 1
                
            #   log restore file
            #if bpy.context.scene.publishmaps_restore:
            #    bpy.context.scene.publishmaps_restore = therestorefile
            #logmsg += ('\n\nThe restore file for this publish is: ' + str(therestorefile))
            
            #   log totals
            logmsg += ('\n\nTotal images processed: ' + str(totalimgs) + \
                       '\nTotal images unpacked: ' + str(totalpacks) + \
                       '\nTotal images published: ' + str(totalpubs) + \
                       '\nTotal images archived: ' + str(totalbaks) + \
                       '\nTotal publishes skipped: ' + str(totalpubskps) + \
                       '\nTotal archives skipped: ' + str(totalarcskps) + \
                       '\n\nTotal confirmed publishes: ' + str(totalconfirmedpaths))
            print('Done.')
        #   close log files and finish
        thelog.write(logmsg)
        #therestore.close()
        thelog.close()
        print('COMPLETE PUBLISH')
        return{'FINISHED'}

'''#   OPERATOR publishmapsrestore RESTORE
class BUTTON_OT_publishmapsrestore(bpy.types.Operator):
    #Restore From Log
    bl_idname = "publishmaps.restore"
    bl_label = "Restore From Log"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('\n\nSTART RESTORE')
        imglist = []
        totalfound = 0
        totalrestored = 0
        totalskipped = 0
        #   check for a restore log from the UI
        if (len(bpy.context.scene.publishmaps_restore) >= 1) and (os.path.exists(bpy.context.scene.publishmaps_restore)):
            thepath = bpy.context.scene.publishmaps_restore
        else:
            thepath = ''
        
        #   set up restore log files; get date and time and filename and filepath
        now = datetime.datetime.now()
        theDate = (str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2))
        theTime = (str(now.hour).zfill(2)+'.'+str(now.minute).zfill(2))
        theFile = os.path.basename(bpy.data.filepath)[:-6]
        thefilepath = os.path.dirname(bpy.data.filepath) 
        thislog = ('texture_restore_log_' + theFile + '_' + theDate + '_' + theTime + '.txt')
        restorelogfile = os.path.join(thefilepath, thislog)
        restorelog = open(restorelogfile, 'w')
        logmsg = ('chums_publishmaps    version: ' + vsn)
        logmsg += ('\nRESTORING FROM: ' + thepath)
        
        #   switch to absolute paths
        bpy.ops.file.make_paths_absolute()
        
        #   open restore log file
        if (len(thepath) >= 1) and os.path.exists(thepath):
            therestorelog = open(thepath, 'r')
            therestorelines = therestorelog.readlines()
            therestorelog.seek(0)
            therestoretext = therestorelog.read()
        #   cycle thru images in local scene
            for img in bpy.data.images:
                if not(img.is_library_indirect) and not(img.name in imgignorelist):
                    print('\nLOOKING FOR:', img.name)
                    logmsg += ('\n\nLooking for: ' + img.name)
                    theline = 0
                    texturepath = img.filepath
                    thename = img.name
                    thisname = os.path.basename(texturepath)
                    for thisline in therestorelines:
                        listline = thisline.split(',')
                        if len(listline) >= 2:
                            if thename in listline:
                                theline += 1
                                thepos = listline.index(thename)
                                #   restore original path
                                if os.path.exists(listline[1]):
                                    totalfound += 1
                                    totalrestored += 1
                                    print('found image:', listline[0])
                                    logmsg += ('\n    Found: ' + listline[0])
                                    print('revert path to:', listline[1])
                                    logmsg += ('\n   Revert: ' + listline[1])
                                    img.filepath = (listline[1])
                                    imglist.append(thisname)
                                else:
                                    totalskipped += 1
                                    print('could not find old path for', listline[0])
                                    logmsg += ('\nmissing image: ' + listline[0] + '\nskipped')
                                    print('keeping current path')
                #   close restore log
            therestorelog.close()
        
        #   user driven option make all paths relative again
        if bpy.context.scene.relative_paths:
            bpy.ops.file.make_paths_relative()
        else:
            bpy.ops.file.make_paths_absolute()
        
        #   confirm all scene images
        print('\nConfirming all new path integrity')
        logmsg += ('\n\nConfirming restored path integrity')
        for img in bpy.data.images:
            if not(img.name in imgignorelist):
                print('confirming:', img.filepath, os.path.realpath(bpy.path.abspath(img.filepath)))
                logmsg += ('\nConfirming:\n    ' + img.filepath + '\n    ' + os.path.realpath(bpy.path.abspath(img.filepath)))
                if not(os.path.exists(os.path.realpath(bpy.path.abspath(img.filepath)))):
                    print('\nFAILED to find: ' + os.path.realpath(bpy.path.abspath(img.filepath)))
                    logmsg += ('\nFAILED to find:\n    ' + os.path.realpath(bpy.path.abspath(img.filepath)))
        
        print('Total images found in log: ', totalfound)
        print('Total images restored: ', totalrestored)
        print('Total images repathed: ', len(imglist))
        print('Total images skipped: ', totalskipped)
        
        logmsg += ('\n\nTotal images found in log: '+ str(totalfound))
        logmsg += ('\nTotal images restored: '+ str(totalrestored))
        logmsg += ('\nTotal images repathed: '+ str(len(imglist)))
        logmsg += ('\nTotal images skipped: '+ str(totalskipped))
        
        restorelog.write(logmsg)
        restorelog.close()
        print('COMPLETE RESTORE')
        return{'FINISHED'}
'''
        
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
        layout.prop(scene, "relative_paths")
        layout.operator("publishmaps.publish", text=(BUTTON_OT_publishmapspublish.bl_label))
        #layout.prop(scene, "publishmaps_restore", text="")
        #layout.operator("publishmaps.restore", text=(BUTTON_OT_publishmapsrestore.bl_label))
        

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
        name = "Clean Up",
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
