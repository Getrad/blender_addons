# ----------------------- NOTES -----------------------
# 0.5.2

import bpy
import os
import sys
import addon_utils
for i in addon_utils.modules():
    if i.bl_info['name'] == 'Turntable Tools':
        print(i)
        addon_utils.enable('chums_tt_addon', default_set=True, persistent=False, handle_error=None)
        from chums_tt_addon.chums_tt_utils import *
        print("IMPORTED FUNCTIONS!")
from chums_tt_addon.chums_tt_utils import get_asset
from chums_tt_addon.chums_tt_utils import set_camera
from chums_tt_addon.chums_tt_utils import set_output_path
from chums_tt_addon.chums_tt_utils import save_tt_file
from chums_tt_addon.chums_tt_utils import sendDeadlineCmd
from chums_tt_addon.chums_tt_utils import xcodeH264


# --------   VARIABLES   --------
# SET THE CAMERA OBJECT NAME
thecam_name = "cam.ttCamera"
# OUTPUT PARAMETERS
thekeyframes_cam = [121,122,123]
thekeyframes_val = [72,135,45]


# --------   FUNCTIONS   --------
def build_turntable(tt_path, tt_range, tt_version):
    print("   Working with turntable file: ", tt_path)
    # define collection list
    coll_list = ['col.anim_controls','col.tt_objects','references','lightrig.sun']
    # import tt collections
    if os.path.exists(tt_path):
        with bpy.data.libraries.load(tt_path, link=False) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        for coll in data_dst.collections:
            if coll.name in coll_list:
                bpy.context.scene.collection.children.link(coll)
    # set active camera
    if bpy.data.objects['cam.ttCamera']:
        bpy.context.scene.camera = bpy.data.objects['cam.ttCamera']
    # confirm output resolution
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.use_motion_blur = False
    # set version
    bpy.context.scene.tt_override_version = tt_version
    try:
        bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_version = tt_version
    except:
        print("error setting addon preferences version")
    # set range
    try:
        if tt_range == "1-123":
            bpy.context.scene.tt_override_range = False
        else:
            bpy.context.scene.tt_override_range = True
    except:
        print("error setting addon preferences tt_override_range")
    bpy.context.scene.frame_start = int(tt_range.split("-")[0])
    bpy.context.scene.frame_end = int(tt_range.split("-")[1])
    # update asset list
    queryAssetList()

def save_temp_turntable():
    current_user = os.getlogin()
    user_path = os.path.join("C:\\users",current_user)
    localtmpdir = os.path.join(user_path, "tmp")
    if not(os.path.exists(localtmpdir)):
        os.mkdir(localtmpdir)
    the_outpath = os.path.join(localtmpdir,"temporary_tt_file.blend")
    print("the_outpath: ", the_outpath)
    try:
        bpy.ops.wm.save_as_mainfile(filepath=the_outpath)
    except:
        print("FAILED TO SAVE TEMP TT FILE")

def load_asset(assetname):
    pass


# --------     EXEC     ---------
if __name__ == "__main__":
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]
    print("Building Turntable using (argv: ", (argv[0]))
    print("   for asset: ", (argv[1]))
    print("   for stage: ", (argv[2]))
    print("    autoload: ", (argv[3]))
    print("  autorender: ", (argv[4]))
    print("  frameRange: ", (argv[5]))
    print("     version: ", (argv[6]))
    if (argv[5]) == "Custom":
        try:
            print("      ttroot: ", (argv[7]))
            print("   ttsubtree: ", (argv[8]))
            print("    tt_stage: ", (argv[9]))
            print("      tt_out: ", (argv[10]))
        except:
            print("Missing arguments for Custom build - troot, ttbase, ttfile, tt_out")
    # build file
    build_turntable((argv[0]), (argv[5]), (argv[6]))
    # save temp local safety file file
    save_temp_turntable()
    # load asset
    queryAssetList()
    if (len(argv[1]) > 1) and (argv[3]) == "True":
        if (argv[6]) == "Custom":
            #update prefs
            bpy.context.scene.tt_override_assetroot = argv[7]
            bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_assetroot = argv[7]
            bpy.context.scene.tt_override_subtree = argv[8]
            bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_subtree = argv[8]
            bpy.context.scene.tt_override_stage = argv[9]
            bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_stage = argv[9]
            bpy.context.scene.tt_override_renderroot = argv[10]
            bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_renderroot = argv[10]
        #from chums_tt_addon.chums_tt_utils import get_asset
        bpy.context.scene.tt_tools_assetname = (argv[1])
        bpy.context.scene.tt_tools_task = (argv[2])
        get_asset(bpy.context.scene.tt_tools_assetname)
        print("   bpy.context.scene.tt_tools_task: ", bpy.context.scene.tt_tools_task)
        set_camera(thecam_name, thekeyframes_cam, thekeyframes_val)
        bpy.context.scene.render.filepath = set_output_path(bpy.context.scene.tt_tools_assetname)
        save_temp_turntable()
        if (argv[4]) == "True":
            # launch render
            save_tt_file(bpy.context.scene.tt_tools_assetname, bpy.context.scene.tt_tools_task)
            sendDeadlineCmd()
            xcodeH264()
            save_tt_file(bpy.context.scene.tt_tools_assetname, bpy.context.scene.tt_tools_task)
        
    
    