# 0.4.7 - FEATURE - rebuild_turntable function - using basefile as starting point, then appending necessary (will require post load script write)

import bpy
import os
from pathlib import Path

from .chums_tt_addon import *
from .chums_tt_utils import *

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
LAUNCHPAD_REPOSITORY_PATH = r"X:\projects\chums_season2\onsite\pipeline\repos\launchpadRepository"


# FUNCTIONS
def set_version_override_paths(self, context):
    if self.tt_override_version:
        match self.tt_override_version:
            case '3.x':
                self.tt_override_assetroot = "Y:/projects/CHUMS_Onsite/_prod/assets/"
                self.tt_override_filepath = "Y:/projects/CHUMS_Onsite/_prod/assets/helpers/turntable/projects/blender/turntable_331.blend"
                self.tt_override_basefile = "X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish/basefile_v002.blend"
                self.tt_override_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
                self.tt_override_subtree = "projects/blender"
                self.tt_override_stage = 'workfiles'
            case '4.x':
                self.tt_override_assetroot = "X:/projects/chums_season2/onsite/_prod/assets/"
                self.tt_override_filepath = "X:/projects/chums_season2/onsite/_prod/assets/helpers/turntable/publish/blender/turntable_410.blend"
                self.tt_override_basefile = "X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish/basefile_v002.blend"
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
                self.tt_override_basefile = "X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish/basefile_v002.blend"
                self.tt_override_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
                self.tt_override_subtree = "projects/blender"
                self.tt_override_stage = 'workfiles'
    return None

def update_prefs_assetroot(self, context):
    print("\nself.tt_override_version:", self.tt_override_version)
    try:
        if self.tt_override_version == "Custom":
            bpy.context.scene.tt_override_assetroot = self.tt_override_assetroot
            print("self.tt_override_assetroot:", self.tt_override_assetroot)
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

def queryAssetList():
    #print("\nENTER queryAssetList FUNCTION")
    print("call update_base_settings from: queryAssetList")
    chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage, chm_tt_version = update_base_settings()
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

def update_base_settings(): #(chm_assetroot, chm_tt_basefile, chm_tt_filepath, chm_renderroot, chm_assetssubtree, chm_assetturntables, chm_tt_stage)
    try:
        override_version = bpy.context.preferences.addons[__name__].preferences.tt_override_version
        print("\nusing PREFERENCES")
        if override_version == "Custom":
            if len(bpy.context.preferences.addons[__name__].preferences.tt_override_assetroot) > 0:
                pref_assetroot = bpy.context.preferences.addons[__name__].preferences.tt_override_assetroot
                bpy.context.scene.tt_override_assetroot = pref_assetroot
            else:
                pref_assetroot = ""
                bpy.context.scene.tt_override_assetroot = pref_assetroot
            print("    pref_assetroot:", pref_assetroot)
                        
            if len(bpy.context.preferences.addons[__name__].preferences.tt_override_basefile) > 0:
                pref_basefile = bpy.context.preferences.addons[__name__].preferences.tt_override_basefile
                bpy.context.scene.tt_override_basefile = pref_basefile
            else:
                pref_basefile = 'Path to basefile'
                bpy.context.scene.tt_override_basefile = pref_basefile
            print("    pref_basefile:", pref_basefile)
            
            if len(bpy.context.preferences.addons[__name__].preferences.tt_override_filepath) > 0:
                pref_tt_filepath = bpy.context.preferences.addons[__name__].preferences.tt_override_filepath
                bpy.context.scene.tt_override_filepath = pref_tt_filepath
                print("    pref_tt_filepath:", pref_tt_filepath)
            else:
                pref_tt_filepath = ""
                bpy.context.scene.tt_override_filepath = pref_tt_filepath
            
            if len(bpy.context.preferences.addons[__name__].preferences.tt_override_renderroot) > 0:
                pref_renderroot = bpy.context.preferences.addons[__name__].preferences.tt_override_renderroot
                bpy.context.scene.tt_override_renderroot = pref_renderroot
                print("    pref_renderroot:", pref_renderroot)
            else:
                pref_renderroot = ""
                bpy.context.scene.tt_override_filepath = pref_renderroot
            
            if len(bpy.context.preferences.addons[__name__].preferences.tt_override_subtree) > 0:
                pref_assetssubtree = bpy.context.preferences.addons[__name__].preferences.tt_override_subtree
                bpy.context.scene.tt_override_subtree = pref_assetssubtree
                print("    pref_renderroot:", pref_assetssubtree)
            else:
                pref_assetssubtree = ""
                bpy.context.scene.tt_override_subtree = pref_assetssubtree
            
            if len(bpy.context.preferences.addons[__name__].preferences.tt_override_stage) > 0:
                pref_tt_stage = bpy.context.preferences.addons[__name__].preferences.tt_override_stage
                bpy.context.scene.tt_override_stage = pref_tt_stage
                print("    pref_renderroot:", pref_tt_stage)
            else:
                pref_tt_stage = ""
                bpy.context.scene.tt_override_stage = pref_tt_stage
    except:
        print("FROM DEFAULTS")
        override_version = (str(blender_version[0]) + ".x")
    print("override_version:", override_version)
    match blender_version_str:
        case '3.x':
            pref_assetroot = "Y:/projects/CHUMS_Onsite/_prod/assets/"
            pref_tt_filepath = Path(str(pref_assetroot + "helpers/turntable/projects/blender/turntable_331.blend"))
            pref_basefile = 'Path to Base File'
            pref_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
            pref_assetssubtree = "projects/blender"
            pref_assetturntables = "/projects/blender/turntables"
            pref_tt_stage = 'workfiles'
        case '4.x':
            pref_assetroot = "X:/projects/chums_season2/onsite/_prod/assets"
            pref_tt_filepath = Path(str(pref_assetroot + "/helpers/turntable/publish/blender/turntable_410.blend"))
            pref_basefile = 'X:/projects/chums_season2/onsite/_prod/assets/helpers/basefiles/publish/basefile_v002.blend'
            pref_renderroot = "X:/projects/chums_season2/onsite/renders/_prod/assets"
            pref_assetssubtree = "blender"
            pref_assetturntables = "turntables"
            pref_tt_stage = 'work'
        case _:
            pref_assetroot = "Y:/projects/CHUMS_Onsite/_prod/assets/"
            pref_tt_filepath = Path(str(pref_assetroot + "helpers/turntable/projects/blender/turntable_331.blend"))
            pref_basefile = 'Path to Base File'
            pref_renderroot = "Y:/projects/CHUMS_Onsite/renders/_prod/assets/"
            pref_assetssubtree = "projects/blender"
            pref_assetturntables = "/projects/blender/turntables"
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
            if len(bpy.context.scene.tt_override_stage) > 0:
                pref_tt_stage = bpy.context.scene.tt_override_stage
            if len(bpy.context.scene.tt_override_subtree) > 0:
                pref_assetssubtree = bpy.context.scene.tt_override_subtree
        
    pref_override_version = override_version
    
    print("\npref_assetroot:", pref_assetroot, "\npref_basefile:", pref_basefile, "\npref_tt_filepath:", pref_tt_filepath, "\npref_renderroot:", pref_renderroot)
    return (pref_assetroot, pref_basefile, pref_tt_filepath, pref_renderroot, pref_assetssubtree, pref_assetturntables, pref_tt_stage, pref_override_version)


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
        default = "Path to Base File",
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
        default = "Path to basefile"
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
