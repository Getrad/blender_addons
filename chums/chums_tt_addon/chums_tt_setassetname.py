# ----------------------- NOTES -----------------------

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
from chums_tt_addon.chums_tt_utils import set_asset_from_name

if __name__ == "__main__":
    print("\n\nRunning chums_tt_setassetname.py")
    argv = sys.argv
    print("Setting assetname using argv: ", (argv[-3]))
    tt_asset_name = (argv[-5])
    tt_version = (argv[-4])
    tt_asset_root = (argv[-3])
    tt_user = (argv[-2])
    tt_asset_version = (argv[-1])
    try:
        bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_version = tt_version
    except:
        print("error setting addon preferences version")
    try:
        bpy.context.scene.tt_override_assetroot = tt_asset_root
        bpy.context.preferences.addons["chums_tt_addon"].preferences.tt_override_assetroot = tt_asset_root
    except:
        print("error setting addon preferences version")
    try:
        bpy.context.scene.tt_tools_assetname = tt_asset_name
    except:
        print("error setting scene parameter tt_tools_assetname")
    try:
        bpy.context.scene.entityCtx = tt_asset_name
    except:
        print("error setting scene parameter entityCtx")
    try:
        bpy.context.scene.userCtx = tt_user
    except:
        print("error setting scene parameter userCtx")
    try:
        bpy.context.scene.versionCtx = tt_asset_version
    except:
        print("error setting scene parameter versionCtx")
    print("bpy.context.scene.tt_tools_assetname = ", bpy.context.scene.tt_tools_assetname)
    set_asset_from_name(bpy.context.scene.tt_tools_assetname)
