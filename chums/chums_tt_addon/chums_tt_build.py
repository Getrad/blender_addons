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
def build_turntable(tt_path):
    print("   Working with turntable file: ", tt_path)
    #define collection list
    coll_list = ['col.anim_controls','col.tt_objects','references','lightrig.sun']
    #import tt collections
    if os.path.exists(tt_path):
        with bpy.data.libraries.load(tt_path, link=False) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        for coll in data_dst.collections:
            if coll.name in coll_list:
                bpy.context.scene.collection.children.link(coll)
    if bpy.data.objects['cam.ttCamera']:
        bpy.context.scene.camera = bpy.data.objects['cam.ttCamera']
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080

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
    # build file
    build_turntable((argv[0]))
    # save temp local safety file file
    save_temp_turntable()
    # load asset
    queryAssetList()
    from chums_tt_addon.chums_tt_utils import get_asset
    bpy.context.scene.tt_tools_alist = (argv[1])
    print("   bpy.context.scene.tt_tools_alist: ", bpy.context.scene.tt_tools_alist)
    bpy.context.scene.tt_tools_task = (argv[2])
    get_asset((argv[1]))
    print("   bpy.context.scene.tt_tools_task: ", bpy.context.scene.tt_tools_task)
    set_camera(thecam_name, thekeyframes_cam, thekeyframes_val)
    #set_output_path(asset_name)
    #save_tt_file(asset_name, asset_task)
    #sendDeadlineCmd()
    #xcodeH264()
    #save_tt_file(asset_name, asset_task)
    
    
    