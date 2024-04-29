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

def build_turntable(tt_path):
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
    from chums_tt_addon.chums_tt_utils import get_asset
    from chums_tt_addon.chums_tt_utils import set_camera
    from chums_tt_addon.chums_tt_utils import set_output_path
    from chums_tt_addon.chums_tt_utils import save_tt_file
    from chums_tt_addon.chums_tt_utils import sendDeadlineCmd
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

def load_asset(asset_entity):
    pass

if __name__ == "__main__":
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]
    print("Building Turntable using (argv: ", (argv[0]))
    # build file
    build_turntable((argv[0]))
    # load asset
    #from chums_tt_addon.chums_tt_utils import get_asset
    #get_asset(asset_name, asset_dept, asset_stage)
    #set_camera(tt_cam_name, keyframes_cam, keyframes_val)
    #set_output_path(asset_root, render_root, asset_name, asset_task, asset_stage)
    #save_tt_file(asset_name, asset_task, asset_stage)
    #sendDeadlineCmd()
    # save file
    save_temp_turntable()
    