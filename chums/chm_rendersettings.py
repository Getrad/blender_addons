######################## NOTES ##############################
# v0.0.1 - first pass at addon to save render settings
# v0.0.2
# v0.0.4 - add call to script that saves new version which is ignored by UI code
# v0.0.5 - removed direct pyton settings file run to avoid having unexpected saves/closures
# v0.0.6 - revert back to settings file execute approach to loading

bl_info = {
    "name": "Render Settings",
    "author": "Conrad Dueck",
    "version": (0,1,0),
    "blender": (3, 3, 1),
    "location": "View3D > Tool Shelf > Chums",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}


import bpy
import os
from pathlib import Path

# GLOBAL VARIABLES
vsn = '0.1.0'
ONSITE_ROOT_DIR = "Y:/projects/CHUMS_Onsite"
RENDER_SETTINS_FILENAME = "rendersettings_v001.py"

zeroRenderSettings = {
    'bpy.context.scene.world.light_settings.ao_factor': 1.0,
    'bpy.context.scene.world.light_settings.distance': 0.5,
    'bpy.context.scene.node_tree.chunk_size': '64',
    'bpy.context.scene.node_tree.use_opencl': False,
    'bpy.context.scene.render.use_motion_blur': True,
    'bpy.context.scene.render.motion_blur_shutter': 0.5,
    'bpy.context.scene.cycles.adaptive_threshold': 0.014999999664723873,
    'bpy.context.scene.cycles.caustics_reflective': 0,
    'bpy.context.scene.cycles.caustics_refractive': 0,
    'bpy.context.scene.cycles.device': 'GPU',
    'bpy.context.scene.cycles.diffuse_bounces': 4,
    'bpy.context.scene.cycles.glossy_bounces': 2,
    'bpy.context.scene.cycles.max_bounces': 12,
    'bpy.context.scene.cycles.preview_adaptive_threshold': 0.019999999552965164,
    'bpy.context.scene.cycles.preview_samples': 256,
    'bpy.context.scene.cycles.sample_clamp_indirect': 20.0,
    'bpy.context.scene.cycles.samples': 1024,
    'bpy.context.scene.cycles.transmission_bounces': 3,
    'bpy.context.scene.cycles.transparent_max_bounces': 2,
    'bpy.context.scene.cycles.use_auto_tile': 0,
    'bpy.context.scene.cycles.use_denoising': 0,
    'bpy.context.scene.cycles.use_fast_gi': 0,
    'bpy.context.scene.cycles.film_exposure': 1.0,
    'bpy.context.scene.view_settings.exposure': 1.0,
    'bpy.context.scene.cycles.sample_clamp_direct': 0.0,
    'bpy.context.scene.cycles.use_adaptive_sampling': True,
    'bpy.context.scene.render.use_persistent_data': True
}
all_render_passes = [
    'use_pass_ambient_occlusion', 
    'use_pass_combined', 
    'use_pass_cryptomatte_accurate', 
    'use_pass_cryptomatte_asset', 
    'use_pass_cryptomatte_material', 
    'use_pass_cryptomatte_object',
    'use_pass_diffuse_color',
    'use_pass_diffuse_direct',
    'use_pass_diffuse_indirect',
    'use_pass_emit',
    'use_pass_environment',
    'use_pass_glossy_color',
    'use_pass_glossy_direct',
    'use_pass_glossy_indirect',
    'use_pass_material_index',
    'use_pass_mist',
    'use_pass_normal',
    'use_pass_object_index',
    'use_pass_position',
    'use_pass_shadow',
    'use_pass_subsurface_color',
    'use_pass_subsurface_direct',
    'use_pass_subsurface_indirect',
    'use_pass_transmission_color',
    'use_pass_transmission_direct',
    'use_pass_transmission_indirect',
    'use_pass_uv',
    'use_pass_vector',
    'use_pass_z'
]
view_layer_passes = {}

# FUNCTIONS
# convert paths to absolute
def make_path_absolute(self, context):
    if self.rs_output:
        if self.rs_output.startswith('//'):
            self.rs_output = (os.path.abspath(bpy.path.abspath(self.rs_output)))
    return None

# entity breakdown; return element list
def breakdownEntityName(entityName):
    parts = entityName.split("_")
    keys = ['projName', 'epNo', 'seqNo', 'shotNo', 'lang', 'vNo']
    values = [parts[i] if len(parts) > i and parts[i] else None for i in range(len(keys))]
    return {k: v for k, v in zip(keys, values) if v is not None}

# collect zero path hierarchy; return 3 items
def get_zero_paths(entityName):
    e = breakdownEntityName(entityName)
    zeroShotPath = Path(ONSITE_ROOT_DIR).joinpath("_prod", "shots",
        f"{e['projName']}_{e['epNo']}",
        f"{e['projName']}_{e['epNo']}_{e['seqNo']}",
        f"{e['projName']}_{e['epNo']}_{e['seqNo']}_sh000",
        "publish")
    zeroScenePath = Path(ONSITE_ROOT_DIR).joinpath("_prod", "shots",
        f"{e['projName']}_{e['epNo']}",
        f"{e['projName']}_{e['epNo']}_sc00")
    zeroEpisodePath = Path(ONSITE_ROOT_DIR).joinpath("_prod", "shots",
        f"{e['projName']}_ep000",
        "publish")
    return zeroShotPath, zeroScenePath, zeroEpisodePath

# update zeroRenderSettings
def set_zeroRenderSettings_dict(zeroRenderSettings, newSettingsPath):
    if len(newSettingsPath) >= 0 and newSettingsPath.endswith(".py"):
        thesettingsfile = open(newSettingsPath, "r")
        if thesettingsfile:
            for line in thesettingsfile.readlines():
                linebits = line.split(" = ")
                if len(linebits)>=2:
                    if linebits[0] in zeroRenderSettings.keys():
                        zeroRenderSettings[linebits[0]] = linebits[1]
        thesettingsfile.close()
    return zeroRenderSettings

# collect view layer render passes
def collect_render_passes(all_render_passes):
    view_layers_passes = {}
    for vl in bpy.context.scene.view_layers:
        for thepass in all_render_passes:
            thispass = ("bpy.context.scene.view_layers["+vl.name+"]."+thepass)
            if vl.name in view_layers_passes.keys():
                view_layers_passes[vl.name].append(eval(thispass))
            else:
                view_layers_passes[vl.name] = [eval(thispass)]
    print(view_layers_passes)
    return view_layers_passes


# CLASSES
# PROPERTY GROUP renderSettingsProperties
class renderSettingsProperties(bpy.types.PropertyGroup):
    bpy.types.Scene.rs_world = bpy.props.StringProperty(
        default = ("bpy.context.scene.world.light_settings.ao_factor,bpy.context.scene.world.light_settings.distance")
        )
    bpy.types.Scene.rs_node_tree = bpy.props.StringProperty(
        default = ("bpy.context.scene.node_tree.chunk_size,bpy.context.scene.node_tree.use_opencl")
        )
    bpy.types.Scene.rs_view_layer = bpy.props.StringProperty(
        default = ("bpy.context.scene.view_settings.exposure")
        )
    bpy.types.Scene.rs_render = bpy.props.StringProperty(
        default = ("bpy.context.scene.render.engine,bpy.context.scene.render.use_motion_blur,bpy.context.scene.render.motion_blur_shutter,bpy.context.scene.render.use_persistent_data")
        )
    bpy.types.Scene.rs_cycles = bpy.props.StringProperty(
        default = ("bpy.context.scene.cycles.use_animated_seed,bpy.context.scene.cycles.adaptive_threshold,bpy.context.scene.cycles.caustics_refractive,bpy.context.scene.cycles.caustics_reflective,bpy.context.scene.cycles.device,bpy.context.scene.cycles.diffuse_bounces,bpy.context.scene.cycles.glossy_bounces,bpy.context.scene.cycles.max_bounces,bpy.context.scene.cycles.preview_adaptive_threshold,bpy.context.scene.cycles.preview_samples,bpy.context.scene.cycles.sample_clamp_indirect,bpy.context.scene.cycles.samples,bpy.context.scene.cycles.transmission_bounces,bpy.context.scene.cycles.transparent_max_bounces,bpy.context.scene.cycles.use_auto_tile,bpy.context.scene.cycles.use_denoising,bpy.context.scene.cycles.use_fast_gi,bpy.context.scene.cycles.film_exposure,bpy.context.scene.cycles.sample_clamp_direct,bpy.context.scene.cycles.use_adaptive_sampling,")
        )
    bpy.types.Scene.rs_passes = bpy.props.StringProperty(
        default = ("use_pass_ambient_occlusion,use_pass_combined,use_pass_cryptomatte_accurate,use_pass_cryptomatte_asset,use_pass_cryptomatte_material,use_pass_cryptomatte_object,use_pass_diffuse_color,use_pass_diffuse_direct,use_pass_diffuse_indirect,use_pass_emit,use_pass_environment,use_pass_glossy_color,use_pass_glossy_direct,use_pass_glossy_indirect,use_pass_material_index,use_pass_mist,use_pass_normal,use_pass_object_index,use_pass_position,use_pass_shadow,use_pass_subsurface_color,use_pass_subsurface_direct,use_pass_subsurface_indirect,use_pass_transmission_color,use_pass_transmission_direct,use_pass_transmission_indirect,use_pass_uv,use_pass_vector,use_pass_z")
        )
    bpy.types.Scene.rs_load_override = bpy.props.BoolProperty \
        (
          name = "Custom Load",
          description = "Override default Zero shot",
          default = True
        )
    bpy.types.Scene.rs_save_override = bpy.props.BoolProperty \
        (
          name = "Custom Save",
          description = "Override default Zero shot",
          default = True
        )
    bpy.types.Scene.rs_output = bpy.props.StringProperty(
        name="Save Path:",
        description="Settings Save Path",
        default="",
        maxlen=1024,
        update = make_path_absolute,
        subtype='FILE_PATH')
    bpy.types.Scene.rs_input = bpy.props.StringProperty(
        name="Load Path:",
        description="Settings Load Path",
        default="",
        maxlen=1024,
        update = make_path_absolute,
        subtype='FILE_PATH')


# OPERATOR BUTTON_OT_rssave
class BUTTON_OT_rssave(bpy.types.Operator):
    '''Save render settings.'''
    bl_idname = "rendersettings.rssave"
    bl_label = "Save"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("************  START SAVE ************")
        entityName_get = os.path.basename(bpy.data.filepath).split(".")[0]
        rs_settings = bpy.context.scene.rs_world.split(",")
        for a in bpy.context.scene.rs_node_tree.split(","): rs_settings.append(a)
        for a in bpy.context.scene.rs_render.split(","): rs_settings.append(a)
        for a in bpy.context.scene.rs_cycles.split(","): rs_settings.append(a)
        for a in bpy.context.scene.rs_view_layer.split(","): rs_settings.append(a)
        rs_passes = bpy.context.scene.rs_passes.split(",")
        all_render_passes = [
            'use_pass_ambient_occlusion', 
            'use_pass_combined', 
            'use_pass_cryptomatte_accurate', 
            'use_pass_cryptomatte_asset', 
            'use_pass_cryptomatte_material', 
            'use_pass_cryptomatte_object',
            'use_pass_diffuse_color',
            'use_pass_diffuse_direct',
            'use_pass_diffuse_indirect',
            'use_pass_emit',
            'use_pass_environment',
            'use_pass_glossy_color',
            'use_pass_glossy_direct',
            'use_pass_glossy_indirect',
            'use_pass_material_index',
            'use_pass_mist',
            'use_pass_normal',
            'use_pass_object_index',
            'use_pass_position',
            'use_pass_shadow',
            'use_pass_subsurface_color',
            'use_pass_subsurface_direct',
            'use_pass_subsurface_indirect',
            'use_pass_transmission_color',
            'use_pass_transmission_direct',
            'use_pass_transmission_indirect',
            'use_pass_uv',
            'use_pass_vector',
            'use_pass_z'
        ]
        newzeroRenderSettings = {}
        thefiletext = "import bpy"
        thefiletext += "\nbpy.ops.file.make_paths_absolute()"
        thefiletext += "\nbpy.context.preferences.filepaths.use_relative_paths = False"
        for setting in rs_settings:
            if len(setting) >= 1:
                thevalue = eval(setting)
                if thevalue in ["GPU", "64", "CYCLES"]:
                    thecmd = (setting + " = \'" + str(thevalue) + "\'")
                else:
                    thecmd = (setting + " = " + str(thevalue))
                thefiletext += ("\n" + thecmd)
                print("thecmd:", thecmd)
        for vl in bpy.context.scene.view_layers:
            print("vl.name = ", vl.name)
            for thepass in rs_passes:
                thispass = ("bpy.context.scene.view_layers[\""+vl.name+"\"]."+thepass)
                thispassvalue = eval(thispass)
                thefiletext += ("\n" + thispass + " = " + str(thispassvalue))
        if bpy.context.scene.rs_save_override and len(bpy.context.scene.rs_output) > 0 and bpy.context.scene.rs_output.endswith(".py"):
            thesettingsfile = open(bpy.context.scene.rs_output, "w")
        else:
            thisShotDir = os.path.dirname(bpy.data.filepath)
            thisShotRenderSettings = os.path.join(thisShotDir, RENDER_SETTINS_FILENAME)
            thesettingsfile = open(thisShotRenderSettings, "w")
        print("thesettingsfile: ", thesettingsfile)
        zeroRenderSettings = newzeroRenderSettings
        thesettingsfile.write(thefiletext)
        thesettingsfile.close()
        print("************  DONE SAVE ************")
        return{'FINISHED'}

# OPERATOR BUTTON_OT_rsload
class BUTTON_OT_rsload(bpy.types.Operator):
    '''Load render settings.'''
    bl_idname = "rendersettings.rsload"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("************  START LOAD ************")
        entityName_get = os.path.basename(bpy.data.filepath).split(".")[0]
        zeroRenderSettings = {
            'bpy.context.scene.world.light_settings.ao_factor': 1.0,
            'bpy.context.scene.world.light_settings.distance': 0.5,
            'bpy.context.scene.node_tree.chunk_size': '64',
            'bpy.context.scene.node_tree.use_opencl': False,
            'bpy.context.scene.render.use_motion_blur': True,
            'bpy.context.scene.render.motion_blur_shutter': 0.5,
            'bpy.context.scene.cycles.adaptive_threshold': 0.014999999664723873,
            'bpy.context.scene.cycles.caustics_reflective': 0,
            'bpy.context.scene.cycles.caustics_refractive': 0,
            'bpy.context.scene.cycles.device': 'GPU',
            'bpy.context.scene.cycles.diffuse_bounces': 4,
            'bpy.context.scene.cycles.glossy_bounces': 2,
            'bpy.context.scene.cycles.max_bounces': 12,
            'bpy.context.scene.cycles.preview_adaptive_threshold': 0.019999999552965164,
            'bpy.context.scene.cycles.preview_samples': 256,
            'bpy.context.scene.cycles.sample_clamp_indirect': 20.0,
            'bpy.context.scene.cycles.samples': 1024,
            'bpy.context.scene.cycles.transmission_bounces': 3,
            'bpy.context.scene.cycles.transparent_max_bounces': 2,
            'bpy.context.scene.cycles.use_auto_tile': 0,
            'bpy.context.scene.cycles.use_denoising': 0,
            'bpy.context.scene.cycles.use_fast_gi': 0,
            'bpy.context.scene.cycles.film_exposure': 1.0,
            'bpy.context.scene.view_settings.exposure': 1.0,
            'bpy.context.scene.cycles.sample_clamp_direct': 0.0,
            'bpy.context.scene.cycles.use_adaptive_sampling': True,
            'bpy.context.scene.render.use_persistent_data': True
        }
        thesettingsfile = ""
        #look for the render settings python file
        if bpy.context.scene.rs_load_override and len(bpy.context.scene.rs_input)>0 and bpy.context.scene.rs_input.endswith(".py"):
            if bpy.context.scene.rs_load_override and len(bpy.context.scene.rs_input) > 0 and bpy.context.scene.rs_input.endswith(".py"):
                thesettingspath = bpy.context.scene.rs_input
        else:
            zeroShotDir, zeroSceneDir, zeroEpisodeDir = get_zero_paths(entityName_get)
            thisShotDir = os.path.dirname(bpy.data.filepath)
            thisShotRenderSettings = os.path.join(thisShotDir, RENDER_SETTINS_FILENAME)
            zeroShotRenderSettings = os.path.join(zeroShotDir, RENDER_SETTINS_FILENAME)
            zeroSceneRenderSettings = os.path.join(zeroSceneDir, RENDER_SETTINS_FILENAME)
            zeroEpisodeRenderSettings = os.path.join(zeroEpisodeDir, RENDER_SETTINS_FILENAME)
            if os.path.exists(thisShotRenderSettings):
                thesettingspath = thisShotRenderSettings
            elif os.path.exists(zeroShotRenderSettings):
                print("FAIL TO FIND LOCAL SHOT SETTINGS FILE: ", zeroShotRenderSettings)
                thesettingspath = zeroShotRenderSettings
            elif os.path.exists(zeroSceneRenderSettings):
                print("FAIL TO FIND ZERO SHOT SETTINGS FILE: ", zeroShotRenderSettings)
                thesettingspath = zeroSceneRenderSettings
            elif os.path.exists(zeroEpisodeRenderSettings):
                print("FAIL TO FIND ZERO SCENE SETTINGS FILE: ", zeroSceneRenderSettings)
                thesettingspath = zeroEpisodeRenderSettings
            else:
                thesettingspath = ""
                print("FAIL TO FIND ANY SETTINGS FILE")
        if len(thesettingspath) >= 0 and thesettingspath.endswith(".py"):
            thesettingsfile = open(thesettingspath, "r")
            if thesettingsfile:
                print("thesettingspath: ", thesettingspath)
                for line in thesettingsfile.readlines():
                    try:
                        exec(line)
                    except:
                        print("FAILED TO EVALUATE: ", line)
                #exec(compile(thesettingsfile.read(), thesettingspath, 'exec'))
            thesettingsfile.close()
            zeroRenderSettings = set_zeroRenderSettings_dict(zeroRenderSettings, thesettingspath)
        else:
            print("FAIL TO LOAD!!")
        #print("zeroRenderSettings: ", zeroRenderSettings)    
        print("************  DONE LOAD ************")
        return{'FINISHED'}
   
# PANEL VIEW3D_PT_rspanel
class VIEW3D_PT_rspanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Render Settings "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(bpy.context.scene, "rs_save_override")
        layout.prop(bpy.context.scene, "rs_output")
        layout.operator("rendersettings.rssave", text=(BUTTON_OT_rssave.bl_label))
        layout.prop(bpy.context.scene, "rs_load_override")
        layout.prop(bpy.context.scene, "rs_input")
        layout.operator("rendersettings.rsload", text=(BUTTON_OT_rsload.bl_label))
        


# REGISTER
classes = [ renderSettingsProperties, 
           BUTTON_OT_rssave, BUTTON_OT_rsload, 
           VIEW3D_PT_rspanel ]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


# UNREGISTER
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
