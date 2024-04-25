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

# ---    GLOBAL VARIABLES    ----
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
# OMIT THESE ASSET NAMES
chm_omitlist = (['archive', 'chr_AAAtemplate', 'chr_ants', 'chr_barry - Copy', 'chr_squirrel', 
                'env_AAAtemplate', 'env_rompersburrow', 
                'prp_AAAtemplate', 'prp_bush_romperPopout_01', 'prp_tree_hollowknot',
                'prx_AAAtemplate', 'prx_treeObstacle_Source'])
# LAUNCHPAD
LAUNCHPAD_REPOSITORY_PATH = "X:/projects/chums_season2/onsite/pipeline/repos/launchpadRepository"

# FUNCTIONS
def update_base_settings(): #(chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version)
    try:
        override_version = (str(bpy.context.scene.tt_override_version))
        print("override_version:", override_version)
        print("using PREFERENCES")
    except:
        override_version = (str(blender_version[0]) + ".x")
        print("override_version:", override_version)
        print("using DEFAULTS")
    
    print("override_version:", override_version)
    
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
        
        if len(bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_range) > 0:
            pref_range = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_range
            bpy.context.scene.tt_override_range = pref_range
        else:
            pref_range = "BOO"
            bpy.context.scene.tt_override_range = pref_range
        print("    pref_range:", pref_range)
        
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
        print("    tt_override_stage:", pref_tt_stage)

    match blender_version_str:
        case '3.x':
            pref_assetroot = "Y:/projects/CHUMS_Onsite/_prod/assets/"
            pref_tt_filepath = Path(str(pref_assetroot + "helpers/turntable/projects/blender/turntable_331.blend"))
            pref_basefile = 'Y:/projects/CHUMS_Onsite/_prod/assets/helpers/basefiles/publish/'
            pref_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
            pref_assetssubtree = "projects/blender"
            pref_assetturntables = "/projects/blender/turntables"
            pref_range = "1-123"
            pref_tt_stage = 'workfiles'
        case '4.x':
            pref_assetroot = "X:/projects/chums_season2/onsite/_prod/assets"
            pref_tt_filepath = Path(str(pref_assetroot + "/helpers/turntable/publish/blender/turntable_410.blend"))
            pref_basefile = 'X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish'
            pref_renderroot = "X:/projects/chums_season2/onsite/renders/_prod/assets"
            pref_assetssubtree = "blender"
            pref_assetturntables = "turntables"
            pref_range = "1-123"
            pref_tt_stage = 'work'
        case _:
            pref_assetroot = "Y:/projects/CHUMS_Onsite/_prod/assets/"
            pref_tt_filepath = Path(str(pref_assetroot + "helpers/turntable/projects/blender/turntable_331.blend"))
            pref_basefile = 'X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish'
            pref_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
            pref_assetssubtree = "projects/blender"
            pref_assetturntables = "/projects/blender/turntables"
            pref_range = "1-123"
            pref_tt_stage = 'workfiles'
    if override_version == 'Custom':
        if len(bpy.context.scene.tt_override_assetroot) > 0:
            pref_assetroot = bpy.context.scene.tt_override_assetroot
        if len(bpy.context.scene.tt_override_filepath) > 0:
            pref_tt_filepath = bpy.context.scene.tt_override_filepath
        if len(bpy.context.scene.tt_override_basefile) > 0:
            pref_basefile = bpy.context.scene.tt_override_basefile
        if len(bpy.context.scene.tt_override_renderroot) > 0:
            pref_renderroot = bpy.context.scene.tt_override_renderroot
        if len(bpy.context.scene.tt_override_range) > 0:
            pref_range = bpy.context.scene.tt_override_range
        if len(bpy.context.scene.tt_override_stage) > 0:
            pref_tt_stage = bpy.context.scene.tt_override_stage
        if len(bpy.context.scene.tt_override_subtree) > 0:
            pref_assetssubtree = bpy.context.scene.tt_override_subtree
        
    pref_override_version = override_version
    
    print("\npref_assetroot:", pref_assetroot, "\npref_basefile:", pref_basefile, "\npref_tt_filepath:", pref_tt_filepath, "\npref_renderroot:", pref_renderroot)
    return(pref_assetroot, pref_basefile, pref_tt_filepath, pref_renderroot, pref_assetssubtree, pref_assetturntables, pref_range, pref_tt_stage, pref_override_version)

def get_asset_from_path(path):
    asset_name = ""
    asset_name = path.split("\\")[-1]
    return asset_name

def getPipelineTmpFolder():
    #tmp = r'Y:\projects\CHUMS_Onsite\pipeline\tmp'
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
    asset_name = bpy.context.scene.tt_tools_alist
    bpy.context.scene.tt_tools_assetname = asset_name
    asset_task = bpy.context.scene.tt_tools_task
    chm_assetprefix = {'chr':'characters', 
                        'env':'environments', 
                        'prp':'props', 
                        'prx':'proxies',
                        'sky':'skies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    print("call update_base_settings from: sendDeadlineCmd")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    if chm_tt_version == "4.x":
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_tt_stage,chm_assetssubtree).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,asset_type,asset_name,asset_task,chm_tt_stage).replace("/","\\")
        the_comment = "4.x Turntable"
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
    outname = latest_asset_filename.replace(".blend",".####.png")
    thisoutputpath = os.path.join(the_outpath_base, outname)
    dlName = os.path.basename(thisfilename)[:-6]
    dlSceneFile = Path(thisfilename).as_posix()
    dlOutputFile = Path(thisoutputpath).as_posix()
    #dlFrames = '0-123'
    #dlFrames = str(bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_range)
    dlFrames = str(chm_tt_range)
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
    asset_name = bpy.context.scene.tt_tools_alist
    bpy.context.scene.tt_tools_assetname = asset_name
    asset_task = bpy.context.scene.tt_tools_task
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    if chm_tt_version == "4.x":
        the_workpath = os.path.join(chm_assetroot,asset_type,asset_name,asset_task,chm_tt_stage,chm_assetssubtree).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,asset_type,asset_name,asset_task,chm_tt_stage).replace("/","\\")
        the_comment = "4.x Turntable"
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
    outname = latest_asset_filename.replace(".blend",".####.png")
    outmovname = os.path.basename(latest_asset_filename)[:-6]
    the_outpath = os.path.join(the_outpath_base, outname)
    dlName = os.path.basename(thisfilename)[:-6]
    dlSceneFile = Path(thisfilename).as_posix()
    dlOutputFile = Path(the_outpath).as_posix()
    dlOutputPath = Path(the_outpath_base).as_posix()
    dlFrames = str(chm_tt_range)
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
    with open(pluginInfoPath, 'w') as f:
        f.write(f"InputFile0={dlOutputFile.replace('####', '%04d')}\n") # the image sequence
        f.write(f"InputArgs0=-r {frameRate}\n") # force the image sequence fps to output framerate
        f.write(f"ReplacePadding0=False\n")
        f.write(f"OutputArgs=-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -level 4.1 -r {frameRate} -s 1080x1080 -map 0:v:0 -y\n")
        f.write(f"OutputFile={Path(dlOutputPath).joinpath((outmovname) + '_h264.mov')}\n")
    
    command = f'{deadlineBin} {jobInfoPath} {pluginInfoPath}'
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
    #print("\nENTER get_local_asset_objects FUNCTION")
    object_list = []
    for col in bpy.data.collections:
        if col.name == "asset_prod":
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
    #print("\nENTER get_assetroot FUNCTION")
    try:
        tt_override_assetroot = bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_assetroot
    except:
        tt_override_assetroot = chm_assetroot
    print("fn get_assetroot returns ", tt_override_assetroot)
    return tt_override_assetroot

def open_turntable():
    print("call update_base_settings from: open_turntable")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    if os.path.exists(chm_tt_filepath):
        if bpy.context.scene.tt_tools_newblend:
            if os.path.exists(LAUNCHPAD_REPOSITORY_PATH):
                print("launching Blender from LAUNCHPAD function")
                sys.path.append(Path(LAUNCHPAD_REPOSITORY_PATH, 'api', 'python').as_posix())
                from launchpad.helpers.launchers import launchBlenderDetached
                newsesh = launchBlenderDetached(scenePath=chm_tt_filepath, scriptPath=None, background=False, args=sys.argv)
            else:
                print("launching Blender from DIRECT local path")
                mycmd = '\"'
                mycmd += bpy.app.binary_path
                mycmd += ('\" \"' + chm_tt_filepath.__str__() + '\"')
                newsesh = os.popen(mycmd)
        else:
            bpy.ops.wm.open_mainfile(filepath=chm_tt_filepath.__str__())
    else:
        tt_tools_messagebox("Turntable cannot be found here:    " + str(chm_tt_filepath) + "\nPlease check path manually and notify your supervisor if you can see and open the file directly.", "Turntable Missing")
    return {'FINISHED'}

def build_turntable():
    print("\ncall update_base_setting() from: build_turntable")
    this_file_path = os.path.dirname(os.path.realpath(__file__))
    chm_postload = os.path.join(this_file_path, 'chums_tt_build.py')
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    chm_basefile = find_latest_workfile(chm_tt_basedir)
    print("chm_basefile: ", chm_basefile)
    mycmd = '\"'
    mycmd += bpy.app.binary_path
    mycmd += ('\" \"' + chm_basefile.__str__() + "\"")
    mycmd += (' -P \"' + chm_postload.__str__() + ("\""))
    mycmd += (' -- \"' + chm_tt_filepath.__str__() + '\"')
    print("\nmycmd = ", mycmd)
    
    my_build_tt = os.popen(mycmd)
    
    return {'FINISHED'}

def queryAssetList():
    #print("\nENTER queryAssetList FUNCTION")
    print("call update_base_settings from: queryAssetList")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    print("chm_assetroot: ", chm_assetroot, "\nchm_tt_filepath: ", chm_tt_filepath, "\nchm_renderroot: ", chm_renderroot, "\nchm_assetssubtree: ", chm_assetssubtree, "\nchm_assetturntables: ", chm_assetturntables, "\nchm_tt_stage: ", chm_tt_stage, "\nchm_tt_version: ", chm_tt_version)
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

def explore_asset(asset_name, asset_dept, asset_stage):
    chm_assetprefix = {'chr':'characters', 
                    'env':'environments', 
                    'prp':'props', 
                    'prx':'proxies',
                    'sky':'skies'}
    print("call update_base_settings from: explore_asset")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_type = chm_assetprefix[asset_name[:3]]
    if chm_tt_version == "4.x":
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,asset_stage,chm_assetssubtree).replace("/","\\")
    else:
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_assetssubtree,asset_stage).replace("/","\\")
    print("the_asset_dir:", the_asset_dir)
    print("       exists:", os.path.exists(the_asset_dir))
    if os.path.exists(the_asset_dir):
        subprocess.Popen('explorer \"' + the_asset_dir + '\"')
    else:
        # return messagebox showing filepath and message that it can't be found
        tt_tools_messagebox(("Cannot find Path:    " + the_asset_dir), "Missing Path")
        #print("CANNOT FIND PATH: ", the_asset_dir)

    return 0

def get_asset_list(asset_stage):
    asset_list = []
    for asset_type in chm_assettypes:
        chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
        asset_type_path = (os.path.join(chm_assetroot,asset_type))
        assets = [o for o in os.listdir(asset_type_path) if (not(o[-3:] == "zip") and not("_AAA" in o) and not(o == ".DS_Store"))]
        for asset in assets:
            # find the asset blender folder
            this_asset_path = os.path.join(asset_type_path,asset,chm_assetssubtree,asset_stage)
            this_latest_filepath = find_latest_workfile(this_asset_path)
            if len(this_latest_filepath) > 0:
                asset_list.append((asset,asset,""))

    return asset_list

def get_asset(asset_name, asset_dept, asset_stage):
    #print("ENTER get_asset FUNCTION", asset_name)
    remove_any_existing_asset()
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    print("call update_base_settings from: get_asset")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_type = chm_assetprefix[asset_name[:3]]
    if chm_tt_version == "4.x":
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_tt_stage,chm_assetssubtree).replace("/","\\")
    else:
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_assetssubtree,chm_tt_stage).replace("/","\\")
    #print("the_asset_dir:", the_asset_dir)
    the_asset_path = find_latest_workfile(the_asset_dir)
    #print("the_asset_path:", the_asset_path)
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
        if bpy.context.scene.tt_tools_task == '30_texture':
            mytask = "Texture"
        else:
            mytask = "Model"
        # return messagebox showing filepath and message that it can't be found
        tt_tools_messagebox(("Cannot find Path:    " + the_asset_dir + "    check if   " + mytask + "   " + chm_tt_stage + "   are set correctly."), "Missing Path")
    return 0

def append_asset(asset_name, asset_dept, asset_stage):
    #print("ENTER get_asset FUNCTION", asset_name)
    #asset_stage = "publish"
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    print("call update_base_settings from: append_asset")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_type = chm_assetprefix[asset_name[:3]]
    if chm_tt_version == "4.x":
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_tt_stage,chm_assetssubtree).replace("/","\\")
    else:
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_assetssubtree,chm_tt_stage).replace("/","\\")
    #print("the_asset_dir:", the_asset_dir)
    the_asset_path = find_latest_workfile(the_asset_dir)
    #print("the_asset_path:", the_asset_path)
    if os.path.exists(the_asset_path):
        with bpy.data.libraries.load(the_asset_path, link=False) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        for coll in data_dst.collections:
            if "asset_prod" in coll.name:
                coll.name = (asset_name + "_asset_prod_appended")
                bpy.context.scene.collection.children.link(coll)
    return 0

def link_asset(asset_name, asset_dept, asset_stage):
    #print("ENTER get_asset FUNCTION", asset_name)
    #asset_stage = "publish"
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    print("call update_base_settings from: link_asset")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_type = chm_assetprefix[asset_name[:3]]
    if chm_tt_version == "4.x":
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_tt_stage,chm_assetssubtree).replace("/","\\")
    else:
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_assetssubtree,chm_tt_stage).replace("/","\\")
    #print("the_asset_dir:", the_asset_dir)
    the_asset_path = find_latest_workfile(the_asset_dir)
    #print("the_asset_path:", the_asset_path)
    if os.path.exists(the_asset_path):
        with bpy.data.libraries.load(the_asset_path, link=True) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        for coll in data_dst.collections:
            if "asset_prod" in coll.name:
                #coll.name = (asset_name + "_asset_prod_appended")
                bpy.context.scene.collection.children.link(coll)
    return 0

def open_assetfile(asset_name, asset_dept, asset_stage):
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    the_asset_type = chm_assetprefix[asset_name[:3]]
    print("call update_base_settings from: open_assetfile")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    if chm_tt_version == "4.x":
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_tt_stage,chm_assetssubtree)
    else:
        the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_dept,chm_assetssubtree,chm_tt_stage)
    #print("the_asset_dir:", the_asset_dir)
    the_asset_path = find_latest_workfile(the_asset_dir)
    if os.path.exists(the_asset_dir):
        if bpy.context.scene.tt_tools_newblend:
            if os.path.exists(LAUNCHPAD_REPOSITORY_PATH):
                print("opening asset in Blender from LAUNCHPAD function")
                sys.path.append(Path(LAUNCHPAD_REPOSITORY_PATH, 'api', 'python').as_posix())
                from launchpad.helpers.launchers import launchBlenderDetached
                newsesh = launchBlenderDetached(scenePath=the_asset_path, scriptPath=None, background=False, args=sys.argv)
            else:
                print("opening asset in Blender from DIRECT local path")
                mycmd = '\"'
                mycmd += bpy.app.binary_path
                mycmd += ('\" \"' + the_asset_path + '\"')
                newsesh = os.popen(mycmd)
        else:
            bpy.ops.wm.open_mainfile(filepath=the_asset_path)
    else:
        # return messagebox showing filepath and message that it can't be found
        tt_tools_messagebox(("Cannot find Path:    " + the_asset_dir), "Missing Path")
        #print("CANNOT FIND PATH: ", the_asset_dir)

    return 0

def set_output_path(asset_root, render_root, asset_name, asset_task, asset_stage):
    #410 X:\projects\chums_season2\onsite\renders\_prod\assets\props\prp_cdtest_01\30_texture\work\v001
    #    <chm_renderroot> <asset_type> <asset_name> <asset_task> <asset_stage> <asset_version>
    #331 Y:\projects\CHUMS_Onsite\renders\_prod\assets\characters\chr_emiree\v013
    #    <chm_renderroot> <asset_type> <asset_name> <asset_version>
    the_outpath = ""
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    print("call update_base_settings from: set_output_path")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    the_asset_type = chm_assetprefix[asset_name[:3]]
    if chm_tt_version == "4.x":
        the_workpath = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_task,chm_tt_stage,chm_assetssubtree).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,the_asset_type,asset_name,asset_task,chm_tt_stage).replace("/","\\")
    else:
        the_workpath = os.path.join(chm_assetroot,the_asset_type,asset_name,asset_task,chm_assetssubtree,chm_tt_stage).replace("/","\\")
        the_outpath_base = os.path.join(chm_renderroot,the_asset_type,asset_name).replace("/","\\")
    print("the_workpath: ", the_workpath)
    latest_asset_workfile = find_latest_workfile(the_workpath)
    print("latest_asset_workfile: ", latest_asset_workfile)
    latest_asset_version = latest_asset_workfile.split(".")[-2][-4:]
    latest_asset_filename = os.path.basename(latest_asset_workfile)
    the_outpath_base = os.path.join(the_outpath_base, latest_asset_version)
    print("the_workpath: ", the_workpath)
    print("latest_asset_workfile: ", latest_asset_workfile)
    print("the_outpath_base: ", the_outpath_base)
    if not(os.path.exists(the_outpath_base)):
        os.makedirs(the_outpath_base)
    outname = latest_asset_filename.replace(".blend",".####.png")
    the_outpath = os.path.join(the_outpath_base, outname)
    
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
    asset_name = bpy.context.scene.tt_tools_alist
    bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
    asset_task = bpy.context.scene.tt_tools_task
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies',
                       'sky':'skies'}
    print("call update_base_settings from: save_tt_file")
    chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_range, chm_tt_stage, chm_tt_version = update_base_settings()
    asset_type = chm_assetprefix[asset_name[:3]]
    if chm_tt_version == "4.x":
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

__all__ = ["tt_tools_messagebox","save_tt_file",
           "clean_up_after_blender_save","set_output_path",
           "open_assetfile","link_asset",
           "append_asset","get_asset",
           "get_asset_list","explore_asset",
           "queryAssetList","build_turntable",
           "open_turntable","get_assetroot",
           "find_latest_workfile","remove_any_existing_asset",
           "get_local_asset_objects","get_selection_bounds",
           "xcodeH264","sendDeadlineCmd",
           "getMachineName","getCurrentUser",
           "getPipelineTmpFolder","get_asset_from_path",
           "update_base_settings","blender_version"
           ]

def register():
    pass

#   UNREGISTER
def unregister():
    pass
    
if __name__ == "__main__":
    register()

