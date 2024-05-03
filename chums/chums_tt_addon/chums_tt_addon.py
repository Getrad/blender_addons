# ----------------------- NOTES -----------------------
# 0.5.0 - MODULARIZING
####### - NOW TRACKED IN INIT FILE

# ---    GLOBAL IMPORTS    ----
from pathlib import Path
from getpass import getuser
from socket import gethostname
from importlib import reload
import bpy
import os
import re
import math
import shutil
import uuid
import sys
import subprocess
import builtins
from chums_tt_addon.chums_tt_utils import *
from chums_tt_addon.chums_tt_utils import queryAssetList
from chums_tt_addon.chums_tt_utils import set_camera


# --------   VARIABLES   --------
# VERSION
vsn = '0.5.2a'
# GET BLENDER MAIN VERSION
blender_version = bpy.app.version
# SET DEFAULT VERSION STRING
blender_version_str = (str(blender_version[0]) + ".x")
# SET THE CAMERA OBJECT NAME
thecam_name = "cam.ttCamera"
# OUTPUT PARAMETERS
thekeyframes_cam = [121,122,123]
thekeyframes_val = [72,135,45]


# --------    CLASSES    --------
# OPERATORS
class BUTTON_OT_openTT(bpy.types.Operator):
    '''Open Turntable Basefile.'''
    bl_idname = "tt_tools.opentt"
    bl_label = "Open Turntable"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        open_this_file = open_turntable()
        print(open_this_file)
        return{'FINISHED'}

class BUTTON_OT_buildTT(bpy.types.Operator):
    '''Build Turntable Basefile.'''
    bl_idname = "tt_tools.buildtt"
    bl_label = "Build Turntable"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        build_this_file = build_turntable()
        print(build_this_file)
        return{'FINISHED'}

class BUTTON_OT_openAsset(bpy.types.Operator):
    '''Open Latest Asset File'''
    bl_idname = "tt_tools.openasset"
    bl_label = "Open Asset File"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        open_this_file = open_assetfile(bpy.context.scene.tt_tools_assetname)
        return{'FINISHED'}

class BUTTON_OT_refresh(bpy.types.Operator):
    '''Refresh the Asset List'''
    bl_idname = "tt_tools.refresh"
    bl_label = "Refresh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.types.Scene.tt_tools_alist = bpy.props.EnumProperty(
            name="",
            description="Asset List",
            items=queryAssetList(),
            default = None
            )
        return{'FINISHED'}

class BUTTON_OT_exploreAsset(bpy.types.Operator):
    '''Open Asset Folder'''
    bl_idname = "tt_tools.exploreasset"
    bl_label = "Explore Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("call update_base_settings from: BUTTON_OT_exploreAsset")
        bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        #chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
        explore_asset(bpy.context.scene.tt_tools_assetname)
        return{'FINISHED'}

class BUTTON_OT_set_cam_loc(bpy.types.Operator):
    '''Set Camera distance from asset.'''
    bl_idname = "tt_tools.set_cam_loc"
    bl_label = "Set Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #print("EXECUTE set_cam_loc OPERATOR")
        thekeyframes_val = [72,135,45]
        set_camera(thecam_name, thekeyframes_cam, thekeyframes_val)
        return{'FINISHED'}

class BUTTON_OT_get_asset(bpy.types.Operator):
    '''REPLACE the asset_prod collection from the latest asset from selected stage; then link asset to turntable helpers.'''
    bl_idname = "tt_tools.get_asset"
    bl_label = "Get Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        if len(bpy.context.scene.tt_tools_assetname) < 1 or (bpy.context.scene.tt_tools_assetname != bpy.context.scene.tt_tools_alist):
            bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        get_asset(bpy.context.scene.tt_tools_assetname)
        return{'FINISHED'}

class BUTTON_OT_append_asset(bpy.types.Operator):
    '''APPEND the asset_prod collection from the latest PUBLISHED asset'''
    bl_idname = "tt_tools.append_asset"
    bl_label = "Append Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("\n\nCall update_base_settings from: BUTTON_OT_append_asset")
        #chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
        try:
            bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        except:
            print("FAIL to update bpy.context.scene.tt_tools_assetname, using: ", bpy.context.scene.tt_tools_assetname)
        append_asset(bpy.context.scene.tt_tools_assetname)
        return{'FINISHED'}

class BUTTON_OT_link_asset(bpy.types.Operator):
    '''LINK the asset_prod collection from the latest PUBLISHED asset'''
    bl_idname = "tt_tools.link_asset"
    bl_label = "Link Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("\n\nCall update_base_settings from: BUTTON_OT_link_asset")
        #chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
        try:
            bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        except:
            print("FAIL to update bpy.context.scene.tt_tools_assetname, using: ", bpy.context.scene.tt_tools_assetname)
        link_asset(bpy.context.scene.tt_tools_assetname)
        return{'FINISHED'}

class BUTTON_OT_tilt_cam(bpy.types.Operator):
    '''Select the camera tilt control'''
    bl_idname = "tt_tools.tilt_cam"
    bl_label = "Select Camera Control"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if "AnimGrp.camera" in bpy.data.objects:
            for o in bpy.context.selected_objects:
                o.select_set(False)
            bpy.data.objects["AnimGrp.camera"].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects["AnimGrp.camera"]
        else:
            tt_tools_messagebox("Camera control object    AnimGrp.camera    appears to be missing.\nPlease ensure you're in a turntable file that contains this object.", "Missing Object")
        return{'FINISHED'}

class BUTTON_OT_selectTTcam(bpy.types.Operator):
    '''Select turntable camera object.'''
    bl_idname = "tt_tools.selectttcam"
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
                pass
                #print("FAILED TO FIND " + str(thecam_name))
        else:
            tt_tools_messagebox("Camera " + str(thecam_name) + "appears to be missing.\nPlease ensure you're in a turntable file that contains this object.", "Missing Object")
        return{'FINISHED'}

class BUTTON_OT_set_out_filepath(bpy.types.Operator):
    '''Set Output path.'''
    bl_idname = "tt_tools.set_out_filepath"
    bl_label = "Set Output"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
        theoutpath = set_output_path(bpy.context.scene.tt_tools_assetname)
        bpy.context.scene.render.filepath = theoutpath
        return{'FINISHED'}

class BUTTON_OT_save_ttfile(bpy.types.Operator):
    '''Return the latest asset - see console'''
    bl_idname = "tt_tools.save_ttfile"
    bl_label = "Save Turntable File"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thisfilepath = bpy.data.filepath
        thisfilename = os.path.basename(thisfilepath)
        save_tt_file(bpy.context.scene.tt_tools_assetname, bpy.context.scene.tt_tools_task)
        
        return{'FINISHED'}

class BUTTON_OT_submit_tt(bpy.types.Operator):
    '''Submit Turntable to Deadline'''
    bl_idname = "tt_tools.submit_tt"
    bl_label = "Submit Turntable Render"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #chm_blenderpath, chm_assetroot, chm_tt_basedir, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_tt_stage, chm_tt_version = update_base_settings()
        thisfilepath = bpy.data.filepath
        thisfilename = os.path.basename(thisfilepath)
        thisoutputpath = bpy.context.scene.render.filepath
        asset_name = bpy.context.scene.tt_tools_alist
        bpy.context.scene.tt_tools_assetname = asset_name
        theoutpath = set_output_path(bpy.context.scene.tt_tools_assetname)
        if (bpy.context.scene.tt_tools_assetname.lower() in thisfilename.lower() and 
            bpy.context.scene.tt_tools_assetname.lower() in thisoutputpath.lower() and
            thisfilename[-8:] == "tt.blend"):
            sendDeadlineCmd()
            if bpy.context.scene.tt_tools_xcode == True:
                xcodeH264()
        else:
            tt_tools_messagebox("To submit a turntable render, this file name must start with the asset selected above    " + str(bpy.context.scene.tt_tools_assetname) + "    in the filename and the filename must end with    tt.blend", "Failed Submit")
        
        return{'FINISHED'}

#PANEL
class VIEW3D_PT_tt_tools_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Turntable Utils "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        #layout.label(text="Build Turntable")
        split = layout.split(factor=0.5, align=True)
        col = split.column(align=True)
        col.prop(bpy.context.scene, "tt_tools_autoload")
        col = split.column(align=True)
        col.prop(bpy.context.scene, "tt_tools_autorender")
        layout.operator("tt_tools.buildtt", text=(BUTTON_OT_buildTT.bl_label))
        #layout.label(text="Asset")
        layout.prop(bpy.context.scene, "tt_tools_filter")
        split = layout.split(factor=0.75, align=True)
        col = split.column(align=True)
        col.prop(bpy.context.scene, "tt_tools_alist")
        col = split.column(align=True)
        col.operator("tt_tools.refresh", text=(BUTTON_OT_refresh.bl_label))
        #layout.label(text="Department/Task")
        layout.prop(bpy.context.scene, "tt_tools_task")
        #layout.label(text="Actions")
        layout.operator("tt_tools.exploreasset", text=(BUTTON_OT_exploreAsset.bl_label))
        layout.operator("tt_tools.openasset", text=(BUTTON_OT_openAsset.bl_label))
        layout.operator("tt_tools.get_asset", text=(BUTTON_OT_get_asset.bl_label))
        split = layout.split(factor=0.5, align=True)
        col = split.column(align=True)
        col.operator("tt_tools.append_asset", text=(BUTTON_OT_append_asset.bl_label))
        col = split.column(align=True)
        col.operator("tt_tools.link_asset", text=(BUTTON_OT_link_asset.bl_label))
        layout.label(text="Camera")
        layout.prop(bpy.context.scene, "tt_tools_overscan")
        layout.operator("tt_tools.set_cam_loc", text=(BUTTON_OT_set_cam_loc.bl_label))
        layout.operator("tt_tools.tilt_cam", text=(BUTTON_OT_tilt_cam.bl_label))
        layout.operator("tt_tools.selectttcam", text=(BUTTON_OT_selectTTcam.bl_label))
        layout.operator("tt_tools.set_out_filepath", text=(BUTTON_OT_set_out_filepath.bl_label))
        layout.operator("tt_tools.save_ttfile", text=(BUTTON_OT_save_ttfile.bl_label))
        layout.operator("tt_tools.submit_tt", text=(BUTTON_OT_submit_tt.bl_label))
        split = layout.split(factor=0.5, align=True)
        col = split.column(align=True)
        col.prop(bpy.context.scene, "tt_tools_xcode")
        col = split.column(align=True)
        col.prop(bpy.context.scene, "tt_tools_draft")
        layout.prop(bpy.context.scene, "tt_override_range")
        


# -------- REGISTRATION ---------
__all__ = [ "VIEW3D_PT_tt_tools_panel",
            "BUTTON_OT_set_cam_loc", "BUTTON_OT_get_asset", 
            "BUTTON_OT_openTT", "BUTTON_OT_exploreAsset",
            "BUTTON_OT_set_out_filepath", "BUTTON_OT_save_ttfile",
            "BUTTON_OT_tilt_cam", "BUTTON_OT_selectTTcam",
            "BUTTON_OT_openAsset", "BUTTON_OT_submit_tt",
            "BUTTON_OT_refresh", "BUTTON_OT_append_asset",
            "BUTTON_OT_link_asset", "BUTTON_OT_buildTT" ]

#   REGISTER
def register():
    pass

#   UNREGISTER
def unregister():
    pass


# --------     EXEC     ---------
if __name__ == "__main__":
    register()

