# ----------------------- NOTES -----------------------
# 0.5.3

import bpy
from pathlib import Path
from getpass import getuser
from socket import gethostname
import os
import re
import math
import shutil
import uuid
import sys
import subprocess
import builtins


# --------   VARIABLES   --------
#   GET BLENDER MAIN VERSION
blender_version = bpy.app.version
#   SET DEFAULT VERSION STRING
blender_version_str = (str(blender_version[0]) + ".x")
# DEFINE ASSET TYPE PREFIXES
chm_assetprefix = {'chr':'characters', 
                    'env':'environments', 
                    'prp':'props', 
                    'prx':'proxies',
                    'sky':'skies'}
# DEFINE ASSET DEPARTMENT LIST
chm_assetdepts = [('20_model','model',''),('30_texture','texture','')]
# OMIT THESE ASSET NAMES
chm_omitlist = (['archive', 'chr_AAAtemplate', 'chr_ants', 'chr_barry - Copy', 'chr_squirrel', 
                'env_AAAtemplate', 'env_rompersburrow', 
                'prp_AAAtemplate', 'prp_bush_romperPopout_01', 'prp_tree_hollowknot',
                'prx_AAAtemplate', 'prx_treeObstacle_Source'])
# DEADLINE COMMAND
deadlineBin = r"C:\Program Files\Thinkbox\Deadline10\bin\deadlinecommand.exe"
# LAUNCHPAD
LAUNCHPAD_REPOSITORY_PATH = "X:/projects/chums_season3/onsite/pipeline/repos/launchpadRepository"
LAUNCHPAD_BLENDER_PATH = "C:/pipeline/chums_season2/launchpad/software/blender-4.1.0/blender_launcher.exe"
# OUTPUT PARAMETERS
frameRate = 23.976
frameRange = "1-123"


# --------   FUNCTIONS   --------
#def print(*args, **kwargs):
#    kwargs['flush'] = True
#    builtins.print(*args, **kwargs)

def update_base_settings(): #(chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version)
    print("update_base_settings")
    try:
        override_version = (str(bpy.context.scene.tt_override_version))
        print("override_version:", override_version)
        print("using PREFERENCES")
    except:
        override_version = (str(blender_version[0]) + ".x")
        print("override_version:", override_version)
        print("using DEFAULTS")
    
    try:
        pref_useLP = (str(bpy.context.scene.tt_override_LP))
        print("override_version:", pref_useLP)
        #def print(*args, **kwargs):
        #    kwargs['flush'] = True
        #    builtins.print(*args, **kwargs)
        print("using PREFERENCES")
    except:
        pref_useLP = False
        print("pref_useLP:", pref_useLP)

    if override_version == "Custom":
        if len(bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_assetroot) > 0:
            pref_assetroot = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_assetroot
            bpy.context.scene.tt_override_assetroot = pref_assetroot
        else:
            pref_assetroot = ""
            bpy.context.scene.tt_override_assetroot = pref_assetroot
        print("    pref_assetroot:", pref_assetroot)
                    
        if len(bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_basefile) > 0:
            pref_basefile = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_basefile
            bpy.context.scene.tt_override_basefile = pref_basefile
        else:
            pref_basefile = 'Path to basefile'
            bpy.context.scene.tt_override_basefile = pref_basefile
        print("    pref_basefile:", pref_basefile)
        
        if len(bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_filepath) > 0:
            pref_tt_filepath = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_filepath
            bpy.context.scene.tt_override_filepath = pref_tt_filepath
        else:
            pref_tt_filepath = ""
            bpy.context.scene.tt_override_filepath = pref_tt_filepath
        print("    pref_tt_filepath:", pref_tt_filepath)
        
        if len(bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_renderroot) > 0:
            pref_renderroot = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_renderroot
            bpy.context.scene.tt_override_renderroot = pref_renderroot
        else:
            pref_renderroot = ""
            bpy.context.scene.tt_override_filepath = pref_renderroot
        print("    pref_renderroot:", pref_renderroot)
        
        if len(bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_subtree) > 0:
            pref_assetssubtree = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_subtree
            bpy.context.scene.tt_override_subtree = pref_assetssubtree
        else:
            pref_assetssubtree = ""
            bpy.context.scene.tt_override_subtree = pref_assetssubtree
        print("    pref_assetssubtree:", pref_assetssubtree)
        
        if len(bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_stage) > 0:
            pref_tt_stage = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_stage
            bpy.context.scene.tt_override_stage = pref_tt_stage
        else:
            pref_tt_stage = ""
            bpy.context.scene.tt_override_stage = pref_tt_stage
        print("    pref_tt_stage:", pref_tt_stage)

        #v4_blenderpath = "C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"
        v4_blenderpath = LAUNCHPAD_BLENDER_PATH
        if os.path.exists(v4_blenderpath):
            print("os.path.exists is True, so blenderpath is: ", v4_blenderpath)
            pref_blenderpath = v4_blenderpath
        else:
            print("os.path.exists is False, so blenderpath is: ", bpy.app.binary_path)
            pref_blenderpath = bpy.app.binary_path
    else:
        match override_version:
            case '3.3.x':
                pref_blenderpath = "C:/Program Files/Blender Foundation/Blender 3.3/blender.exe"
                pref_assetroot = "Y:/projects/CHUMS_Onsite/_prod/assets/"
                pref_tt_filepath = Path(str(pref_assetroot + "helpers/turntable/projects/blender/turntable.blend"))
                pref_basefile = 'Y:/projects/CHUMS_Onsite/_prod/shots/chm_ep000/'
                pref_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
                pref_assetssubtree = "projects/blender"
                pref_tt_stage = 'workfiles'
            case '4.1.x':
                pref_blenderpath = "C:/pipeline/chums_season2/launchpad/software/blender-4.1.0/blender.exe"
                pref_assetroot = "X:/projects/chums_season2/onsite/_prod/assets"
                pref_tt_filepath = Path(str(pref_assetroot + "/helpers/turntable/publish/blender/turntable.blend"))
                pref_basefile = 'X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish'
                pref_renderroot = "X:/projects/chums_season2/onsite/renders/_prod/assets"
                pref_assetssubtree = "blender"
                pref_tt_stage = "work"
            case '4.2.x':
                pref_blenderpath = "C:/pipeline/chums_season3/launchpad/software/blender-4.2.3/blender.exe"
                pref_assetroot = "X:/projects/chums_season3/onsite/_prod/assets"
                pref_tt_filepath = Path(str(pref_assetroot + "/helpers/turntable/publish/blender/turntable.blend"))
                pref_basefile = 'X:/projects/chums_season3/onsite/_prod/assets/helpers/basefiles/publish'
                pref_renderroot = "X:/projects/chums_season3/onsite/renders/_prod/assets"
                pref_assetssubtree = "blender"
                pref_tt_stage = "work"
            case _:
                pref_blenderpath = "C:/pipeline/chums_season2/launchpad/software/blender-4.1.0/blender.exe"
                pref_assetroot = "X:/projects/chums_season2/onsite/_prod/assets"
                pref_tt_filepath = Path(str(pref_assetroot + "/helpers/turntable/publish/blender/turntable.blend"))
                pref_basefile = 'X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish'
                pref_renderroot = "X:/projects/chums_season2/onsite/renders/_prod/assets"
                pref_assetssubtree = "blender"
                pref_tt_stage = "work"
    pref_override_version = override_version
    
    return(pref_useLP, pref_blenderpath, pref_assetroot, pref_basefile, pref_tt_filepath, pref_renderroot, pref_assetssubtree, pref_tt_stage, pref_override_version)

def get_asset_from_path(path):
    asset_name = ""
    asset_name = path.split("\\")[-1]
    return asset_name

def getPipelineTmpFolder():
    tmp = r'X:\projects\chums_season2\onsite\pipeline\tmp'
    return tmp

def getCurrentUser():
    currentUser = getuser()
    return currentUser

def getMachineName():
    hostName = gethostname()
    return hostName

def sendDeadlineCmd():
    #print("RUNNING SUBMIT TO DEADLINE")
    #410 X:\projects\chums_season2\onsite\renders\_prod\assets\props\prp_cdtest_01\30_texture\work\v001
    #    <chm_renderroot> <asset_type> <asset_name> <asset_task> <asset_stage> <asset_version>
    #331 Y:\projects\CHUMS_Onsite\renders\_prod\assets\characters\chr_emiree\v013
    #    <chm_renderroot> <asset_type> <asset_name> <asset_version>
    tmpDir = Path(getPipelineTmpFolder()).joinpath('dlJobFiles')
    thisfilename = bpy.data.filepath
    thisoutputpath = bpy.context.scene.render.filepath
    asset_name = bpy.context.scene.tt_tools_assetname
    asset_task = bpy.context.scene.tt_tools_task
    chm_assetprefix = {'chr':'characters', 
                        'env':'environments', 
                        'prp':'props', 
                        'prx':'proxies',
                        'sky':'skies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    print("\nCall update_base_settings from: sendDeadlineCmd")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    if chm_tt_version in ["4.1.x","4.2.x"]:
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_tt_stage,chm_assetssubtree).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,asset_type,asset_name,asset_task,chm_tt_stage).replace("/","\\")
        the_comment = [chm_tt_version + " Turntable"]
    elif chm_tt_version == "Custom":
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_assetssubtree,chm_tt_stage).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,asset_type,asset_name).replace("/","\\")
        the_comment = "Custom Turntable"
    else:
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_assetssubtree,chm_tt_stage).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,asset_type,asset_name).replace("/","\\")
        the_comment = "3.x Turntable"
    if "workfiles" in the_outpath_base:
        the_outpath_base = the_outpath_base.replace("workfiles", "turntables")
        the_outpath_base = the_outpath_base.replace("publish", "turntables")
    else:
        the_outpath_base = the_outpath_base.replace("work", "work\\turntables")
        the_outpath_base = the_outpath_base.replace("publish", "publish\\turntables")
    print("the_workpath: ", the_workpath)
    latest_asset_workfile = find_latest_workfile(the_workpath)
    print("latest_asset_workfile: ", latest_asset_workfile)
    latest_asset_version = latest_asset_workfile.split(".")[-2][-4:]
    latest_asset_filename = os.path.basename(latest_asset_workfile)
    the_outpath_base = os.path.join(the_outpath_base, latest_asset_version)
    if not(os.path.exists(the_outpath_base)):
        os.makedirs(the_outpath_base)
    outname = latest_asset_filename.replace(".blend",".####.exr")
    thisoutputpath = os.path.join(the_outpath_base, outname)
    dlName = os.path.basename(thisfilename)[:-6]
    dlSceneFile = Path(thisfilename).as_posix()
    dlOutputFile = Path(thisoutputpath).as_posix()
    #frameRamge
    dlFrames = "1-123"
    if bpy.context.scene.tt_override_range == True:
        dlFrames = (str(bpy.context.scene.frame_start) +"-" + str(bpy.context.scene.frame_end))
    filename = uuid.uuid4()
    jobInfoPath = Path(tmpDir).joinpath(f'{filename}_jobInfo.job')
    jobPrio = str(bpy.context.preferences.addons["chums_tt_addon"].preferences.defaultpriority)

    with open(jobInfoPath, 'w') as f:
        f.write(f"Name={dlName} [Blender Render]\n")
        f.write(f"BatchName={dlName}\n")
        f.write(f"Department=Assets\n")
        f.write(f"Priority={jobPrio}\n")
        f.write(f"ChunkSize=10\n")
        f.write(f"Comment={the_comment}\n")
        f.write(f"Frames={dlFrames}\n")
        f.write(f"UserName={getCurrentUser()}\n")
        f.write(f"MachineName={getMachineName()}\n")
        f.write(f"Plugin=Blender\n") # required
        f.write(f"OutputDirectory0={the_outpath_base}\n")
        f.write(f"OutputFilename0={outname}\n")
        f.write(f"Pool=turntable\n")
        f.write(f"Group=blender\n")
        f.write(f"SecondaryPool=primary\n")
        if bpy.context.scene.tt_tools_draft == True:
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
        output = stdout.decode('utf-8')
        match = re.search(r'JobID=([0-9a-z]+)', output)
        global blendJobId
        if match:
            blendJobId = match.group(1)

def xcodeH264():
    #print("Info: Submitting H264 Transcode Job...")
    tmpDir = Path(getPipelineTmpFolder()).joinpath('dlJobFiles')
    thisfilename = bpy.data.filepath
    thisoutputpath = bpy.context.scene.render.filepath
    #asset_name = bpy.context.scene.tt_tools_alist
    asset_name = bpy.context.scene.tt_tools_assetname
    asset_task = bpy.context.scene.tt_tools_task
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    print("\nCall update_base_setting() from: xcodeH264")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    if chm_tt_version in ["4.1.x","4.2.x"]:
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_tt_stage,chm_assetssubtree).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,asset_type,asset_name,asset_task,chm_tt_stage).replace("/","\\")
        the_comment = [chm_tt_version + " Turntable"]
    elif chm_tt_version == "Custom":
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_assetssubtree,chm_tt_stage).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,asset_type,asset_name).replace("/","\\")
        the_comment = "Custom Turntable"
    else:
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_assetssubtree,chm_tt_stage).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,asset_type,asset_name).replace("/","\\")
        the_comment = "3.x Turntable"
    if "workfiles" in the_outpath_base:
        the_outpath_base = the_outpath_base.replace("workfiles", "turntables")
        the_outpath_base = the_outpath_base.replace("publish", "turntables")
    else:
        the_outpath_base = the_outpath_base.replace("work", "work\\turntables")
        the_outpath_base = the_outpath_base.replace("publish", "publish\\turntables")
    latest_asset_workfile = find_latest_workfile(the_workpath)
    latest_asset_version = latest_asset_workfile.split(".")[-2][-4:]
    latest_asset_filename = os.path.basename(latest_asset_workfile)
    the_outpath_base = os.path.join(the_outpath_base, latest_asset_version)
    if not(os.path.exists(the_outpath_base)):
        os.makedirs(the_outpath_base)
    outname = latest_asset_filename.replace(".blend",".####.exr")
    outmovname = os.path.basename(latest_asset_filename)[:-6]
    the_outpath = os.path.join(the_outpath_base, outname)
    dlName = os.path.basename(thisfilename)[:-6]
    dlSceneFile = Path(thisfilename).as_posix()
    dlOutputFile = Path(the_outpath).as_posix()
    dlOutputPath = Path(the_outpath_base).as_posix()
    #frameRamge
    dlFrames = "1-123"
    if bpy.context.scene.tt_override_range == True:
        dlFrames = (str(bpy.context.scene.frame_start) +"-" + str(bpy.context.scene.frame_end))
    filename = uuid.uuid4()
    jobInfoPath = Path(tmpDir).joinpath(f'{filename}_jobInfo.job')
    jobPrio = str(bpy.context.preferences.addons["chums_tt_addon"].preferences.defaultpriority)

    with open(jobInfoPath, 'w') as f:
        f.write(f"Name={dlName} [H.264 Transcode]\n")
        f.write(f"BatchName={dlName}\n")
        f.write(f"ChunkSize=1000000\n")
        f.write(f"JobDependency0={blendJobId}\n")
        f.write(f"Comment={the_comment}\n")
        f.write(f"Department=Assets\n")
        f.write(f"Priority={jobPrio}\n")
        f.write(f"Frames={dlFrames}\n")
        f.write(f"UserName={os.getlogin()}\n")
        f.write(f"MachineName={getMachineName()}\n")
        f.write(f"Plugin=FFmpeg\n")
        f.write(f"OutputDirectory0={dlOutputPath}\n")
        f.write(f"OutputFilename0={outmovname}.mov\n")
        f.write(f"MachineLimit=1\n")
        f.write(f"Group=xcode\n")
        f.write(f"Pool=turntable\n")
        f.write(f"SecondaryPool=primary\n")
        f.write(f"ExtraInfo6={dlSceneFile}\n")

    pluginInfoPath = Path(tmpDir).joinpath(f'{filename}_pluginInfo.job')
    print("pluginInfoPath: ", pluginInfoPath)
    with open(pluginInfoPath, 'w') as f:
        f.write(f"InputFile0={dlOutputFile.replace('####', '%04d')}\n") # the image sequence
        f.write(f"InputArgs0=-r {frameRate}\n") # force the image sequence fps to output framerate
        f.write(f"ReplacePadding0=False\n")
        f.write(f"OutputArgs=-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -level 4.1 -r {frameRate} -s 1080x1080 -map 0:v:0 -y\n")
        f.write(f"OutputFile={Path(dlOutputPath).joinpath((outmovname) + '_h264.mov')}\n")
    
    command = f'{deadlineBin} {jobInfoPath} {pluginInfoPath}'
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def set_model_material():
    if bpy.data.materials['Modeling_MTL']:
        mdl_mtl = bpy.data.materials['Modeling_MTL']
        if bpy.data.collections['asset_prod']:
            for o in bpy.data.collections['asset_prod'].objects:
                if o.data.materials:
                    for mslt in o.material_slots:
                        mslt.material = mdl_mtl
                else:
                    o.data.materials.append(mdl_mtl)
    
    return 0

def get_selection_bounds(thesel):
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
                        if themin[2] < 0:
                            themin[2] = 0.0
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
    
    return thesize, thecenter

def get_local_asset_objects():
    object_list = []
    for col in bpy.data.collections:
        if col.name[-10:] == "asset_prod":
            #print("FOUND: ", col.name)
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
    latest_filepath = ""
    vNo = 0
    if os.path.exists(input_path):
        for f in os.listdir(input_path):
            this_path = os.path.join(input_path, f)
            if this_path.endswith(".blend") and (this_path[-10] == "v"):
                if os.path.isfile(this_path):
                    str_version = (f.split(".")[0][-3:])
                    this_version = int(str_version)
                    if this_version > vNo:
                        vNo = this_version
                        latest_filepath = this_path
    else:
        tt_tools_messagebox(("Cannot find Path:    " + input_path), "Missing Path")
    if len(latest_filepath) < 3:
        tt_tools_messagebox(("Cannot find latest version:    " + input_path), "Version Issue")
    
    print("fn find_latest_workfile : ", latest_filepath)
    return latest_filepath

def get_assetroot():
    try:
        tt_override_assetroot = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_assetroot
    except:
        tt_override_assetroot = chm_assetroot
    print("fn get_assetroot returns ", tt_override_assetroot)
    return tt_override_assetroot

def build_turntable():
    print("Call update_base_setting() from: build_turntable")
    if len(bpy.context.scene.tt_tools_assetname) < 1 or ((len(bpy.context.scene.tt_tools_alist) > 1) and (bpy.context.scene.tt_tools_assetname != bpy.context.scene.tt_tools_alist)):
        bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
    this_file_path = os.path.dirname(os.path.realpath(__file__))
    chm_postload = os.path.join(this_file_path, 'chums_tt_build.py')
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    chm_basefile = find_latest_workfile(chm_tt_basedir)
    print("chm_basefile: ", chm_basefile)
    chm_asset = bpy.context.scene.tt_tools_assetname
    chm_task = bpy.context.scene.tt_tools_task
    chm_load = bpy.context.scene.tt_tools_autoload
    chm_render = bpy.context.scene.tt_tools_autorender
    chm_range = "1-123"
    if bpy.context.scene.tt_override_range == True:
        chm_range = (str(bpy.context.scene.frame_start) +"-" + str(bpy.context.scene.frame_end))
    chm_version = bpy.context.scene.tt_override_version
    # construct the cmd line
    mycmd = '\"'
    # path to blender exe
    if os.path.exists(chm_blenderpath):
        print("opening asset in Blender from DEFINED path")
        mycmd += chm_blenderpath
    else:
        print("opening asset in Blender from CURRENT SESSION path")
        mycmd += bpy.app.binary_path
    # path to base empty file to open
    mycmd += ('\" \"' + chm_basefile.__str__() + "\"")
    # path to script that builds turntable
    mycmd += (' -P \"' + chm_postload.__str__() + ("\""))
    # path to the master turntable file from which to append collections
    mycmd += (' -- \"' + chm_tt_filepath.__str__() + '\"')
    # asset name
    mycmd += (' \"' + chm_asset.__str__() + '\"')
    # task folder name
    mycmd += (' \"' + chm_task.__str__() + '\"')
    # boolean string  if asset should be loaded automatically
    mycmd += (' \"' + chm_load.__str__() + '\"')
    # boolean string if loaded turntable should be rendered
    mycmd += (' \"' + chm_render.__str__() + '\"')
    # frame range to render
    mycmd += (' \"' + chm_range.__str__() + '\"')
    # blender version
    mycmd += (' \"' + chm_version.__str__() + '\"')
    # path to asset root folder
    mycmd += (' \"' + chm_assetroot.__str__() + '\"')
    # folder sub path below asset folder
    mycmd += (' \"' + chm_assetssubtree.__str__() + '\"')
    # work or publish stage 
    mycmd += (' \"' + chm_tt_stage.__str__() + '\"')
    # path to render root folder
    mycmd += (' \"' + chm_renderroot.__str__() + '\"')
    print("\nmycmd = ", mycmd)
    
    my_build_tt = os.popen(mycmd)
    
    return {'FINISHED'}

def check_departments(asset_name):
    available_depts = []
    print("\nCall update_base_settings from: check_departments")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    if len(asset_name) < 1:
        asset_name = bpy.context.scene.tt_tools_assetname
    print("get_asset_dir -     asset_name: ", asset_name)
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    for the_dept in ["20_model","30_texture"]:
        if len(asset_name) > 1:
            the_asset_type = chm_assetprefix[asset_name[:3]]
            match chm_tt_version:
                case '3.3.x':
                    asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_assetssubtree,the_dept)
                    print('3.3.x asset_dir:', asset_dir)
                case '4.1.x':
                    asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,the_dept,chm_assetssubtree)
                    print("4.1.x asset_dir:", asset_dir)
                case '4.2.x':
                    asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,the_dept,chm_assetssubtree)
                    print("4.2.x asset_dir:", asset_dir)
                case 'Custom':
                    asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_assetssubtree,the_dept)
                    print("Custom asset_dir:", asset_dir)
                case _:
                    asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_assetssubtree,the_dept)
                    print("_")
        asset_dir = asset_dir.replace("/","\\")
        if os.path.exists(asset_dir) and (len(os.listdir(asset_dir)) > 1):
            if the_dept == "20_model":
                available_depts.append('20_model', "Model", "")
            else:
                available_depts.append('30_texture', "Texture", "")
    if os.path.exists(chm_assetroot):
        chm_assettypes = ([f for f in os.listdir(chm_assetroot) if 
                os.path.isdir(os.path.join(chm_assetroot, f))])
        for atype in chm_assettypes:
            thistype = os.path.join(chm_assetroot, atype)
            anames += ([(aname,aname,'') for aname in os.listdir(thistype) if 
                (aname[:3] in chm_assetprefix.keys() and 
                not(aname in chm_omitlist)) and (filtstr.lower() in aname.lower())])
    
    return available_depts

def update_asset_name():
    asset_name = ""
    bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
    asset_name = bpy.context.scene.tt_tools_alist
    return asset_name

def queryAssetList():
    print("\nCall update_base_settings() from: queryAssetList")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    anames = []
    try:
        filtstr = bpy.context.scene.tt_tools_filter
    except:
        filtstr = ""
    if os.path.exists(chm_assetroot):
        chm_assettypes = ([f for f in os.listdir(chm_assetroot) if 
                os.path.isdir(os.path.join(chm_assetroot, f))])
        for atype in chm_assettypes:
            thistype = os.path.join(chm_assetroot, atype)
            anames += ([(aname,aname,'') for aname in os.listdir(thistype) if 
                (aname[:3] in chm_assetprefix.keys() and 
                not(aname in chm_omitlist)) and (filtstr.lower() in aname.lower())])
    return anames

def queryDepartments():
    dept_list = ['20_model', '30_texture']
    dept_names = []
    print("\nCall update_base_settings() from: queryDepartments")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    dept_names = []
    asset_name = bpy.context.scene.tt_tools_alist
    if asset_name is not None:
        asset_dir = get_asset_dir(asset_name)
        if len(os.listdir(asset_dir)) >= 1:
            dept_names.append((chm_tt_stage,chm_tt_stage[3:],""))
            for d in dept_list:
                if not(chm_tt_stage == d):
                    other_dir = asset_dir.replace(chm_tt_stage, d)
                    if len(os.listdir(other_dir)) >= 1:
                        dept_names.append((d,d[3:],""))
    return dept_names

def refreshAssetList():
    thelist = queryAssetList()
    print("thelist:", len(thelist))
    if bpy.context.scene.tt_tools_assetname is not None:
        print(bpy.context.scene.tt_tools_assetname)
        theitem = (bpy.context.scene.tt_tools_assetname,bpy.context.scene.tt_tools_assetname,'')
        print("Found", bpy.context.scene.tt_tools_assetname, " in the enum list returned by queryAssetList(): ", (theitem in thelist))
        if theitem in thelist:
            bpy.context.scene.tt_tools_alist = (bpy.context.scene.tt_tools_assetname)
    return 0

def set_asset_from_name(asset_name):
    queryAssetList()
    try:
        bpy.context.scene.tt_tools_assetname = asset_name
    except:
        print("failed to update bpy.context.scene.tt_tools_assetname: ", asset_name)
    try:
        bpy.context.scene.tt_tools_alist = asset_name
    except:
        print("failed to update bpy.context.scene.tt_tools_alist", asset_name)
    return bpy.context.scene.tt_tools_assetname

def get_asset_dir(asset_name):
    print("\nCall update_base_settings() from: get_asset_dir")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    asset_dir = ""
    if len(asset_name) < 1:
        asset_name = bpy.context.scene.tt_tools_assetname
    print("get_asset_dir       asset_name: ", asset_name)
    print("get_asset_dir   chm_tt_version: ", chm_tt_version)
    # define asset path
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    if len(asset_name) > 1:
        the_asset_type = chm_assetprefix[asset_name[:3]]
        match chm_tt_version:
            case '3.3.x':
                asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_assetssubtree,chm_tt_stage)
                print('3.3.x asset_dir:', asset_dir)
            case '4.1.x':
                asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_tt_stage,chm_assetssubtree)
                print("4.1.x asset_dir:", asset_dir)
            case '4.2.x':
                asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_tt_stage,chm_assetssubtree)
                print("4.2.x asset_dir:", asset_dir)
            case 'Custom':
                asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_assetssubtree,chm_tt_stage)
                print("Custom asset_dir:", asset_dir)
            case _:
                asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_assetssubtree,chm_tt_stage)
                print("_")
    asset_dir = asset_dir.replace("/","\\")
    
    return asset_dir

def get_render_dir(asset_name, asset_version, chm_renderroot, chm_tt_stage, chm_tt_version):
    render_dir = ""
    print("get_render_dir       asset_name: ", asset_name)
    print("get_render_dir   chm_tt_version: ", chm_tt_version)
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    the_asset_type = chm_assetprefix[asset_name[:3]]
    match chm_tt_version:
        case '3.3.x':
            render_dir = os.path.join(chm_renderroot,the_asset_type,asset_name,asset_version)
            print('3.3.x render_dir:', render_dir)
        case '4.1.x':
            render_dir = os.path.join(chm_renderroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_tt_stage,asset_version)
            print("4.1.x render_dir:", render_dir)
        case '4.2.x':
            render_dir = os.path.join(chm_renderroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_tt_stage,asset_version)
            print("4.2.x render_dir:", render_dir)
        case 'Custom':
            render_dir = os.path.join(chm_renderroot,the_asset_type,asset_name,bpy.context.scene.tt_tools_task,chm_tt_stage,asset_version)
            print("Custom render_dir:", render_dir)
        case _:
            render_dir = os.path.join(chm_renderroot,the_asset_type,asset_name,asset_version)
            print("_")
    render_dir = render_dir.replace("/","\\")
    return render_dir

def explore_asset(asset_name):
    print("Call update_base_settings() from: explore_asset")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_dir = get_asset_dir(asset_name)
    if os.path.exists(the_asset_dir):
        subprocess.Popen('explorer \"' + (the_asset_dir) + '\"')
    else:
        tt_tools_messagebox(("Cannot find Path:    " + the_asset_dir), "Missing Path")

    return 0

def get_asset(asset_name):
    #print("ENTER get_asset FUNCTION", asset_name)
    remove_any_existing_asset()
    print("\nCall update_base_settings from: get_asset")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    bpy.context.scene.tt_tools_assetpath = get_asset_dir(asset_name)
    the_asset_dir = bpy.context.scene.tt_tools_assetpath
    print("the_asset_dir: ", the_asset_dir)
    the_asset_path = find_latest_workfile(the_asset_dir)
    the_asset_coll = (asset_name + ":asset_prod")
    if os.path.exists(the_asset_path):
        with bpy.data.libraries.load(the_asset_path, link=False) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        for coll in data_dst.collections:
            if (coll.name == the_asset_coll or coll.name == "asset_prod"):
                bpy.context.scene.collection.children.link(coll)
            for colobj in coll.all_objects:
                if not(colobj.parent):
                    colobj.parent = bpy.data.objects['AnimGrp.asset']
        if bpy.context.scene.tt_tools_task == '20_model':
            set_model_material()
    else:
        if bpy.context.scene.tt_tools_task == '30_texture':
            mytask = "Texture"
        else:
            mytask = "Model"
        tt_tools_messagebox(("Cannot find Path:    " + the_asset_path + "    check if   " + mytask + "   " + chm_tt_stage + "   are set correctly."), "Missing Path")
    return 0

def append_asset(asset_name):
    the_asset_dir = get_asset_dir(asset_name)
    the_asset_path = find_latest_workfile(the_asset_dir)
    the_asset_coll = (asset_name + ":asset_prod")
    if os.path.exists(the_asset_path):
        with bpy.data.libraries.load(the_asset_path, link=False) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        for coll in data_dst.collections:
            #if "asset_prod" in coll.name:
            if (coll.name == the_asset_coll or coll.name == "asset_prod"):
                coll.name = (asset_name + ":asset_prod_appended")
                bpy.context.scene.collection.children.link(coll)
    return 0

def link_asset(asset_name):
    print("\nCall update_base_settings from: link_asset")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_dir = get_asset_dir(asset_name)
    the_asset_path = find_latest_workfile(the_asset_dir)
    the_asset_coll = (asset_name + ":asset_prod")
    if os.path.exists(the_asset_path):
        with bpy.data.libraries.load(the_asset_path, link=True) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        for coll in data_dst.collections:
            #if "asset_prod" in coll.name:
            if (coll.name == the_asset_coll or coll.name == "asset_prod"):
                bpy.context.scene.collection.children.link(coll)
    return 0

def open_assetfile(asset_name):
    print("Call update_base_settings() from: open_assetfile")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_dir = get_asset_dir(asset_name)
    the_asset_path = find_latest_workfile(the_asset_dir)
    this_file_path = os.path.dirname(os.path.realpath(__file__))
    split_asset_version = this_file_path.split("_")
    the_asset_version = "unknown"
    for i in split_asset_version:
        if i[0] == 'v' and len(i) == 4:
            the_asset_version = str(i[1:])
    if bpy.context.scene.userCtx:
        the_username = bpy.context.scene.userCtx
    else:
        the_username = "unknown"
    the_assetname_script = os.path.join(this_file_path, "chums_tt_setassetname.py")
    print("the_assetname_script: ", the_assetname_script)
    if os.path.exists(the_asset_dir):
        if chm_useLP == True and os.path.exists(LAUNCHPAD_REPOSITORY_PATH) and not(chm_tt_version == "3.x"):
            use_lp_launch = True
        else:
            use_lp_launch = False
        if use_lp_launch:
            try:
                print("opening asset in Blender from LAUNCHPAD function")
                sys.path.append(Path(LAUNCHPAD_REPOSITORY_PATH, 'api', 'python').as_posix())
                use_lp_launch = True
            except:
                print("ERROR: trying with DIRECT LOCAL blender path - ie; the same as the one you're using to generate and see this message")
                tt_tools_messagebox("ERROR: trying with DIRECT LOCAL blender path - ie; the same as the one you're using to generate and see this message", "Missing Path")
                use_lp_launch = False
        if use_lp_launch == False:
            mycmd = '\"'
            if os.path.exists(chm_blenderpath):
                print("opening asset in Blender from DEFINED path")
                mycmd += chm_blenderpath
            else:
                print("opening asset in Blender from CURRENT SESSION path")
                mycmd += bpy.app.binary_path
            mycmd += ('\" \"' + the_asset_path)
            mycmd += ('\" -P \"' + str(the_assetname_script) + '\"')
            # asset name
            mycmd += (' -- \"' + asset_name + '\"')
            # addon version
            mycmd += (' \"' + chm_tt_version + '\"')
            # path to asset root folder
            mycmd += (' \"' + chm_assetroot + '\"')
            # user name
            mycmd += (' \"' + the_username + '\"')
            # asset version
            mycmd += (' \"' + the_asset_version + '\"')
            print("\nmycmd: ", mycmd)
            newsesh = os.popen(mycmd)
            use_lp_launch = False
        else:
            from launchpad.helpers.launchers import launchBlenderDetached
            # asset name
            myargs = (' \"' + asset_name + '\"')
            # addon version
            myargs += (' \"' + chm_tt_version + '\"')
            # path to asset root folder
            myargs += (' \"' + chm_assetroot + '\"')
            # user name
            myargs += (' \"' + the_username + '\"')
            # asset version
            myargs += (' \"' + the_asset_version + '\"')
            print("\myargs: ", myargs)
            newsesh = launchBlenderDetached(scenePath=the_asset_path, scriptPath=the_assetname_script, background=False, args=sys.argv)
    else:
        tt_tools_messagebox(("Cannot find Path:    " + the_asset_dir), "Missing Path")

    return 0

def set_output_path(asset_name):
    #410 X:\projects\chums_season2\onsite\renders\_prod\assets\props\prp_cdtest_01\30_texture\work\v001
    #    <chm_renderroot> <asset_type> <asset_name> <asset_task> <asset_stage> <asset_version>
    #331 Y:\projects\CHUMS_Onsite\renders\_prod\assets\characters\chr_emiree\v013
    #    <chm_renderroot> <asset_type> <asset_name> <asset_version>
    the_outpath = ""
    print("\nCall update_base_settings from: set_output_path")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_dir = get_asset_dir(asset_name)
    latest_asset_workfile = find_latest_workfile(the_asset_dir)
    print("latest_asset_workfile: ", latest_asset_workfile)
    latest_asset_version = latest_asset_workfile.split(".")[-2][-4:]
    latest_asset_filename = os.path.basename(latest_asset_workfile)
    the_outpath_base = get_render_dir(asset_name, latest_asset_version, chm_renderroot, chm_tt_stage, chm_tt_version)
    print("the_outpath_base: ", the_outpath_base)
    if not(os.path.exists(the_outpath_base)):
        os.makedirs(the_outpath_base)
    outname = latest_asset_filename.replace(".blend",".####.exr")
    the_outpath = os.path.join(the_outpath_base, outname)
    
    return the_outpath

def set_camera(tt_cam_name, keyframes_cam, keyframes_val):
    if tt_cam_name in bpy.data.objects:
        thecam = bpy.data.objects[tt_cam_name]
        theasset_objects = get_local_asset_objects()
        theasset_size = (get_selection_bounds(theasset_objects))
        theasset_max = 0
        for theasset_dim in theasset_size[0]:
            if theasset_dim >= theasset_max:
                theasset_max = theasset_dim
            thecam.location.z = (((theasset_max/2.0)*(1.0+((2*bpy.context.scene.tt_tools_overscan)/100.0)))/math.tan((bpy.context.scene.camera.data.angle)/2))
            if bpy.data.objects['Ruler']:
                bpy.data.objects['Ruler'].location.y = ((theasset_size[0][1]/2)*(-1.0 - (bpy.context.scene.tt_tools_overscan/100.0)))
            thecam.parent.location.z = (theasset_size[1][2])
            userBaseAngle = math.radians(bpy.context.preferences.addons['chums_tt_addon'].preferences.tt_override_angle)
            for ii in range(len(keyframes_cam)):
                aframe = keyframes_cam[ii]
                avalue = keyframes_val[ii]
                bpy.context.scene.frame_set(aframe)
                thecam.parent.rotation_euler.z = userBaseAngle
                userTiltAngle = math.radians(avalue)
                thecam.parent.rotation_euler.x = userTiltAngle
                thecam.parent.keyframe_insert(data_path='rotation_euler', frame=aframe)
    else:
        tt_tools_messagebox("Camera    " + str(tt_cam_name) + "    appears to be missing.\nPlease ensure you're in a turntable file that contains this object.", "Missing Object")
    
    return 0

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

def save_tt_file(asset_name, asset_task):
    the_outpath = ""
    #bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    print("\nCall update_base_settings from: save_tt_file")
    chm_useLP, chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
    asset_type = chm_assetprefix[asset_name[:3]]
    if chm_tt_version in ["4.1.x","4.2.x"]:
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_tt_stage,chm_assetssubtree).replace("/","\\")
    else:
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_assetssubtree,chm_tt_stage).replace("/","\\")
    latest_asset_workfile = find_latest_workfile(the_workpath)
    if "workfiles" in latest_asset_workfile:
        the_outpath = latest_asset_workfile.replace("workfiles", "turntables")
    else:
        the_outpath = latest_asset_workfile.replace("work", "work\\turntables")
    the_outpath = the_outpath.replace("publish", "publish\\turntables")
    the_outpath = the_outpath.replace(".blend",("_tt.blend"))
    if not(os.path.exists(the_outpath)):
        os.makedirs(the_outpath)
    clean_up_after_blender_save(the_outpath)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=the_outpath)
        clean_up_after_blender_save(the_outpath)
    except:
        tt_tools_messagebox("Error encountered.\nIf it appears the file saved successfully, \nyou may wish to check that file before closing this one,\nto ensure it actually did save correctly.\nIf not please reach out for support to flag the issue.", "File Save Issue")
    return the_outpath

def tt_tools_messagebox(message, title):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon='ERROR')


# -------- REGISTRATION ---------
__all__ = ["tt_tools_messagebox","save_tt_file",
           "clean_up_after_blender_save","set_output_path",
           "open_assetfile","link_asset",
           "append_asset","get_asset",
           "explore_asset","get_asset_dir",
           "queryAssetList","build_turntable",
           "get_assetroot","get_render_dir",
           "set_camera","queryDepartments",
           "find_latest_workfile","remove_any_existing_asset",
           "get_local_asset_objects","get_selection_bounds",
           "xcodeH264","sendDeadlineCmd",
           "getMachineName","getCurrentUser",
           "getPipelineTmpFolder","get_asset_from_path",
           "update_base_settings","blender_version",
           "set_asset_from_name","refreshAssetList"]

#   REGISTER
def register():
    pass

#   UNREGISTER
def unregister():
    pass


# --------     EXEC     ---------
if __name__ == "__main__":
    register()

