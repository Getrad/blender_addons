# ----------------------- NOTES -----------------------
# v0.0.1
# first pass of manual UI based turntable setup
# 0.0.4 - fixes output path to go into _prod folder
# 0.0.5 - adds dropdown for choosing latest workfile vs publish
# 0.0.8 - adds camera select button
# 0.0.9 - add button to open asset file; bugfix-list asset fail on missing dir; optopm to force new sessions on file opens
# 0.1.1 - add deadline submit
# 0.1.2 - add quick draft and remove transcode
# 0.1.3 - music for xcode - is all working but disabled as this audio will make us crazy
# 0.1.6 - added/fixed transcode and draft qt post gen options; expanded submit to render capabilities
# 0.1.7 - add 20_model level support
# 0.1.8 - add asset directory query code
#         a: debug assetname variable to work better with ttutils_alist
# 0.1.9 - messagebox for error messages like missing paths
#       - a - bugfix on overzealous blocking filesave
# 0.2.0 - explore asset button
# 0.2.1 - asset preferences
# to do - add asset library path as user preference
# to do - add deadline repo path as user preference
# to do - add refresh button to force update the asset root path when dropped connection

bl_info = {
    "name": "TurnTable Tools",
    "author": "Conrad Dueck, Darren Place",
    "version": (0, 2, 1),
    "blender": (3, 3, 1),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Turntable Convenience Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}


# ---    GLOBAL IMPORTS    ----
from pathlib import Path
from getpass import getuser
from socket import gethostname
import bpy
import os
import re
import math
import shutil
import uuid
import sys
import subprocess

# ---    GLOBAL VARIABLES    ----
chm_assetroot = 'Y:/projects/CHUMS_Onsite/_prod/assets/'
if not(os.path.exists(chm_assetroot)):
    chm_assetroot = 'P:/projects/CHUMS_Onsite/_prod/assets/'
if not(os.path.exists(chm_assetroot)):
    chm_assetroot = 'C:/temp/'
chm_assetprefix = {'chr':'characters', 
                    'env':'environments', 
                    'prp':'props', 
                    'prx':'proxies'}
chm_omitlist = (['chr_AAAtemplate', 'chr_ants', 'chr_barry - Copy', 'chr_squirrel', 
                'env_AAAtemplate', 'env_rompersburrow', 
                'prp_AAAtemplate', 'prp_bush_romperPopout_01', 'prp_tree_hollowknot',
                'prx_AAAtemplate', 'prx_treeObstacle_Source'])
#chm_assettypes = ['characters', 'environments', 'props', 'proxies']
chm_assettypes = ([f for f in os.listdir(chm_assetroot) if 
                  os.path.isdir(os.path.join(chm_assetroot, f))])
chm_renderroot = 'Y:/projects/CHUMS_Onsite/renders/_prod/assets/'
chm_assetssubtree = 'projects/blender'
chm_assetturntables = '30_texture/projects/blender/turntables'
thecam_name = "cam.ttCamera"
turntable_filepath = "Y:/projects/CHUMS_Onsite/_prod/assets/helpers/turntable/projects/blender/turntable.blend"
deadlineBin = r"C:\Program Files\Thinkbox\Deadline10\bin\deadlinecommand.exe"
tunes = "Y:/projects/CHUMS_Onsite/pipeline/software/tools/blender/addons/conrad/audio/LosStraitjacketsSardinianHoliday.mp3"
frameRate = 23.976
vsn = '0.2.1a'

def getPipelineTmpFolder():
    tmp = r'Y:\projects\CHUMS_Onsite\pipeline\tmp'
    return tmp

def getCurrentUser():
    currentUser = getuser()
    return currentUser

def getMachineName():
    hostName = gethostname()
    return hostName

def sendDeadlineCmd():
    print("RUNNING SUBMIT TO DEADLINE")
    tmpDir = Path(getPipelineTmpFolder()).joinpath('dlJobFiles')
    thisfilename = bpy.data.filepath
    thisoutputpath = bpy.context.scene.render.filepath
    asset_name = bpy.context.scene.ttutils_alist
    bpy.context.scene.assetname = bpy.context.scene.ttutils_alist
    asset_stage = bpy.context.scene.ttutils_stage
    asset_task = bpy.context.scene.ttutils_task
    chm_assetprefix = {'chr':'characters', 
                    'env':'environments', 
                    'prp':'props', 
                    'prx':'proxies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    the_outpath_base = os.path.join(chm_renderroot, 
                                asset_type,
                                asset_name,
                                asset_task)
    if os.path.basename(thisfilename) == os.path.basename(turntable_filepath):
        the_workpath = os.path.join(chm_assetroot, 
                                    asset_type,
                                    asset_name, 
                                    asset_task, 
                                    chm_assetssubtree,
                                    asset_stage)
        latest_asset_workfile = find_latest_workfile(the_workpath)
        the_outfilepath = latest_asset_workfile.replace("workfiles", "turntables")
        the_outfilepath = the_outfilepath.replace("publish", "turntables")
        the_outfilepath = the_outfilepath.replace(".blend",("_tt.blend"))
        latest_asset_version = latest_asset_workfile.split(".")[-2][-4:]
        latest_asset_filename = os.path.basename(latest_asset_workfile)
        the_outpath_base = os.path.join(the_outpath_base, latest_asset_version)
        if not(os.path.exists(the_outpath_base)):
            os.makedirs(the_outpath_base)
        outname = latest_asset_filename.replace(".blend",".####.png")
        the_outpath = os.path.join(the_outpath_base, outname)
        dlName = os.path.basename(the_outfilepath)[:-6]
        dlSceneFile = Path(the_outfilepath).as_posix()
        dlOutputFile = Path(the_outpath).as_posix()
    else:
        dlName = os.path.basename(thisfilename)[:-6]
        dlSceneFile = Path(thisfilename).as_posix()
        dlOutputFile = Path(thisoutputpath).as_posix()
        the_outpath_base = os.path.dirname(thisoutputpath)
        outname = os.path.basename(thisoutputpath)
    dlFrames = '0-121'
    filename = uuid.uuid4()
    jobInfoPath = Path(tmpDir).joinpath(f'{filename}_jobInfo.job')
    
    with open(jobInfoPath, 'w') as f:
        f.write(f"Name={dlName} [Blender Render]\n")
        f.write(f"BatchName={dlName}\n")
        f.write(f"Department=Assets\n")
        f.write(f"Priority=50\n")
        f.write(f"ChunkSize=10\n")
        f.write(f"Comment=Turntable\n")
        f.write(f"Frames={dlFrames}\n")
        f.write(f"UserName={getCurrentUser()}\n")
        f.write(f"MachineName={getMachineName()}\n")
        f.write(f"Plugin=Blender\n") # required
        f.write(f"OutputDirectory0={the_outpath_base}\n")
        f.write(f"OutputFilename0={outname}\n")
        if bpy.context.scene.ttutils_draft == True:
            f.write(f"ExtraInfoKeyValue0=SubmitQuickDraft=True\n")
            f.write(f"ExtraInfoKeyValue1=DraftExtension=mov\n")
            f.write(f"ExtraInfoKeyValue2=DraftType=movie\n")
            f.write(f"ExtraInfoKeyValue3=DraftResolution=1\n")
            f.write(f"ExtraInfoKeyValue4=DraftCodec=h264\n")
            f.write(f"ExtraInfoKeyValue5=DraftQuality=85\n")
            f.write(f"ExtraInfoKeyValue6=DraftFrameRate=24\n")
            f.write(f"ExtraInfoKeyValue7=DraftColorSpaceIn=Draft sRGB\n")
            f.write(f"ExtraInfoKeyValue8=DraftColorSpaceOut=Draft sRGB\n")
            f.write(f"ExtraInfoKeyValue9=DraftUploadToShotgun=False\n")

    pluginInfoPath = Path(tmpDir).joinpath(f'{filename}_pluginInfo.job')
    # Open the pluginInfo jobfile for writing
    with open(pluginInfoPath, 'w') as f:
        f.write(f"SceneFile={dlSceneFile}\n")
        f.write(f"OutputFile={dlOutputFile}\n")
        f.write(f"Threads=0\n")
        f.write(f"Build=None\n")

    command = f'{deadlineBin} {jobInfoPath} {pluginInfoPath}'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    sys.stdout.write(stdout.decode())
    if stdout:
        # Decode the byte string into a UTF-8 string
        output = stdout.decode('utf-8')
        match = re.search(r'JobID=([0-9a-z]+)', output)
        global blendJobId
        if match:
            blendJobId = match.group(1)

def xcodeH264():
    print("Info: Submitting H264 Transcode Job...")
    tmpDir = Path(getPipelineTmpFolder()).joinpath('dlJobFiles')
    thisfilename = bpy.data.filepath
    thisoutputpath = bpy.context.scene.render.filepath
    asset_name = bpy.context.scene.ttutils_alist
    asset_stage = bpy.context.scene.ttutils_stage
    asset_task = bpy.context.scene.ttutils_task
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    the_outpath_base = os.path.join(chm_renderroot, 
                                asset_type,
                                asset_name,
                                asset_task)
    if os.path.basename(thisfilename) == os.path.basename(turntable_filepath):
        the_workpath = os.path.join(chm_assetroot, 
                                    asset_type,
                                    asset_name, 
                                    asset_task, 
                                    chm_assetssubtree,
                                    asset_stage)
        latest_asset_workfile = find_latest_workfile(the_workpath)
        the_outfilepath = latest_asset_workfile.replace("workfiles", "turntables")
        the_outfilepath = the_outfilepath.replace("publish", "turntables")
        the_outfilepath = the_outfilepath.replace(".blend",("_tt.blend"))
        latest_asset_version = latest_asset_workfile.split(".")[-2][-4:]
        latest_asset_filename = os.path.basename(latest_asset_workfile)
        the_outpath_base = os.path.join(the_outpath_base, latest_asset_version)
        if not(os.path.exists(the_outpath_base)):
            os.makedirs(the_outpath_base)
        outname = latest_asset_filename.replace(".blend",".####.png")
        outmovname = os.path.basename(the_outfilepath)[:-6]
        the_outpath = os.path.join(the_outpath_base, outname)
        dlName = os.path.basename(the_outfilepath)[:-6]
        dlSceneFile = Path(the_outfilepath).as_posix()
        dlOutputFile = Path(the_outpath).as_posix()
        dlOutputPath = Path(the_outpath_base).as_posix()
    else:
        dlName = os.path.basename(thisfilename)[:-6]
        dlSceneFile = Path(thisfilename).as_posix()
        dlOutputFile = Path(thisoutputpath).as_posix()
        dlOutputPath = Path(os.path.dirname(thisoutputpath)).as_posix()
        outmovname = os.path.basename(thisfilename)[:-6]
    dlFrames = '0-121'
    filename = uuid.uuid4()
    jobInfoPath = Path(tmpDir).joinpath(f'{filename}_jobInfo.job')
    with open(jobInfoPath, 'w') as f:
        f.write(f"Name={dlName} [H.264 Transcode]\n")
        f.write(f"BatchName={dlName}\n")
        f.write(f"ChunkSize=1000000\n")
        f.write(f"JobDependency0={blendJobId}\n")
        f.write(f"Comment=Turntable\n")
        f.write(f"Department=Assets\n")
        f.write(f"Priority=50\n")
        f.write(f"Frames={dlFrames}\n")
        f.write(f"UserName={os.getlogin()}\n")
        f.write(f"MachineName={getMachineName()}\n")
        f.write(f"Plugin=FFmpeg\n")
        f.write(f"OutputDirectory0={dlOutputPath}\n")
        f.write(f"OutputFilename0={outmovname}.mov\n")
        f.write(f"MachineLimit=1\n")
        f.write(f"Allowlist=Darren\n") #FIXME: remove this line when running in prod on the server
        f.write(f"ExtraInfo6={dlSceneFile}\n")

        #if args["createSgVersion"] == True:
        #    f.write(f"PostJobScript={updateSgVersionScript}\n")
        #    f.write(f"ExtraInfo5={args['sgUsername']}\n")
    
    pluginInfoPath = Path(tmpDir).joinpath(f'{filename}_pluginInfo.job')
    # Open the pluginInfo jobfile for writing
    with open(pluginInfoPath, 'w') as f:
        f.write(f"InputFile0={dlOutputFile.replace('####', '%04d')}\n") # the image sequence
        #f.write(f"InputFile1={tunes}\n")    # the audio
        f.write(f"InputArgs0=-r {frameRate}\n") # force the image sequence fps to output framerate
        f.write(f"ReplacePadding0=False\n")
        #f.write(f"ReplacePadding1=False\n")
        #f.write(f"OutputArgs=-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -level 4.1 -r {frameRate} -s 1080x1080 -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -y\n")
        f.write(f"OutputArgs=-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -level 4.1 -r {frameRate} -s 1080x1080 -map 0:v:0 -y\n")
        f.write(f"OutputFile={Path(dlOutputPath).joinpath((outmovname) + '_h264.mov')}\n")
    
    command = f'{deadlineBin} {jobInfoPath} {pluginInfoPath}'
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_selection_bounds(thesel):
    print("\nENTER get_selection_bounds FUNCTION")
    from mathutils import Vector
    themin = [0.0, 0.0, 0.0]
    themax = [0.0, 0.0, 0.0]
    for theobj in thesel:
        thematrix = theobj.matrix_world
        if theobj.type == 'MESH':
            if len(theobj.data.vertices) >= 1:
                for vertex in theobj.data.vertices:
                    theloc = thematrix @ vertex.co
                    if theloc[0] > themax[0]:
                        themax[0] = theloc[0]
                    if theloc[0] < themin[0]:
                        themin[0] = theloc[0]
                    if theloc[1] > themax[1]:
                        themax[1] = theloc[1]
                    if theloc[1] < themin[1]:
                        themin[1] = theloc[1]
                    if theloc[2] > themax[2]:
                        themax[2] = theloc[2]
                    if theloc[2] < themin[2]:
                        themin[2] = theloc[2]
            else:
                for vertex in theobj.bound_box:
                    theloc = thematrix @ Vector((vertex[0], vertex[1], vertex[2]))
                    if theloc[0] > themax[0]:
                        themax[0] = theloc[0]
                    if theloc[0] < themin[0]:
                        themin[0] = theloc[0]
                    if theloc[1] > themax[1]:
                        themax[1] = theloc[1]
                    if theloc[1] < themin[1]:
                        themin[1] = theloc[1]
                    if theloc[2] > themax[2]:
                        themax[2] = theloc[2]
                    if theloc[2] < themin[2]:
                        themin[2] = theloc[2]
    thesize = [(themax[0]-themin[0]), (themax[1]-themin[1]), (themax[2]-themin[2])]
    thecenter = ([themin[0]+(thesize[0]/2), 
                  themin[1]+(thesize[1]/2), 
                  themin[2]+(thesize[2]/2)])
    print("size [0]", str(thesize))
    print("center [1]", str(thecenter))
    
    return thesize, thecenter

def get_local_asset_objects():
    print("\nENTER get_local_asset_objects FUNCTION")
    object_list = []
    for col in bpy.data.collections:
        if col.name == "asset_prod":
            print("FOUND: ", col.name)
            asset_col = col
            for obj in asset_col.all_objects:
                if not(obj in object_list):
                    object_list.append(obj)
                if obj.type == 'EMPTY' and len(obj.children) >= 1:
                    for chobj in obj.children:
                        if not(obj in object_list):
                            object_list.append(obj)
    return object_list

def remove_any_existing_asset():
    # asumee all objects in collection "asset_prod" are to be removed as well as the collection itself
    for col in bpy.data.collections:
        if col.name == "asset_prod":
            for obj in col.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)
    return 0

def find_latest_workfile(input_path):
    print("ENTER find_latest_workfile FUNCTION")
    latest_filepath = ""
    vNo = 0
    if os.path.exists(input_path):
        for f in os.listdir(input_path):
            this_path = os.path.join(input_path, f)
            if this_path.endswith(".blend") and (this_path[-10] == "v"):
                print("this_path: ", this_path)
                if os.path.isfile(this_path):
                    str_version = (f.split(".")[0][-3:])
                    #print("str_version: ", str_version)
                    this_version = int(str_version)
                    if this_version > vNo:
                        vNo = this_version
                        latest_filepath = this_path
    else:
        # return messagebox showing filepath and message that it can't be found
        ttutils_messagebox(("Cannot find Path:    " + input_path), "Missing Path")
        print("CANNOT FIND PATH: ", input_path)
    if len(latest_filepath) < 3:
        ttutils_messagebox(("Cannot find latest version:    " + input_path), "Version Issue")
    return latest_filepath

def get_asset(asset_name, asset_dept, asset_stage):
    print("ENTER get_asset FUNCTION", asset_name)
    remove_any_existing_asset()
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    the_asset_type = chm_assetprefix[asset_name[:3]]
    the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_assetssubtree,asset_stage)
    print("the_asset_dir:", the_asset_dir)
    the_asset_path = find_latest_workfile(the_asset_dir)
    print("the_asset_path:", the_asset_path)
    if os.path.exists(the_asset_path):
        # LINK FROM LATEST WORKFILE
        # initialize
        with bpy.data.libraries.load(the_asset_path, link=False) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        # link collections
        for coll in data_dst.collections:
            the_topnodes = []
            if coll.name == "asset_prod":
                bpy.context.scene.collection.children.link(coll)
            for colobj in coll.all_objects:
                if not(colobj.parent):
                    colobj.parent = bpy.data.objects['AnimGrp.asset']
    else:
        if bpy.context.scene.ttutils_task == '30_texture':
            mytask = "Texture"
        else:
            mytask = "Model"
        # return messagebox showing filepath and message that it can't be found
        ttutils_messagebox(("Cannot find Path:    " + the_asset_dir + "    check if   " + mytask + "   " + bpy.context.scene.ttutils_stage + "   are set correctly."), "Missing Path")
        print("CANNOT FIND PATH: ", the_asset_dir)
    return 0

def open_assetfile(asset_name, asset_dept, asset_stage):
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    the_asset_type = chm_assetprefix[asset_name[:3]]
    #the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,chm_assetssubtree,asset_stage)
    the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_assetssubtree,asset_stage)
    print("the_asset_dir:", the_asset_dir)
    the_asset_path = find_latest_workfile(the_asset_dir)
    if os.path.exists(the_asset_dir):
        if bpy.context.scene.ttutils_newblend:
            mycmd = '\"'
            mycmd += bpy.app.binary_path
            mycmd += ('\" \"' + the_asset_path + '\"')
            os.popen(mycmd)
        else:
            bpy.ops.wm.open_mainfile(filepath=the_asset_path)
    else:
        # return messagebox showing filepath and message that it can't be found
        ttutils_messagebox(("Cannot find Path:    " + the_asset_dir), "Missing Path")
        print("CANNOT FIND PATH: ", the_asset_dir)

    return 0

def explore_asset(asset_name, asset_dept, asset_stage):
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    the_asset_type = chm_assetprefix[asset_name[:3]]
    #the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,chm_assetssubtree,asset_stage)
    the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_assetssubtree,asset_stage).replace("/","\\")
    print("the_asset_dir:", the_asset_dir)
    if os.path.exists(the_asset_dir):
        subprocess.Popen('explorer \"' + the_asset_dir + '\"')
    else:
        # return messagebox showing filepath and message that it can't be found
        ttutils_messagebox(("Cannot find Path:    " + the_asset_dir), "Missing Path")
        print("CANNOT FIND PATH: ", the_asset_dir)

    return 0

def get_asset_list(asset_stage):
    asset_list = []
    for asset_type in chm_assettypes:
        asset_type_path = (os.path.join(chm_assetroot,asset_type))
        assets = [o for o in os.listdir(asset_type_path) if (not(o[-3:] == "zip") and not("_AAA" in o) and not(o == ".DS_Store"))]
        for asset in assets:
            # find the asset blender folder
            this_asset_path = os.path.join(asset_type_path,asset,chm_assetssubtree,asset_stage)
            this_latest_filepath = find_latest_workfile(this_asset_path)
            if len(this_latest_filepath) > 0:
                asset_list.append((asset,asset,""))

    return asset_list

def open_turntable():
    if os.path.exists(turntable_filepath):
        if bpy.context.scene.ttutils_newblend:
            mycmd = '\"'
            mycmd += bpy.app.binary_path
            mycmd += ('\" \"' + turntable_filepath + '\"')
            os.popen(mycmd)
        else:
            bpy.ops.wm.open_mainfile(filepath=turntable_filepath)
    else:
        ttutils_messagebox("Turntable cannot be found here:    " + str(turntable_filepath) + "\nPlease check path manually and notify your supervisor if you can see and open the file directly.", "Turntable Missing")

def set_output_path(asset_name, asset_task, asset_stage):
    #new goal: Y:\projects\CHUMS_Onsite\renders\assets\<asset type>\<asset name>\<v###>
    the_outpath = ""
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    the_outpath_base = os.path.join(chm_renderroot, 
                                asset_type,
                                asset_name,
                                asset_task)
    the_workpath = os.path.join(chm_assetroot, 
                                asset_type,
                                asset_name, 
                                asset_task, 
                                chm_assetssubtree,
                                asset_stage)
    #print("the_outpath_base: ", the_outpath_base)
    #print("the_workpath: ", the_workpath)
    if os.path.exists(the_workpath):
        latest_asset_workfile = find_latest_workfile(the_workpath)
        #print("latest_asset_workfile: ", latest_asset_workfile)
        latest_asset_version = latest_asset_workfile.split(".")[-2][-4:]
        latest_asset_filename = os.path.basename(latest_asset_workfile)
        the_outpath_base = os.path.join(the_outpath_base, latest_asset_version)
        if not(os.path.exists(the_outpath_base)):
            os.makedirs(the_outpath_base)
        outname = latest_asset_filename.replace(".blend",".####.png")
        the_outpath = os.path.join(the_outpath_base, outname)
        print("outpath: ", the_outpath)
    else:
        ttutils_messagebox(("Cannot find Path:    " + str(the_workpath)), "Error Setting Output")
    return the_outpath

def clean_up_after_blender_save(save_path):
    the_garbage_dir = save_path.replace("_tt.blend",("_tt_blend"))
    if os.path.exists(the_garbage_dir) and os.path.isdir(the_garbage_dir):
        shutil.rmtree(the_garbage_dir)
    the_garbage_file_1 = save_path.replace(".blend",(".blend1"))
    if os.path.exists(the_garbage_file_1) and os.path.isfile(the_garbage_file_1):
        os.remove(the_garbage_file_1)
    if os.path.exists(the_garbage_file_1) and os.path.isdir(the_garbage_file_1):
        shutil.rmtree(the_garbage_file_1)
    the_garbage_file_2 = save_path.replace(".blend",(".blend@"))
    if os.path.exists(the_garbage_file_2) and os.path.isfile(the_garbage_file_2):
        os.remove(the_garbage_file_2)
    return 0

def save_tt_file(asset_name, asset_task, asset_stage):
    the_outpath = ""
    asset_name = bpy.context.scene.ttutils_alist
    bpy.context.scene.assetname = bpy.context.scene.ttutils_alist
    asset_stage = bpy.context.scene.ttutils_stage
    asset_task = bpy.context.scene.ttutils_task
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    the_workpath = os.path.join(chm_assetroot, 
                                asset_type,
                                asset_name, 
                                asset_task,
                                chm_assetssubtree,
                                asset_stage)
    latest_asset_workfile = find_latest_workfile(the_workpath)
    the_outpath = latest_asset_workfile.replace("workfiles", "turntables")
    the_outpath = the_outpath.replace("publish", "turntables")
    the_outpath = the_outpath.replace(".blend",("_tt.blend"))
    if not(os.path.exists(the_outpath)):
        os.makedirs(the_outpath)
    clean_up_after_blender_save(the_outpath)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=the_outpath)
        clean_up_after_blender_save(the_outpath)
    except:
        ttutils_messagebox("Error encountered.\nIf it appears the file saved successfully, \nyou may wish to check that file before closing this one,\nto ensure it actually did save correctly.\nIf not please reach out for support to flag the issue.", "File Save Issue")
    return the_outpath

def ttutils_messagebox(message, title):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon='ERROR')

def queryAssetList():
        print("\nENTER queryAssetList FUNCTION")
        chm_assetroot = 'Y:/projects/CHUMS_Onsite/_prod/assets/'
        if not(os.path.exists(chm_assetroot)):
            chm_assetroot = 'P:/projects/CHUMS_Onsite/_prod/assets/'
        if not(os.path.exists(chm_assetroot)):
            chm_assetroot = 'C:/temp/'
        bpy.context.scene.assetroot = chm_assetroot
        anames = []
        for atype in chm_assettypes:
            thistype = os.path.join(chm_assetroot, atype)
            anames += ([(aname,aname,'') for aname in os.listdir(thistype) if 
                    (aname[:3] in chm_assetprefix.keys() and 
                    not(aname in chm_omitlist))])
        return anames

# PREFERENCES ttutilsPreferences
class ttutilsPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = "TurnTable Tools"

    filepath: bpy.props.StringProperty(
        name="Example File Path",
        subtype='FILE_PATH',
    )
    number: bpy.props.IntProperty(
        name="Example Number",
        default=4,
    )
    boolean: bpy.props.BoolProperty(
        name="Example Boolean",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our add-on")
        layout.prop(self, "filepath")
        layout.prop(self, "number")
        layout.prop(self, "boolean")

class OBJECT_OT_ttutils_preferences(bpy.types.Operator):
    bl_idname = "object.ttutils_preferences"
    bl_label = "Turntable Add-on Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons["Turntable Tools"].preferences

        info = ("Path: %s, Number: %d, Boolean %r" %
                (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}


# PROPERTY GROUP ttutilsProperties
class ttutilsProperties(bpy.types.PropertyGroup):
    bpy.types.Scene.assetname = bpy.props.StringProperty \
        (
          name = "Asset Name",
          description = "Asset Name",
          default = ""
        )
    bpy.types.Scene.assetroot = bpy.props.StringProperty \
        (
          name = "Asset Root",
          description = "Asset Root",
          default = 'Y:/projects/CHUMS_Onsite/_prod/assets/'
        )
    bpy.types.Scene.ttutils_task = bpy.props.EnumProperty(
        name="",
        description="Use latest model or texture version.",
        items=[ ('20_model', "Model", ""),
                ('30_texture', "Texture", "")
               ],
        default = "30_texture"
        )
    bpy.types.Scene.ttutils_stage = bpy.props.EnumProperty(
        name="",
        description="Use latest publish or workfiles version.",
        items=[ ('publish', "Publish", ""),
                ('workfiles', "Workfiles", "")
               ],
        default = "workfiles"
        )
    bpy.types.Scene.ttutils_custom = bpy.props.StringProperty(
        name="Custom:",
        description="",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
    bpy.types.Scene.ttutils_overscan = bpy.props.FloatProperty \
        (
          name = "Overscan %",
          description = "Percent of asset size to use as border",
          min = 0.00,
          max = 10000.0,
          step = 0.5,
          default = 20.0
        )
    bpy.types.Scene.ttutils_newblend = bpy.props.BoolProperty \
        (
          name = "Force New Blender",
          description = "When opening assets or the turntable file with this enabled will launch a new Bledner session.",
          default = True
        )
    bpy.types.Scene.ttutils_xcode = bpy.props.BoolProperty \
        (
          name = "Transcode",
          description = "Transcode H264.",
          default = True
        )
    bpy.types.Scene.ttutils_draft = bpy.props.BoolProperty \
        (
          name = "Draft",
          description = "Deadline Draft.",
          default = False
        )
    bpy.types.Scene.ttutils_alist = bpy.props.EnumProperty(
        name="",
        description="Asset List",
        items=queryAssetList(),
        default = None
        )
    
# OPERATOR BUTTON_OT_openTT
class BUTTON_OT_openTT(bpy.types.Operator):
    '''Open Turntable Basefile.'''
    bl_idname = "ttutils.opentt"
    bl_label = "Open Turntable"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        open_turntable()
        return{'FINISHED'}

class BUTTON_OT_openAsset(bpy.types.Operator):
    '''Open Latest Asset File'''
    bl_idname = "ttutils.openasset"
    bl_label = "Open Asset File"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        open_assetfile(bpy.context.scene.ttutils_alist, bpy.context.scene.ttutils_task,bpy.context.scene.ttutils_stage)
        return{'FINISHED'}

# OPERATOR BUTTON_OT_exploreAsset
class BUTTON_OT_exploreAsset(bpy.types.Operator):
    '''Open Asset Folder'''
    bl_idname = "ttutils.exploreasset"
    bl_label = "Explore Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        explore_asset(bpy.context.scene.ttutils_alist, bpy.context.scene.ttutils_task,bpy.context.scene.ttutils_stage)
        return{'FINISHED'}

# OPERATOR BUTTON_OT_selectTTcam
class BUTTON_OT_selectTTcam(bpy.types.Operator):
    '''Select turntable camera object.'''
    bl_idname = "ttutils.selectttcam"
    bl_label = "Select Camera Object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if thecam_name in bpy.data.objects:
            try:
                for o in bpy.context.selected_objects:
                    o.select_set(False)
                thecam = bpy.data.objects[thecam_name]
                thecam.select_set(True)
                bpy.context.view_layer.objects.active = thecam
            except:
                print("FAILED TO FIND " + str(thecam_name))
        else:
            ttutils_messagebox("Camera " + str(thecam_name) + "appears to be missing.\nPlease ensure you're in a turntable file that contains this object.", "Missing Object")
        return{'FINISHED'}

# OPERATOR BUTTON_OT_set_out_filepath
class BUTTON_OT_set_out_filepath(bpy.types.Operator):
    '''Set Output path.'''
    bl_idname = "ttutils.set_out_filepath"
    bl_label = "Set Output"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        theoutpath = set_output_path(bpy.context.scene.ttutils_alist, bpy.context.scene.ttutils_task, bpy.context.scene.ttutils_stage)
        print("theoutpath: ", theoutpath)
        bpy.context.scene.render.filepath = theoutpath
        return{'FINISHED'}

# OPERATOR BUTTON_OT_set_cam_loc
class BUTTON_OT_set_cam_loc(bpy.types.Operator):
    '''Set Camera distance from asset.'''
    bl_idname = "ttutils.set_cam_loc"
    bl_label = "Set Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE set_cam_loc OPERATOR")
        if thecam_name in bpy.data.objects:
            thecam = bpy.data.objects[thecam_name]
            theasset_objects = get_local_asset_objects()
            theasset_size = (get_selection_bounds(theasset_objects))
            theasset_max = 0
            for theasset_dim in theasset_size[0]:
                if theasset_dim >= theasset_max:
                    theasset_max = theasset_dim
            thecam.location.z = (((theasset_max/2.0)*(1.0+((2*bpy.context.scene.ttutils_overscan)/100.0)))/math.tan((bpy.context.scene.camera.data.angle)/2))
            if bpy.data.objects['Ruler']:
                bpy.data.objects['Ruler'].location.y = ((theasset_size[0][1]/2)*(-1.0 - (bpy.context.scene.ttutils_overscan/100.0)))
            thecam.parent.location.z = (theasset_size[1][2])
        else:
            ttutils_messagebox("Camera    " + str(thecam_name) + "    appears to be missing.\nPlease ensure you're in a turntable file that contains this object.", "Missing Object")
        return{'FINISHED'}

# OPERATOR BUTTON_OT_get_asset
class BUTTON_OT_get_asset(bpy.types.Operator):
    '''Append the asset_prod collection from the latest asset'''
    bl_idname = "ttutils.get_asset"
    bl_label = "Get Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE BUTTON_OT_get_asset OPERATOR CLASS")
        bpy.context.scene.assetname = bpy.context.scene.ttutils_alist
        get_asset(bpy.context.scene.ttutils_alist, bpy.context.scene.ttutils_task, bpy.context.scene.ttutils_stage)
        return{'FINISHED'}

# OPERATOR BUTTON_OT_get_asset_list - currently not used
class BUTTON_OT_get_asset_list(bpy.types.Operator):
    '''Return the latest asset - see console'''
    bl_idname = "ttutils.get_asset_list"
    bl_label = "Get Asset List"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE BUTTON_OT_get_asset_list OPERATOR CLASS")
        the_asset_list = get_asset_list(bpy.context.scene.ttutils_stage)
        print("the_asset_list: ")
        for i in the_asset_list:
            print( i[0])
        return{'FINISHED'}

# OPERATOR BUTTON_OT_tilt_cam
class BUTTON_OT_tilt_cam(bpy.types.Operator):
    '''Select the camera tilt control'''
    bl_idname = "ttutils.tilt_cam"
    bl_label = "Select Camera Control"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE BUTTON_OT_tilt_cam OPERATOR CLASS")
        if "AnimGrp.camera" in bpy.data.objects:
            for o in bpy.context.selected_objects:
                o.select_set(False)
            bpy.data.objects["AnimGrp.camera"].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects["AnimGrp.camera"]
        else:
            ttutils_messagebox("Camera control object    AnimGrp.camera    appears to be missing.\nPlease ensure you're in a turntable file that contains this object.", "Missing Object")
        return{'FINISHED'}

# OPERATOR BUTTON_OT_save_ttfile
class BUTTON_OT_save_ttfile(bpy.types.Operator):
    '''Return the latest asset - see console'''
    bl_idname = "ttutils.save_ttfile"
    bl_label = "Save Turntable File"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE BUTTON_OT_save_ttfile OPERATOR CLASS")
        thisfilepath = bpy.data.filepath
        print("thisfilepath: ", thisfilepath)
        thisfilename = os.path.basename(thisfilepath)
        print("thisfilename: ", thisfilename)
        if (thisfilename == 'turntable.blend') or (bpy.context.scene.ttutils_alist in thisfilename and thisfilename[-8:] == "tt.blend"):
            save_tt_file(bpy.context.scene.ttutils_alist, bpy.context.scene.ttutils_task, bpy.context.scene.ttutils_stage)
        else:
            ttutils_messagebox("To save a turntable file, the starting file must be one of:   the turntable.blend   OR   a previous turntable filename starting with   " + str(bpy.context.scene.ttutils_alist) + "   and ending with   tt.blend.    Please ensure you're starting with one of those files.", "Failed Save")
        
        return{'FINISHED'}

# OPERATOR BUTTON_OT_submit_tt
class BUTTON_OT_submit_tt(bpy.types.Operator):
    '''Submit Turntable to Deadline'''
    bl_idname = "ttutils.submit_tt"
    bl_label = "Submit Turntable Render"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thisfilepath = bpy.data.filepath
        thisfilename = os.path.basename(thisfilepath)
        thisoutputpath = bpy.context.scene.render.filepath
        asset_name = bpy.context.scene.ttutils_alist
        bpy.context.scene.assetname = bpy.context.scene.ttutils_alist
        theoutpath = set_output_path(asset_name, bpy.context.scene.ttutils_task, bpy.context.scene.ttutils_stage)
        if (bpy.context.scene.ttutils_alist in thisfilename and 
            bpy.context.scene.ttutils_alist in thisoutputpath and
            thisfilename[-8:] == "tt.blend"):
            sendDeadlineCmd()
            if bpy.context.scene.ttutils_xcode == True:
                xcodeH264()
        else:
            ttutils_messagebox("To submit a turntable render, this file name must start with the asset selected above    " + str(bpy.context.scene.ttutils_alist) + "    in the filename and the filename must end with    tt.blend", "Failed Submit")
        
        return{'FINISHED'}

# PANEL VIEW3D_PT_ttutils_panel
class VIEW3D_PT_ttutils_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Turntable Utils "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(bpy.context.scene, "ttutils_newblend")
        layout.operator("ttutils.opentt", text=(BUTTON_OT_openTT.bl_label))
        layout.prop(bpy.context.scene, "ttutils_task")
        layout.prop(bpy.context.scene, "ttutils_stage")
        layout.prop(bpy.context.scene, "ttutils_alist")
        layout.operator("ttutils.exploreasset", text=(BUTTON_OT_exploreAsset.bl_label))
        layout.operator("ttutils.openasset", text=(BUTTON_OT_openAsset.bl_label))
        layout.operator("ttutils.get_asset", text=(BUTTON_OT_get_asset.bl_label))
        layout.prop(bpy.context.scene, "ttutils_overscan")
        layout.operator("ttutils.set_cam_loc", text=(BUTTON_OT_set_cam_loc.bl_label))
        layout.operator("ttutils.tilt_cam", text=(BUTTON_OT_tilt_cam.bl_label))
        layout.operator("ttutils.selectttcam", text=(BUTTON_OT_selectTTcam.bl_label))
        layout.operator("ttutils.set_out_filepath", text=(BUTTON_OT_set_out_filepath.bl_label))
        layout.operator("ttutils.save_ttfile", text=(BUTTON_OT_save_ttfile.bl_label))
        layout.operator("ttutils.submit_tt", text=(BUTTON_OT_submit_tt.bl_label))
        split = layout.split(factor=0.5, align=True)
        col = split.column(align=True)
        col.prop(bpy.context.scene, "ttutils_xcode")
        col = split.column(align=True)
        col.prop(bpy.context.scene, "ttutils_draft")

#   REGISTER
classes = [ ttutilsProperties, VIEW3D_PT_ttutils_panel, 
            BUTTON_OT_set_cam_loc, BUTTON_OT_get_asset, 
            BUTTON_OT_openTT, BUTTON_OT_exploreAsset,
            BUTTON_OT_set_out_filepath, BUTTON_OT_save_ttfile,
            BUTTON_OT_tilt_cam, BUTTON_OT_selectTTcam,
            BUTTON_OT_openAsset, BUTTON_OT_submit_tt,
            ttutilsPreferences, OBJECT_OT_ttutils_preferences]

def register():
    from bpy.utils import register_class
    for cls in classes:
        print(cls)
        register_class(cls)
    

#   UNREGISTER
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
  

if __name__ == "__main__":
    register()
    
