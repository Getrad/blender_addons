import bpy
import os
import sys

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

if __name__ == "__main__":
    #print("Building Turntable using (sys.argv[1]): ",(sys.argv[1]))
    # build file
    build_turntable((sys.argv[1]))
    # save file
    save_temp_turntable()