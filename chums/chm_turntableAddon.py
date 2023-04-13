# ----------------------- NOTES -----------------------
# v0.0.1
# first pass of manual UI based turntable setup
# 0.0.4 - fixes output path to go into _prod folder
# 0.0.5 - adds dropdown for choosing latest workfile vs publish
# 0.0.8 - adds camera select button

bl_info = {
    "name": "TurnTable Tools",
    "author": "Conrad Dueck",
    "version": (0, 0, 8),
    "blender": (3, 31, 0),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Turntable Convenience Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

# ---    GLOBAL IMPORTS    ----
import bpy
import os
import math
import shutil

# ---    GLOBAL VARIABLES    ----
chm_assettypes = ['characters', 'environments', 'props', 'proxies']
chm_assetroot = 'Y:/projects/CHUMS_Onsite/_prod/assets/'
chm_renderroot = 'Y:/projects/CHUMS_Onsite/renders/_prod/assets/'
chm_assetssubtree = '30_texture/projects/blender'
chm_assetturntables = '30_texture/projects/blender/turntables'
thecam_name = "cam.ttCamera"
turntable_filepath = "Y:/projects/CHUMS_Onsite/_prod/assets/helpers/turntable/projects/blender/turntable.blend"
vsn = '0.0.8'


def get_selection_bounds(thesel):
    print("\nENTER get_selection_bounds FUNCTION")
    from mathutils import Vector
    themin = [0.0, 0.0, 0.0]
    themax = [0.0, 0.0, 0.0]
    for theobj in thesel:
        thematrix = theobj.matrix_world
        if theobj.type == 'MESH':
            if len(theobj.data.vertices) >= 1:
                for vertex in theobj.data.vertices:
                    theloc = thematrix @ vertex.co
                    if theloc[0] > themax[0]:
                        themax[0] = theloc[0]
                    if theloc[0] < themin[0]:
                        themin[0] = theloc[0]
                    if theloc[1] > themax[1]:
                        themax[1] = theloc[1]
                    if theloc[1] < themin[1]:
                        themin[1] = theloc[1]
                    if theloc[2] > themax[2]:
                        themax[2] = theloc[2]
                    if theloc[2] < themin[2]:
                        themin[2] = theloc[2]
            else:
                for vertex in theobj.bound_box:
                    theloc = thematrix @ Vector((vertex[0], vertex[1], vertex[2]))
                    if theloc[0] > themax[0]:
                        themax[0] = theloc[0]
                    if theloc[0] < themin[0]:
                        themin[0] = theloc[0]
                    if theloc[1] > themax[1]:
                        themax[1] = theloc[1]
                    if theloc[1] < themin[1]:
                        themin[1] = theloc[1]
                    if theloc[2] > themax[2]:
                        themax[2] = theloc[2]
                    if theloc[2] < themin[2]:
                        themin[2] = theloc[2]
    thesize = [(themax[0]-themin[0]), (themax[1]-themin[1]), (themax[2]-themin[2])]
    thecenter = ([themin[0]+(thesize[0]/2), 
                  themin[1]+(thesize[1]/2), 
                  themin[2]+(thesize[2]/2)])
    print("size [0]", str(thesize))
    print("center [1]", str(thecenter))
    
    return thesize, thecenter


def get_local_asset_objects():
    print("\nENTER get_local_asset_objects FUNCTION")
    object_list = []
    for col in bpy.data.collections:
        if col.name == "asset_prod":
            print("FOUND: ", col.name)
            asset_col = col
            for obj in asset_col.all_objects:
                if not(obj in object_list):
                    object_list.append(obj)
                if obj.type == 'EMPTY' and len(obj.children) >= 1:
                    for chobj in obj.children:
                        if not(obj in object_list):
                            object_list.append(obj)
    return object_list


def remove_any_existing_asset():
    # asumee all objects in collection "asset_prod" are to be removed as well as the collection itself
    for col in bpy.data.collections:
        if col.name == "asset_prod":
            for obj in col.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)
    return 0


def find_latest_workfile(input_path):
    #print("ENTER find_latest_workfile FUNCTION")
    latest_filepath = ""
    vNo = 0
    for f in os.listdir(input_path):
        this_path = os.path.join(input_path, f)
        if this_path.endswith(".blend") and (this_path[-10] == "v"):
            #print("this_path: ", this_path)
            if os.path.isfile(this_path):
                str_version = (f.split(".")[0][-3:])
                #print("str_version: ", str_version)
                this_version = int(str_version)
                if this_version > vNo:
                    vNo = this_version
                    latest_filepath = this_path
    return latest_filepath


def get_asset(asset_name, asset_stage):
    print("ENTER get_asset FUNCTION", asset_name)
    remove_any_existing_asset()
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    the_asset_type = chm_assetprefix[asset_name[:3]]
    the_asset_dir = os.path.join(chm_assetroot,the_asset_type,asset_name,chm_assetssubtree,asset_stage)
    the_asset_path = find_latest_workfile(the_asset_dir)
    # LINK FROM LATEST WORKFILE
    # initialize
    with bpy.data.libraries.load(the_asset_path, link=False) as (data_src, data_dst):
        data_dst.collections = data_src.collections
    # link collections
    for coll in data_dst.collections:
        the_topnodes = []
        if coll.name == "asset_prod":
            bpy.context.scene.collection.children.link(coll)
        for colobj in coll.all_objects:
            if not(colobj.parent):
                colobj.parent = bpy.data.objects['AnimGrp.asset']
    return 0


def get_asset_list(asset_stage):
    asset_list = []
    for asset_type in chm_assettypes:
        asset_type_path = (os.path.join(chm_assetroot,asset_type))
        assets = [o for o in os.listdir(asset_type_path) if (not(o[-3:] == "zip") and not("_AAA" in o) and not(o == ".DS_Store"))]
        for asset in assets:
            # find the asset blender folder
            this_asset_path = os.path.join(asset_type_path,asset,chm_assetssubtree,asset_stage)
            this_latest_filepath = find_latest_workfile(this_asset_path)
            if len(this_latest_filepath) > 0:
                asset_list.append((asset,asset,""))

    return asset_list


def open_turntable():
    bpy.ops.wm.open_mainfile(filepath=turntable_filepath)


def set_output_path(asset_name, asset_stage):
    #new goal: Y:\projects\CHUMS_Onsite\renders\assets\<asset type>\<asset name>\<v###>
    the_outpath = ""
    vNo = 0
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    the_outpath_base = os.path.join(chm_renderroot, 
                                asset_type,
                                asset_name)
    the_workpath = os.path.join(chm_assetroot, 
                                asset_type,
                                asset_name, 
                                chm_assetssubtree,
                                asset_stage)
    print("the_outpath_base: ", the_outpath_base)
    latest_asset_workfile = find_latest_workfile(the_workpath)
    print("latest_asset_workfile: ", latest_asset_workfile)
    latest_asset_version = latest_asset_workfile.split(".")[-2][-4:]
    latest_asset_filename = os.path.basename(latest_asset_workfile)
    the_outpath_base = os.path.join(the_outpath_base, latest_asset_version)
    if not(os.path.exists(the_outpath_base)):
        os.makedirs(the_outpath_base)
    outname = latest_asset_filename.replace(".blend",".####.png")
    the_outpath = os.path.join(the_outpath_base, outname)
    print("outpath: ", the_outpath)
    return the_outpath


def clean_up_after_blender_save(save_path):
    the_garbage_dir = save_path.replace("_tt.blend",("_tt_blend"))
    if os.path.exists(the_garbage_dir) and os.path.isdir(the_garbage_dir):
        shutil.rmtree(the_garbage_dir)
    the_garbage_file_1 = save_path.replace(".blend",(".blend1"))
    if os.path.exists(the_garbage_file_1) and os.path.isfile(the_garbage_file_1):
        os.remove(the_garbage_file_1)
    if os.path.exists(the_garbage_file_1) and os.path.isdir(the_garbage_file_1):
        shutil.rmtree(the_garbage_file_1)
    the_garbage_file_2 = save_path.replace(".blend",(".blend@"))
    if os.path.exists(the_garbage_file_2) and os.path.isfile(the_garbage_file_2):
        os.remove(the_garbage_file_2)
    return 0


def save_tt_file(asset_name, asset_stage):
    the_outpath = ""
    vNo = 0
    chm_assetprefix = {'chr':'characters', 
                       'env':'environments', 
                       'prp':'props', 
                       'prx':'proxies'}
    asset_type = chm_assetprefix[asset_name[:3]]
    the_workpath = os.path.join(chm_assetroot, 
                                asset_type,
                                asset_name, 
                                chm_assetssubtree,
                                asset_stage)
    latest_asset_workfile = find_latest_workfile(the_workpath)
    the_outpath = latest_asset_workfile.replace("workfiles", "turntables")
    the_outpath = the_outpath.replace("publish", "turntables")
    the_outpath = the_outpath.replace(".blend",("_tt.blend"))
    if not(os.path.exists(the_outpath)):
        os.makedirs(the_outpath)
    clean_up_after_blender_save(the_outpath)
    bpy.ops.wm.save_as_mainfile(filepath=the_outpath)
    clean_up_after_blender_save(the_outpath)
    return the_outpath


# PROPERTY GROUP ttutilsProperties
class ttutilsProperties(bpy.types.PropertyGroup):
    bpy.types.Scene.assetname = bpy.props.StringProperty \
        (
          name = "Asset Name",
          description = "Asset Name",
          default = ""
        )
    bpy.types.Scene.ttutils_stage = bpy.props.EnumProperty(
        name="",
        description="Use latest publish or workfiles version.",
        items=[ ('publish', "Publish", ""),
                ('workfiles', "Workfiles", "")
               ],
        default = "workfiles"
        )
    bpy.types.Scene.ttutils_custom = bpy.props.StringProperty(
        name="Custom:",
        description="",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
    bpy.types.Scene.ttutils_overscan = bpy.props.FloatProperty \
        (
          name = "Overscan %",
          description = "Percent of asset size to use as border",
          min = 0.00,
          max = 100.0,
          step = 0.5,
          default = 20.0
        )
    

# OPERATOR BUTTON_OT_openTT
class BUTTON_OT_openTT(bpy.types.Operator):
    '''Open Turntable Basefile.'''
    bl_idname = "ttutils.opentt"
    bl_label = "Open Turntable"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        open_turntable()
        return{'FINISHED'}

# OPERATOR BUTTON_OT_selectTTcam
class BUTTON_OT_selectTTcam(bpy.types.Operator):
    '''Select turntable camera object.'''
    bl_idname = "ttutils.selectttcam"
    bl_label = "Select Camera Object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            for o in bpy.context.selected_objects:
                o.select_set(False)
            thecam = bpy.data.objects['cam.ttCamera']
            thecam.select_set(True)
            bpy.context.view_layer.objects.active = thecam
        except:
            print("FAILED TO FIND cam.ttCamera")
        return{'FINISHED'}

# OPERATOR BUTTON_OT_set_out_filepath
class BUTTON_OT_set_out_filepath(bpy.types.Operator):
    '''Set Output path.'''
    bl_idname = "ttutils.set_out_filepath"
    bl_label = "Set Output"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        assetname = bpy.context.scene.assetname
        theoutpath = set_output_path(assetname, bpy.context.scene.ttutils_stage)
        print("theoutpath: ", theoutpath)
        bpy.context.scene.render.filepath = theoutpath
        return{'FINISHED'}

# OPERATOR BUTTON_OT_set_cam_loc
class BUTTON_OT_set_cam_loc(bpy.types.Operator):
    '''Set Camera distance from asset.'''
    bl_idname = "ttutils.set_cam_loc"
    bl_label = "Set Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE set_cam_loc OPERATOR")
        if thecam_name in bpy.data.objects:
            thecam = bpy.data.objects[thecam_name]
            theasset_objects = get_local_asset_objects()
            theasset_size = (get_selection_bounds(theasset_objects))
            theasset_max = 0
            for theasset_dim in theasset_size[0]:
                if theasset_dim >= theasset_max:
                    theasset_max = theasset_dim
            thecam.location.z = (((theasset_max/2.0)*(1.0+((2*bpy.context.scene.ttutils_overscan)/100.0)))/math.tan((bpy.context.scene.camera.data.angle)/2))
            if bpy.data.objects['Ruler']:
                bpy.data.objects['Ruler'].location.y = ((theasset_size[0][1]/2)*(-1.0 - (bpy.context.scene.ttutils_overscan/100.0)))
            thecam.parent.location.z = (theasset_size[1][2])
        return{'FINISHED'}

# OPERATOR BUTTON_OT_get_asset
class BUTTON_OT_get_asset(bpy.types.Operator):
    '''Append the asset_prod collection from the latest asset'''
    bl_idname = "ttutils.get_asset"
    bl_label = "Get Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE BUTTON_OT_get_asset OPERATOR CLASS")
        asset_name = bpy.context.scene.assetname
        get_asset(asset_name, bpy.context.scene.ttutils_stage)
        return{'FINISHED'}

# OPERATOR BUTTON_OT_get_asset_list
class BUTTON_OT_get_asset_list(bpy.types.Operator):
    '''Return the latest asset - see console'''
    bl_idname = "ttutils.get_asset_list"
    bl_label = "Get Asset List"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE BUTTON_OT_get_asset_list OPERATOR CLASS")
        the_asset_list = get_asset_list(bpy.context.scene.ttutils_stage)
        print("the_asset_list: ")
        for i in the_asset_list:
            print( i[0])
        return{'FINISHED'}

# OPERATOR BUTTON_OT_tilt_cam
class BUTTON_OT_tilt_cam(bpy.types.Operator):
    '''Select the camera tilt control'''
    bl_idname = "ttutils.tilt_cam"
    bl_label = "Select Camera Control"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE BUTTON_OT_tilt_cam OPERATOR CLASS")
        for o in bpy.context.selected_objects:
            o.select_set(False)
        bpy.data.objects["AnimGrp.camera"].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects["AnimGrp.camera"]
        return{'FINISHED'}

# OPERATOR BUTTON_OT_save_ttfile
class BUTTON_OT_save_ttfile(bpy.types.Operator):
    '''Return the latest asset - see console'''
    bl_idname = "ttutils.save_ttfile"
    bl_label = "Save Turntable File"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("EXECUTE BUTTON_OT_save_ttfile OPERATOR CLASS")
        save_tt_file(bpy.context.scene.assetname, bpy.context.scene.ttutils_stage)
        return{'FINISHED'}

# PANEL VIEW3D_PT_ttutils_panel
class VIEW3D_PT_ttutils_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Turntable Utils "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator("ttutils.opentt", text=(BUTTON_OT_openTT.bl_label))
        layout.operator("ttutils.get_asset_list", text=(BUTTON_OT_get_asset_list.bl_label))
        layout.prop(bpy.context.scene, "ttutils_stage")
        layout.prop(bpy.context.scene, "assetname")
        layout.operator("ttutils.get_asset", text=(BUTTON_OT_get_asset.bl_label))
        layout.prop(bpy.context.scene, "ttutils_overscan")
        layout.operator("ttutils.set_cam_loc", text=(BUTTON_OT_set_cam_loc.bl_label))
        layout.operator("ttutils.tilt_cam", text=(BUTTON_OT_tilt_cam.bl_label))
        layout.operator("ttutils.selectttcam", text=(BUTTON_OT_selectTTcam.bl_label))
        layout.operator("ttutils.set_out_filepath", text=(BUTTON_OT_set_out_filepath.bl_label))
        layout.operator("ttutils.save_ttfile", text=(BUTTON_OT_save_ttfile.bl_label))
        

#   REGISTER
classes = [ ttutilsProperties, VIEW3D_PT_ttutils_panel, 
            BUTTON_OT_set_cam_loc, BUTTON_OT_get_asset, 
            BUTTON_OT_get_asset_list, BUTTON_OT_openTT, 
            BUTTON_OT_set_out_filepath, BUTTON_OT_save_ttfile,
            BUTTON_OT_tilt_cam, BUTTON_OT_selectTTcam]

def register():
    from bpy.utils import register_class
    for cls in classes:
        print(cls)
        register_class(cls)
    

#   UNREGISTER
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
  

if __name__ == "__main__":
    register()
    
