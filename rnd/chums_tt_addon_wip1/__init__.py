# 0.4.7 - FEATURE - rebuild_turntable function - using basefile as starting point, then appending necessary (will require post load script write)

import bpy
import os
from pathlib import Path

from .chums_tt_utils import *
from .chums_tt_addon import *
#from .chums_tt_utils import queryAssetList

bl_info = {
    "name": "Turntable Tools",
    "author": "Conrad Dueck, Darren Place",
    "version": (0, 5, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Turntable Convenience Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

# ---    GLOBAL VARIABLES    ----
#   GET BLENDER MAIN VERSION
blender_version = bpy.app.version
#   SET DEFAULT VERSION STRING
blender_version_str = (str(blender_version[0]) + ".x")
# GET USER
current_user = os.getlogin()
user_path = os.path.join("C:\\users",current_user)
# BASEFILE SPECIFIC 
thecam_name = "cam.ttCamera"
# DEADLINE COMMAND
deadlineBin = r"C:\Program Files\Thinkbox\Deadline10\bin\deadlinecommand.exe"
# OUTPUT PARAMETERS
frameRate = 23.976
thekeyframes_cam = [121,122,123]
# LAUNCHPAD
LAUNCHPAD_REPOSITORY_PATH = r"X:\projects\chums_season2\onsite\pipeline\repos\launchpadRepository"


# FUNCTIONS
def set_version_override_paths(self, context):
    if self.tt_override_version:
        match self.tt_override_version:
            case '3.x':
                self.tt_override_assetroot = "Y:/projects/CHUMS_Onsite/_prod/assets/"
                self.tt_override_filepath = "Y:/projects/CHUMS_Onsite/_prod/assets/helpers/turntable/projects/blender/turntable_331.blend"
                self.tt_override_basefile = "Y:/projects/CHUMS_Onsite/_prod/assets/helpers/basefiles/publish"
                self.tt_override_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
                self.tt_override_subtree = "projects/blender"
                self.tt_override_stage = 'workfiles'
            case '4.x':
                self.tt_override_assetroot = "X:/projects/chums_season2/onsite/_prod/assets/"
                self.tt_override_filepath = "X:/projects/chums_season2/onsite/_prod/assets/helpers/turntable/publish/blender/turntable.blend"
                self.tt_override_basefile = "X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish/"
                self.tt_override_renderroot = "X:/projects/chums_season2/onsite/renders/_prod/assets"
                self.tt_override_subtree = ""
                self.tt_override_stage = 'work'
            case "Custom":
                self.tt_override_assetroot = bpy.context.scene.tt_override_assetroot
                self.tt_override_filepath = bpy.context.scene.tt_override_filepath
                self.tt_override_basefile = bpy.context.scene.tt_override_basefile
                self.tt_override_renderroot = bpy.context.scene.tt_override_renderroot
                self.tt_override_subtree = bpy.context.scene.tt_override_subtree
                self.tt_override_stage = bpy.context.scene.tt_override_stage
            case _:
                self.tt_override_assetroot = "Y:/projects/CHUMS_Onsite/_prod/assets/"
                self.tt_override_filepath = "Y:/projects/CHUMS_Onsite/_prod/assets/helpers/turntable/projects/blender/turntable_331.blend"
                self.tt_override_basefile = "X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish"
                self.tt_override_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
                self.tt_override_subtree = "projects/blender"
                self.tt_override_stage = 'workfiles'
    return None

def update_prefs_assetroot(self, context):
    #print("\nself.tt_override_version:", self.tt_override_version)
    print("\nself.tt_override_version:", bpy.context.scene.tt_override_version)
    try:
        if self.tt_override_version == "Custom":
            bpy.context.scene.tt_override_assetroot = self.tt_override_assetroot
            print("self.tt_override_assetroot:", bpy.context.scene.tt_override_assetroot)
    except:
        print("fail to update prefs")
    
    return None

def update_prefs_filepath(self, context):
    print("\nself.tt_override_version:", self.tt_override_version)
    try:
        if self.tt_override_version == "Custom":
            bpy.context.scene.tt_override_filepath = self.tt_override_filepath
            print("self.tt_override_filepath:", self.tt_override_filepath)
    except:
        print("fail to update prefs")
    
    return None

def tt_override_basefile(self, context):
    print("\nself.tt_override_basefile:", self.tt_override_basefile)
    try:
        if self.tt_override_basefile == "Custom":
            bpy.context.scene.tt_override_basefile = self.tt_override_basefile
            print("self.tt_override_basefile:", self.tt_override_basefile)
    except:
        print("fail to update prefs")
    
    return None

def update_prefs_renderroot(self, context):
    print("\nself.tt_override_version:", self.tt_override_version)
    try:
        if self.tt_override_version == "Custom":
            bpy.context.scene.tt_override_renderroot = self.tt_override_renderroot
            print("self.tt_override_renderroot:", self.tt_override_renderroot)
    except:
        print("fail to update prefs")
    
    return None

def update_prefs_stage(self, context):
    print("\nself.tt_override_version:", self.tt_override_version)
    try:
        if self.tt_override_version == "Custom":
            bpy.context.scene.tt_override_stage = self.tt_override_stage
            print("self.tt_override_stage:", self.tt_override_stage)
    except:
        print("fail to update prefs")
    
    return None

def update_prefs_subtree(self, context):
    print("\nself.tt_override_version:", self.tt_override_version)
    try:
        if self.tt_override_subtree == "Custom":
            bpy.context.scene.tt_override_subtree = self.tt_override_subtree
            print("self.tt_override_subtree:", self.tt_override_subtree)
    except:
        print("fail to update update_prefs_subtree")
    
    return None

def make_path_absolute(self, context):
    if self.tt_tools_override_asset:
        if self.tt_tools_override_asset.startswith('//'):
            self.tt_tools_override_asset = (os.path.abspath(bpy.path.abspath(self.tt_tools_override_asset)))
    return None

# CLASSES
#   PREFERENCES
class tt_toolsPreferences(bpy.types.AddonPreferences):
    #bl_idname = "Turntable Tools"
    bl_idname = __name__

    tt_override_version: bpy.props.EnumProperty(
        name="Override Version",
        description="Override version defaults",
        items=[('3.x','3.x',''),('4.x','4.x',''),('Custom','Custom','')],
        update = set_version_override_paths,
        default = blender_version_str,
    )

    tt_override_basefile: bpy.props.StringProperty(
        name = "Project Base File",
        subtype = 'DIR_PATH',
        update = tt_override_basefile,
        default = "P:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish",
    )

    tt_override_assetroot: bpy.props.StringProperty(
        name = "Asset Root Directory",
        subtype = 'DIR_PATH',
        update = update_prefs_assetroot,
        default = 'Y:/projects/CHUMS_Onsite/_prod/assets/',
    )

    tt_override_filepath: bpy.props.StringProperty(
        name = "Turntable File",
        subtype = 'FILE_PATH',
        update = update_prefs_filepath,
        default = 'Path to Turntable File',
    )

    tt_override_renderroot: bpy.props.StringProperty(
        name="Output Directory",
        subtype = 'DIR_PATH',
        update = update_prefs_renderroot,
        default = 'Path to Render Root Folder',
    )

    tt_override_stage: bpy.props.StringProperty(
        name="Stage String",
        update = update_prefs_stage,
        default = "",
    )

    tt_override_subtree: bpy.props.StringProperty(
        name="Asset Subtree",
        subtype = 'DIR_PATH',
        update = update_prefs_subtree,
        default = "",
    )

    defaultangle: bpy.props.FloatProperty(
        name="Default Camera Parent Z Rotation",
        default=22.5,
    )

    defaultpriority: bpy.props.IntProperty(
        name="Default Deadline Priority",
        default=60,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "tt_override_version")
        layout.prop(self, "tt_override_assetroot")
        layout.prop(self, "tt_override_basefile")
        layout.prop(self, "tt_override_filepath")
        layout.prop(self, "tt_override_renderroot")
        layout.prop(self, "tt_override_subtree")
        layout.prop(self, "tt_override_stage")
        layout.prop(self, "defaultangle")
        layout.prop(self, "defaultpriority")

class OBJECT_OT_tt_tools_preferences(bpy.types.Operator):
    bl_idname = "object.tt_tools_preferences"
    bl_label = "Turntable Add-on Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons["Turntable Tools"].preferences

        info = ("")

        self.report({'INFO'}, info)
        print("info: ", info)

        return {'FINISHED'}

#   PROPERTIES
class tt_toolsProperties(bpy.types.PropertyGroup):
    bpy.types.Scene.tt_tools_assetname = bpy.props.StringProperty \
        (
        name = "Asset Name",
        description = "Asset Name",
        default = ""
        )
    bpy.types.Scene.tt_override_version = bpy.props.StringProperty \
        (
        name = "Version",
        description = "Version",
        default = "Custom"
        )
    bpy.types.Scene.tt_override_assetroot = bpy.props.StringProperty \
        (
        name = "Asset Root",
        description = "Asset Root",
        default = "Y:/projects/CHUMS_Onsite/_prod/assets/"
        )
    bpy.types.Scene.tt_override_basefile = bpy.props.StringProperty \
        (
        name = "Project Base File",
        description = "Project Base File",
        default = "X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish/"
        )
    bpy.types.Scene.tt_override_filepath = bpy.props.StringProperty \
        (
        name = "Turntable Base File",
        description = "Turntable Base File",
        default = "Y:/projects/CHUMS_Onsite/_prod/assets/helpers/turntable/projects/blender/turntable_410.blend"
        )
    bpy.types.Scene.tt_override_renderroot = bpy.props.StringProperty \
        (
        name = "Output Directory",
        description = "Output Directory",
        default = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
        )
    bpy.types.Scene.tt_override_subtree = bpy.props.StringProperty \
        (
        name = "Asset Subtree",
        description = "Asset Subtree",
        default = "projects/blender"
        )
    bpy.types.Scene.tt_override_stage = bpy.props.StringProperty \
        (
        name = "Stage",
        description = "Stage",
        default = "workfiles"
        )
    bpy.types.Scene.tt_tools_override_ttsave = bpy.props.StringProperty \
        (
        name = "",
        description = "Turntable Blender File Folder",
        default = ""
        )
    bpy.types.Scene.tt_tools_task = bpy.props.EnumProperty \
        (
        name="",
        description="Use latest model or texture version.",
        items=[ ('20_model', "Model", ""),
                ('30_texture', "Texture", "")
               ],
        default = "30_texture"
        )
    bpy.types.Scene.tt_tools_overscan = bpy.props.FloatProperty \
        (
        name = "Overscan %",
        description = "Percent of asset size to use as border",
        min = 0.00,
        max = 10000.0,
        step = 0.5,
        default = 20.0
        )
    bpy.types.Scene.tt_tools_newblend = bpy.props.BoolProperty \
        (
        name = "Force New Blender",
        description = "When opening assets or the turntable file with this enabled will launch a new Bledner session.",
        default = True
        )
    bpy.types.Scene.tt_tools_xcode = bpy.props.BoolProperty \
        (
        name = "Transcode",
        description = "Transcode H264.",
        default = True
        )
    bpy.types.Scene.tt_tools_draft = bpy.props.BoolProperty \
        (
        name = "Draft",
        description = "Deadline Draft.",
        default = False
        )
    bpy.types.Scene.tt_tools_alist = bpy.props.EnumProperty \
        (
        name="",
        description="Asset List",
        items=queryAssetList(),
        default = None
        )
    bpy.types.Scene.tt_tools_filter = bpy.props.StringProperty \
        (
        name = "Filter",
        description = "String to Isolate",
        default = ""
        )


#   REGISTER
classes = [tt_toolsPreferences,OBJECT_OT_tt_tools_preferences,
            tt_toolsProperties,VIEW3D_PT_tt_tools_panel,
            BUTTON_OT_set_cam_loc, BUTTON_OT_get_asset, 
            BUTTON_OT_openTT, BUTTON_OT_exploreAsset,
            BUTTON_OT_set_out_filepath, BUTTON_OT_save_ttfile,
            BUTTON_OT_tilt_cam, BUTTON_OT_selectTTcam,
            BUTTON_OT_openAsset, BUTTON_OT_submit_tt,
            BUTTON_OT_refresh, BUTTON_OT_append_asset,
            BUTTON_OT_link_asset, BUTTON_OT_buildTT]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

#   UNREGISTER
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    #chums_turntableAddon_050()
    chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
    if os.path.exists(chm_assetroot):
        chm_assettypes = ([f for f in os.listdir(chm_assetroot) if 
                    os.path.isdir(os.path.join(chm_assetroot, f))])
    register()
