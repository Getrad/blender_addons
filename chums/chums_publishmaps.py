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
## ** remove/replace Tangent specific code

bl_info = {
    "name": "Publish Maps",
    "author": "conrad dueck",
    "version": (0,4,0),
    "blender": (3, 30, 1),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Collect image maps to publish directory and back up any maps that already exist there.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

import bpy, os, sys, shutil, datetime, time, filecmp

####    GLOBAL VARIABLES    ####
vsn='4.0'
imgignorelist = ['Render Result', 'Viewer Node']


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
        themtls = []     # list of materials
        theimgs = []     # list of images to process
        theimgtypes = [] # list of image types mapped to theimgs
        theoldpaths = [] # list of image paths used by theimgs
        thenewpaths = [] # list of the new paths to which the images will be published
        thearcpaths = [] # list of the archive paths for archiving previous publishes of theimgs
        totalimgs = 0
        totalpubs = 0
        totalbaks = 0
        totalpubskps = 0
        totalarcskps = 0
        anypacks = 0
        totalpacks = 0
        totalmissing = 0
        totalconfirmedpaths = 0
        unpacktarget = os.path.join(os.path.dirname(bpy.data.filepath), 'unpacked')
        myalphanum = 'abcdefghijklmnopqrstuvwxyz1234567890'
        imageformats = {'BMP':'.bmp','PNG':'.png','JPEG':'.jpg','JPEG2000':'.jpg',
                        'TARGA':'.tga','TARGA_RAW':'.tga','CINEON':'.cin','DPX':'.dpx',
                        'OpenEXR':'.exr','OPEN_EXR_MULTILAYER':'.exr','OPEN_EXR':'.exr',
                        'HDR':'.hdr','TIFF':'.tif','AVI_JPEG':'.avi','AVI_RAW':'.avi'}
        
        #   set up restore and log files; get date and time and filename and filepath
        now = datetime.datetime.now()
        theDate = (str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2))
        theTime = (str(now.hour).zfill(2)+'.'+str(now.minute).zfill(2))
        theFile = os.path.basename(bpy.data.filepath)[:-6]
        thefilepath = os.path.dirname(bpy.data.filepath) 
        thistype = ('texture_publish_restore_' + theFile + '_' + theDate + '_' + theTime + '.txt')
        thislog = ('texture_publish_log_' + theFile + '_' + theDate + '_' + theTime + '.txt')
        therestorefile = os.path.join(thefilepath, thistype)
        therestore = open(therestorefile, 'w')
        thelogfile = os.path.join(thefilepath, thislog)
        thelog = open(thelogfile, 'w')
        logmsg = ('tangent_publishmaps    version: ' + vsn)
        
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
            #   check for archive directory and create if needed
            archivedir = os.path.join(thepath, 'archive')
            if not(os.path.exists(archivedir)):
                os.mkdir(archivedir)
                print('\nArchive folder NOT found. Created: ' + archivedir)
                logmsg += ('\nArchive folder NOT found. Created: ' + archivedir)
            else:
                print('\nArchive folder found: '+archivedir)
                logmsg += ('\nArchive folder found: ' + archivedir)
            
            #   gather up a list of the images to process
            if bpy.context.scene.publishmaps_selected:
                logmsg += ('\nPublishing images from selection only.')
                for ob in bpy.context.selected_objects:
                    for mtl in ob.material_slots:
                        if mtl.material.use_nodes:
                            for node in mtl.material.node_tree.nodes:
                                if node.type == 'TEX_IMAGE':
                                    if node.image.packed_file:
                                        anypacks += 1
                                    if not(node.image in theimgs) and not(node.image.name in imgignorelist):
                                        if node.image.packed_file or os.path.exists(node.image.filepath):
                                            theimgs.append(node.image)
                                            theoldpaths.append(node.image.filepath)
                                            theimgtypes.append(node.image.source)
                                        else:
                                            print('MISSING: ', node.image.filepath)
                                            totalmissing += 1
                                            logmsg += ('\nMISSING SOURCE: ' + node.image.filepath)
            else:
                logmsg += ('\nPublishing all images in the file.')
                for img in bpy.data.images:
                    if img.packed_file:
                        anypacks += 1
                    if not(img.name in imgignorelist):
                        if img.packed_file or os.path.exists(img.filepath):
                            theimgs.append(img)
                            theoldpaths.append(img.filepath)
                            theimgtypes.append(img.source)
                        else:
                            print('MISSING: ', img.filepath)
                            totalmissing += 1
                            logmsg += ('\nMISSING SOURCE: ' + img.filepath)
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
                print('Clean up naming is ON')
                logmsg += ('\nClean up naming is ON')
            else:
                print('Clean up naming is OFF')
                logmsg += ('\nClean up naming is OFF')
            
            #   cycle thru images and collect original paths (theoldpaths) and generate the new image paths (thenewpaths) and archive paths (thearcpaths)
            for imgnum in range(len(theimgs)):
                totalimgs += 1
                img = theimgs[imgnum]
                srcfile = theoldpaths[imgnum]
                srcpath = os.path.dirname(srcfile)
                srcfilename = os.path.basename(srcfile)
                srcformat = img.file_format
                srctype = theimgtypes[imgnum]
                theoldname = os.path.basename(theoldpaths[imgnum])
                print('imgnum = ', imgnum)
                print('img = ', img)
                print('commence processing ', img.name)
                print('srcfile = ', srcfile,
                      '\nsrcpath = ', srcpath,
                      '\nsrcfilename = ', srcfilename,
                      '\nsrcformat = ', srcformat,
                      '\nsrctype = ', srctype, '\n')
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
                    #tempname = (img.name + theext)
                    #newpath = os.path.join(unpacktarget, tempname)
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
                #   clean the name if needed, set the 'thenewname' variable
                if bpy.context.scene.publishmaps_cleanup == True:
                    thenewname = theoldname.replace(' ', '_').lower()
                else:
                    thenewname = theoldname
                thenewpath = os.path.join(thepath, thenewname)
                thenewpaths.append(thenewpath)
                thearcpath = os.path.join(archivedir, theoldname)
                thearcpaths.append(thearcpath)
            
            #   process the 3 (old, archive, new) lists
            for imgnum in range(len(theimgs)):
                img = theimgs[imgnum]
                srcfile = theoldpaths[imgnum]
                srcformat = img.file_format
                srcext = srcfile[-3:]
                srctype = theimgtypes[imgnum]
                theoldname = os.path.basename(theoldpaths[imgnum])
                realsrcpath = os.path.realpath(bpy.path.abspath(srcfile))
                arcfile = thearcpaths[imgnum]
                tgtfile = thenewpaths[imgnum]
                thenewname = os.path.basename(thenewpaths[imgnum])
                print('\nProcessing ', srcformat, ' image: ', theoldname)
                print('    src: ', srcfile)
                print('    tgt: ', tgtfile)
                print('    arc: ', arcfile)
                logmsg += ('\n\nProcessing image:       ' + theoldname + 
                           '\n    source file:        ' + srcfile + 
                           '\n    exists:             ' + str(os.path.exists(srcfile)) + 
                           '\n    type:               ' + srctype + 
                           '\n    new image path:     ' + tgtfile +
                           '\n    archive image path: ' + arcfile)
            
                #   publish already exists
                if os.path.exists(tgtfile):
                    print('    found existing publish file')
                    logmsg += ('\n    found existing publish file: ' + tgtfile)
                    
                    #   archive already exists
                    if os.path.exists(arcfile):
                        print('    found arcfile')
                        logmsg += ('\n    archive file already exists')
                        #   check for a match to existing tgtfile
                        if (filecmp.cmp(tgtfile, arcfile, shallow=False)):
                            if not(os.path.basename(tgtfile) == os.path.basename(arcfile)):
                                correctname = os.path.join(os.path.dirname(arcfile), os.path.basename(tgtfile))
                                os.replace(arcfile, correctname)
                            #   skip
                            print('    matching arcfile, so skipping archive step')
                            totalarcskps += 1
                            logmsg += ('\n    archive matches, skipping: ' + arcfile)
                        else:
                            logmsg += ('\n    archive does not match existing publish.')
                            if srctype == 'SEQUENCE':
                                #   delete existing and ARCHIVE sequence
                                print('    existing arcfile SEQUENCE does NOT match, need to delete and copy current tgtfile as new archive')
                                #   check if the arcfile is being used as a srcfile before deleting 
                                if arcfile in theoldpaths:
                                    print('    arcfile is being used as source, so leave arcfile and publish')
                                    totalarcskps += 1
                                    logmsg += ('\n    skipped archive used as source: ' + arcfile)
                                else:
                                    theframecount = 0
                                    thearccount = 0
                                    arcpath = os.path.dirname(arcfile)
                                    srcbasename = removedigits(theoldname)
                                    tgtbasename = removedigits(thenewname)
                                    for fl in os.listdir(arcpath):
                                        flfullpath = os.path.join(arcpath, fl)
                                        if (os.path.isfile(flfullpath)) and not('humbs.db' in fl):
                                            if (removedigits(fl) == srcbasename) or (removedigits(fl) == tgtbasename):
                                                print('    delete', flfullpath)
                                                os.remove(flfullpath)
                                                theframecount += 1
                                    logmsg += ('\n    deleted existing ' + str(theframecount) + 'archive frames for publish that no longer exists.')
                                    for fl in os.listdir(thepath):
                                        flfullpath = os.path.join(thepath, fl)
                                        if removedigits(fl) == tgtbasename:
                                            print('    archive', flfullpath)
                                            shutil.copy2(flfullpath, arcpath)
                                            thearccount += 1
                                    totalbaks += 1
                                    logmsg += ('\n    archived ' + str(thearccount) + ' frames for updated publish.')
                            else:
                                #   delete existing and ARCHIVE single
                                print('    existing arcfile FILE does NOT match, need to delete and copy current tgtfile as new archive')
                                os.remove(arcfile)
                                shutil.copy2(tgtfile, arcfile)
                                totalbaks += 1
                                logmsg += ('\n    archived: ' + arcfile)
                    #   archive does not exist
                    else:
                        if srctype == 'SEQUENCE':
                            #   ARCHIVE sequence
                            theframecount = 0
                            thearccount = 0
                            arcpath = os.path.dirname(arcfile)
                            tgtbasename = removedigits(thenewname)
                            for fl in os.listdir(thepath):
                                flfullpath = os.path.join(thepath, fl)
                                if removedigits(fl) == tgtbasename:
                                    print('    archive', flfullpath)
                                    shutil.copy2(flfullpath, arcpath)
                                    thearccount += 1
                            totalbaks += 1
                            logmsg += ('\n    archived ' + str(thearccount) + ' frames for updated publish.')
                        else:
                            #   ARCHIVE single
                            print('    archive existing tgtfile')
                            shutil.copy2(tgtfile, os.path.dirname(arcfile))
                            totalbaks += 1
                            logmsg += ('\n    archived: ' + arcfile)
                    
                    #   check if existing publish matches srcfile
                    if (filecmp.cmp(srcfile, tgtfile, shallow=False)):
                        #   if so, SKIP and REPATH
                        if not(os.path.basename(tgtfile) == os.path.basename(srcfile)):
                            correctname = os.path.join(os.path.dirname(tgtfile), os.path.basename(tgtfile))
                            os.replace(tgtfile, correctname)
                        print('    matching tgtfile, so skipping publish step')
                        img.filepath = tgtfile
                        totalpubskps += 1
                        logmsg += ('\n    repathed to matched existing publish: ' + tgtfile)
                    else:
                        #   if not, PUBLISH new
                        print('    different tgtfile, so need to republish')
                        logmsg += ('\n    existing publish does not match')
                        if srctype == 'SEQUENCE':
                            #   delete old and PUBLISH sequence
                            print('   delete mismatched tgtfile sequence and publish sequence')
                            theframecount = 0
                            thearccount = 0
                            srcpath = os.path.dirname(srcfile)
                            srcbasename = removedigits(theoldname)
                            tgtbasename = removedigits(thenewname)
                            for fl in os.listdir(thepath):
                                flfullpath = os.path.join(thepath, fl)
                                if (os.path.isfile(flfullpath)) and not('humbs.db' in fl):
                                    if (removedigits(fl) == tgtbasename):
                                        print('    delete', flfullpath)
                                        os.remove(flfullpath)
                                        theframecount += 1
                            logmsg += ('\n    deleted existing ' + str(theframecount) + ' published frames for publish that no longer exists.')
                            for fl in os.listdir(srcpath):
                                flfullpath = os.path.join(thepath, fl)
                                if removedigits(fl) == tgtbasename:
                                    print('    archive', flfullpath)
                                    shutil.copy2(flfullpath, thepath)
                                    thearccount += 1
                            logmsg += ('\n    published ' + str(theframecount) + ' new frames.')
                        else:
                            #   delete old and PUBLISH single
                            print('   delete mismatched tgtfile and publish')
                            os.remove(tgtfile)
                            shutil.copy2(srcfile, tgtfile)
                        img.filepath = tgtfile
                        totalpubs += 1
                        logmsg += ('\n    updated existing publish: ' + tgtfile)
                
                #   publish does not already exist
                else:
                    #   ARCHIVE handle
                    if os.path.exists(arcfile):
                        print('    found arcfile for unpublished image')
                        #   check if the arcfile is being used as a srcfile
                        if arcfile in theoldpaths:
                            print('    arcfile is being used as source, so leave arcfile and publish/repath')
                            totalarcskps += 1
                            logmsg += ('\n    skipped archive used as source: ' + arcfile)
                        else:
                            if srctype == 'SEQUENCE':
                                #   delete sequence
                                theframecount = 0
                                arcpath = os.path.dirname(arcfile)
                                srcbasename = removedigits(theoldname)
                                for fl in os.listdir(arcpath):
                                    flfullpath = os.path.join(arcpath, fl)
                                    if (os.path.isfile(flfullpath)) and not('humbs.db' in fl):
                                        if removedigits(fl) == srcbasename:
                                            print('    delete', flfullpath)
                                            os.remove(flfullpath)
                                            theframecount += 1
                                logmsg += ('\n    deleted existing ' + str(theframecount) + 'archive frames for publish that no longer exists.')
                            else:
                                #   delete single
                                os.remove(arcfile)
                                logmsg += ('\n    deleted existing archive of unpublished source: ' + arcfile)
                    else:
                        logmsg += ('\n    no existing archive found for new publish')
                    
					#   PUBLISH new
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
                                    shutil.copy2(flfullpath, thepath)
                                    theframecount += 1
                        img.filepath = tgtfile
                        totalpubs += 1
                        logmsg += ('\n    published new:      ' + str(theframecount) + ' frame sequence: ' + tgtfile)
                    else:
                        #   publish single
                        shutil.copy2(srcfile, tgtfile)
                        img.filepath = tgtfile
                        totalpubs += 1
                        logmsg += ('\n    published new:      ' + tgtfile)
                
                themsg = ('\n' + img.name)
                themsg += (',' + srcfile)
                themsg += (',' + tgtfile)
                therestore.write(themsg)
            
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
            if bpy.context.scene.publishmaps_restore:
                bpy.context.scene.publishmaps_restore = therestorefile
            logmsg += ('\n\nThe restore file for this publish is: ' + str(therestorefile))
            
            #   log totals
            logmsg += ('\n\nTotal images processed: ' + str(totalimgs) + 
                       '\nTotal images unpacked: ' + str(totalpacks) + 
                       '\nTotal images published: ' + str(totalpubs) + 
                       '\nTotal images archived: ' + str(totalbaks) + 
                       '\nTotal publishes skipped: ' + str(totalpubskps) + 
                       '\nTotal archives skipped: ' + str(totalarcskps) + 
                       '\n\nTotal confirmed publishes: ' + str(totalconfirmedpaths))
            print('Done.')
        #   close log files and finish
        thelog.write(logmsg)
        therestore.close()
        thelog.close()
        print('COMPLETE PUBLISH')
        return{'FINISHED'}

#   OPERATOR publishmapsrestore RESTORE
class BUTTON_OT_publishmapsrestore(bpy.types.Operator):
    '''Restore From Log'''
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
        logmsg = ('tangent_publishmaps    version: ' + vsn)
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
        layout.prop(scene, "publishmaps_restore", text="")
        layout.operator("publishmaps.restore", text=(BUTTON_OT_publishmapsrestore.bl_label))
        

####    REGISTRATION    ####

classes = ( BUTTON_OT_publishmapspublish, BUTTON_OT_publishmapsrestore, VIEW3D_PT_publishmaps )

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
        name = "Clean Up Names",
        description = "Replace spaces with underscores and make the image names all lower case",
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
