# ----------------------- NOTES -----------------------
# 0.4.0 - UPDATE - to Blender version 4.x
# 0.4.1 - UPDATE - removed tunes; set default paths when not 331 or 410 to use 331
# 0.4.2 - FEATURE - string field asset override
#       - DEADLINE SUPPORT - BUG - comment is incorrect for custom submissions
#       - BUG - custom properties don't update scene vars automatically - need to hit refresh button
# 0.4.3 - FEATURE - add enum filter
# 0.4.4 - FEATURE - add LP support
# 0.4.5 - BUGFIX - Custom preferences added - working stable offsite
# 0.4.6 - changed DL tempfile write location to X drive; set deadline pools in submission
# 0.4.7 - FEATURE - rebuild_turntable function - using basefile as starting point, then appending necessary (will require post load script write)
# 0.5.0 - MODULARIZING

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
from .chums_tt_utils import *
from .chums_tt_utils import queryAssetList


# ---    GLOBAL VARIABLES    ----
# VERSION
vsn = '0.5.0b'
#   GET BLENDER MAIN VERSION
blender_version = bpy.app.version
#   SET DEFAULT VERSION STRING
blender_version_str = (str(blender_version[0]) + ".x")
#   SET THE CAMERA OBJECT NAME
thecam_name = "cam.ttCamera"
# OUTPUT PARAMETERS
frameRate = 23.976
thekeyframes_cam = [121,122,123]

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
        chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
        open_this_file = open_assetfile(bpy.context.scene.tt_tools_alist, bpy.context.scene.tt_tools_task, chm_tt_stage)
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
        chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
        explore_asset(bpy.context.scene.tt_tools_alist, bpy.context.scene.tt_tools_task, chm_tt_stage)
        return{'FINISHED'}

class BUTTON_OT_set_cam_loc(bpy.types.Operator):
    '''Set Camera distance from asset.'''
    bl_idname = "tt_tools.set_cam_loc"
    bl_label = "Set Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #print("EXECUTE set_cam_loc OPERATOR")
        if thecam_name in bpy.data.objects:
            thecam = bpy.data.objects[thecam_name]
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
            userBaseAngle = math.radians(bpy.context.preferences.addons['chums_tt_addon'].preferences.defaultangle)
            for aframe in thekeyframes_cam:
                bpy.context.scene.frame_set(aframe)
                thecam.parent.rotation_euler.z = userBaseAngle
                thecam.parent.keyframe_insert(data_path='rotation_euler', frame=aframe)
        else:
            tt_tools_messagebox("Camera    " + str(thecam_name) + "    appears to be missing.\nPlease ensure you're in a turntable file that contains this object.", "Missing Object")
        return{'FINISHED'}

class BUTTON_OT_get_asset(bpy.types.Operator):
    '''REPLACE the asset_prod collection from the latest asset from selected stage; then link asset to turntable helpers.'''
    bl_idname = "tt_tools.get_asset"
    bl_label = "Get Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
        get_asset(bpy.context.scene.tt_tools_alist, bpy.context.scene.tt_tools_task, chm_tt_stage)
        #get_asset(bpy.context.scene.tt_tools_alist, bpy.context.scene.tt_tools_task, bpy.context.scene.tt_override_stage)
        return{'FINISHED'}

class BUTTON_OT_append_asset(bpy.types.Operator):
    '''APPEND the asset_prod collection from the latest PUBLISHED asset'''
    bl_idname = "tt_tools.append_asset"
    bl_label = "Append Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
        append_asset(bpy.context.scene.tt_tools_alist, bpy.context.scene.tt_tools_task, chm_tt_stage)
        return{'FINISHED'}

class BUTTON_OT_get_asset_list(bpy.types.Operator):
    '''Return the latest asset - see console'''
    bl_idname = "tt_tools.get_asset_list"
    bl_label = "Get Asset List"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        the_asset_list = get_asset_list(chm_tt_stage)
        return{'FINISHED'}

class BUTTON_OT_link_asset(bpy.types.Operator):
    '''LINK the asset_prod collection from the latest PUBLISHED asset'''
    bl_idname = "tt_tools.link_asset"
    bl_label = "Link Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
        bpy.context.scene.assetname = bpy.context.scene.tt_tools_alist
        link_asset(bpy.context.scene.tt_tools_alist, bpy.context.scene.tt_tools_task, chm_tt_stage)
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
        chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
        theoutpath = set_output_path(chm_assetroot, chm_renderroot, bpy.context.scene.tt_tools_alist, bpy.context.scene.tt_tools_task, chm_tt_stage)
        bpy.context.scene.render.filepath = theoutpath
        return{'FINISHED'}

class BUTTON_OT_save_ttfile(bpy.types.Operator):
    '''Return the latest asset - see console'''
    bl_idname = "tt_tools.save_ttfile"
    bl_label = "Save Turntable File"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
        thisfilepath = bpy.data.filepath
        thisfilename = os.path.basename(thisfilepath)
        save_tt_file(bpy.context.scene.tt_tools_alist, bpy.context.scene.tt_tools_task, chm_tt_stage)
        
        return{'FINISHED'}

class BUTTON_OT_submit_tt(bpy.types.Operator):
    '''Submit Turntable to Deadline'''
    bl_idname = "tt_tools.submit_tt"
    bl_label = "Submit Turntable Render"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
        thisfilepath = bpy.data.filepath
        thisfilename = os.path.basename(thisfilepath)
        thisoutputpath = bpy.context.scene.render.filepath
        asset_name = bpy.context.scene.tt_tools_alist
        bpy.context.scene.tt_tools_assetname = bpy.context.scene.tt_tools_alist
        theoutpath = set_output_path(chm_assetroot, chm_renderroot, asset_name, bpy.context.scene.tt_tools_task, chm_tt_stage)
        if (bpy.context.scene.tt_tools_alist.lower() in thisfilename.lower() and 
            bpy.context.scene.tt_tools_alist.lower() in thisoutputpath.lower() and
            thisfilename[-8:] == "tt.blend"):
            sendDeadlineCmd()
            if bpy.context.scene.tt_tools_xcode == True:
                xcodeH264()
        else:
            tt_tools_messagebox("To submit a turntable render, this file name must start with the asset selected above    " + str(bpy.context.scene.tt_tools_alist) + "    in the filename and the filename must end with    tt.blend", "Failed Submit")
        
        return{'FINISHED'}

class VIEW3D_PT_tt_tools_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Turntable Utils "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(bpy.context.scene, "tt_tools_newblend")
        #layout.operator("tt_tools.opentt", text=(BUTTON_OT_openTT.bl_label))
        layout.operator("tt_tools.buildtt", text=(BUTTON_OT_buildTT.bl_label))
        layout.prop(bpy.context.scene, "tt_tools_task")
        split = layout.split(factor=0.85, align=True)
        col = split.column(align=True)
        col.prop(bpy.context.scene, "tt_tools_alist")
        col = split.column(align=True)
        col.operator("tt_tools.refresh", text=(BUTTON_OT_refresh.bl_label))
        #layout.prop(bpy.context.scene, "tt_tools_override_asset")
        layout.prop(bpy.context.scene, "tt_tools_filter")
        layout.operator("tt_tools.exploreasset", text=(BUTTON_OT_exploreAsset.bl_label))
        layout.operator("tt_tools.openasset", text=(BUTTON_OT_openAsset.bl_label))
        layout.operator("tt_tools.get_asset", text=(BUTTON_OT_get_asset.bl_label))
        split = layout.split(factor=0.5, align=True)
        col = split.column(align=True)
        col.operator("tt_tools.append_asset", text=(BUTTON_OT_append_asset.bl_label))
        col = split.column(align=True)
        col.operator("tt_tools.link_asset", text=(BUTTON_OT_link_asset.bl_label))
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


#   REGISTER

__all__ = [ "VIEW3D_PT_tt_tools_panel",
            "BUTTON_OT_set_cam_loc", "BUTTON_OT_get_asset", 
            "BUTTON_OT_openTT", "BUTTON_OT_exploreAsset",
            "BUTTON_OT_set_out_filepath", "BUTTON_OT_save_ttfile",
            "BUTTON_OT_tilt_cam", "BUTTON_OT_selectTTcam",
            "BUTTON_OT_openAsset", "BUTTON_OT_submit_tt",
            "BUTTON_OT_refresh", "BUTTON_OT_append_asset",
            "BUTTON_OT_link_asset", "BUTTON_OT_buildTT" ]

def register():
    pass

#   UNREGISTER
def unregister():
    pass

if __name__ == "__main__":
    register()

