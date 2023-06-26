import bpy
import os

print('\n\nHELLO')

canvas = bpy.data.objects['env.loonbeach:beach_canvas']
this_pass = "dynamic_paint_core_"
brush_displace = 0.1
canvas_displace = 0.01
#shots = {'020':10,'030':10,'050':10}
#103_sc06
#shots = {'010':146,'020':198,'030':64,'050':124,'070':280,'080':262,'090':43,'110':73,'120':172}
#103_sc01
#shots = {'010':170,'030':118,'040':113,'050':78,'060':212}
#103_sc03
#shots = {'010':103,'020':223,'030':118,'040':103,'050':126}
#103_sc08
#shots = {'010':191,'020':210,'030':107,'040':229,'050':169,'060':305,'070':234,'080':103,'090':213}
shots = {'010':10,'030':107,'040':229,'080':103,'090':10}
#103_sc10
#shots = {'010':210,'020':83,'030':310}
shots = {'010':20,'020':83,'030':310}
#103_sc11
#shots = {'010':87,'020':321,'030':322,'040':63,'050':105}
shots = {'010':87,'020':321,'030':10,'040':10,'050':105}
paintpath = ''
viewlayer = bpy.context.view_layer.name
shot_end = 0
cache_offset = 0
render_end = 0
resolution = 4096
#define brush objects
brushes = ['chr_frog_scene_ma:body_C',
           'chr_luna_scene_ma:foot_R','chr_luna_scene_ma:foot_L',
           'chr_lloyd_scene_ma:foot_R','chr_lloyd_scene_ma:foot_R',
           'chr_motherloon_scene_ma:foot_L','chr_motherloon_scene_ma:foot_R',
           'chr_fatherloon_scene_ma:foot_L','chr_fatherloon_scene_ma:foot_r',
           'chr_ira_scene_ma:body']
#collect all the mayaCache collections in the file
caches = [c for c in bpy.data.collections if ("_mayaCache" in c.name and not("Caches" in c.name))]
print(caches)

# Helper to list all LayerCollections in the view layer recursively
def all_layer_collections(view_layer):
    stack = [view_layer.layer_collection]
    while stack:
        lc = stack.pop()
        yield lc
        stack.extend(lc.children)

def set_collection_excluded(scene, view_layer_name, collection_name, exclude):
    view_layer = scene.view_layers.get(view_layer_name, None)
    if view_layer:
        for lc in all_layer_collections(view_layer):
            if lc.collection.name == collection_name:
                lc.exclude = exclude

def dp_brush_setup(_brushes,_cache,offset):
    set_collection_excluded(bpy.context.scene, viewlayer, cache.name, False)
    #setup BRUSH es
    for brush in _brushes:
        for obj in _cache.objects:
            if obj.type == 'MESH':
                obj.scale = (0.0,0.0,0.0)
                obj.keyframe_insert(data_path="scale", frame=(offset-1))
                obj.scale = (1.0,1.0,1.0)
                obj.keyframe_insert(data_path="scale", frame=(offset))
            if brush in obj.name and obj.name in bpy.context.view_layer.objects:
                bpy.context.scene.frame_current += 1
                brush_obj = obj
                print('Setup brush: ', brush)
                print('brush_obj: ',brush_obj)
                brush_obj.select_set(True)
                bpy.context.view_layer.objects.active = brush_obj
                #offset mesh cache
                for mod in brush_obj.modifiers:
                    if mod.type == 'MESH_SEQUENCE_CACHE':
                        mod.cache_file.frame_offset = offset
                        print("OFFSET ", brush_obj.name, " BY ", offset ," TO ", mod.cache_file.frame_offset)
                        brush_obj.update_tag()
                #add dynamic paint modifier
                if not('Dynamic Paint Brush' in brush_obj.modifiers):
                    dp_brush_mod = brush_obj.modifiers.new(name='Dynamic Paint Brush',type='DYNAMIC_PAINT')
                else:
                    dp_brush_mod = brush_obj.modifiers['Dynamic Paint Brush']
                dp_brush_mod.ui_type = 'BRUSH'
                bpy.context.view_layer.objects.active = brush_obj
                brush_obj.modifiers.active = brush_obj.modifiers['Dynamic Paint Brush']
                #initialize brush if none found
                if dp_brush_mod.brush_settings == None:
                    bpy.ops.dpaint.type_toggle(type='BRUSH')
                dp_brush_mod.brush_settings.paint_source = 'VOLUME'
                dp_brush_mod.brush_settings.paint_color = (1.0,1.0,1.0)
                dp_brush_mod.brush_settings.paint_alpha = 1.0
                #displace brush_obj
                if not('DP Displace' in brush_obj.modifiers):
                    print("add displace mod to: ", brush_obj) 
                    dp_br_displace = brush_obj.modifiers.new(name='DP Displace',type='DISPLACE')
                    while brush_obj.modifiers.find('DP Displace') > 1:
                        bpy.context.view_layer.objects.active = brush_obj
                        brush_obj.modifiers.active = brush_obj.modifiers['DP Displace']
                        bpy.ops.object.modifier_move_up(modifier='DP Displace')
                    dp_br_displace.strength = brush_displace
                brush_obj.modifiers['Dynamic Paint Brush'].brush_settings.paint_color = (1.0,1.0,1.0)
    return 0

def do_the_bake():
    bpy.ops.dpaint.bake()
    return "done"


#process shots
for shot in shots.keys():
    shot_end = shots[shot]
    #find mayaCache for current shot
    for cache in caches:
        if ("_sh"+shot+"_") in cache.name:
            this_offset = 0
            for shot_key in shots.keys():
                print("shot_key", shot_key)
                if int(shot_key) < int(shot):
                    this_offset = this_offset + shots[shot_key] + 1
                    print("this_offset: ", this_offset)
            cache_offset = this_offset
            print("shot", shot)
            print("cache", cache)
            print("cache_offset", cache_offset)
            dp_brush_setup(brushes,cache,cache_offset)
    #deselect all objects
    for ob in bpy.data.objects:
        ob.select_set(False)
    render_end += (shot_end + 1)
    
    
    

#setup CANVAS
canvas.select_set(True)
bpy.context.view_layer.objects.active = canvas
print('canvas: ', canvas.name)

#set output paintpath for image sequence output
this_version = ''
for i in os.path.basename(bpy.data.filepath).replace(".blend","").split("_"):
    if i.startswith("v") and i[-1] in "0123456789":
        this_version += i
print(this_version)
paintpath = os.path.join(os.path.dirname(bpy.data.filepath), (this_pass+this_version))
print('paintpath: ', paintpath)

#handle output path existence
if not(os.path.exists(paintpath)):
    os.makedirs(paintpath)
#displace ground to catch floaters
if not('DP Displace' in canvas.modifiers):
    print("add displace mod to: ",canvas) 
    dp_cv_displace = canvas.modifiers.new(name='DP Displace',type='DISPLACE')
    bpy.ops.object.modifier_move_up(modifier='DP Displace')
    dp_cv_displace.strength = canvas_displace
    dp_cv_displace.mid_level = 0.0
#dynamic paint canvas modifier
if not('Dynamic Paint Canvas' in canvas.modifiers):
    dp_canvas_mod = canvas.modifiers.new(name='Dynamic Paint Canvas',type='DYNAMIC_PAINT')
else:
    dp_canvas_mod = canvas.modifiers['Dynamic Paint Canvas']
print('CANVAS bpy.context.view_layer.objects.active:', bpy.context.view_layer.objects.active)
dp_canvas_mod.ui_type = 'CANVAS'
#initialize canvas if none found
if dp_canvas_mod.canvas_settings == None:
    bpy.ops.dpaint.type_toggle(type='CANVAS')
dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_start = 1
dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_end = render_end
dp_canvas_mod.canvas_settings.canvas_surfaces[0].surface_format = 'IMAGE'
dp_canvas_mod.canvas_settings.canvas_surfaces[0].image_resolution = resolution
dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_antialiasing = True
dp_canvas_mod.canvas_settings.canvas_surfaces[0].image_output_path = paintpath
dp_canvas_mod.canvas_settings.canvas_surfaces[0].uv_layer = 'UVMap'
dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_output_a = True
dp_canvas_mod.canvas_settings.canvas_surfaces[0].output_name_a = (cache.name.replace('_mayaCache','')[:-6] + '_' + this_pass)
dp_canvas_mod.canvas_settings.canvas_surfaces[0].brush_collection = bpy.data.collections['sh000_mayaCaches']
#dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_output_b = True
#dp_canvas_mod.canvas_settings.canvas_surfaces[0].output_name_b = (cache.name.replace('_mayaCache','')[:-6] + '_wetmap_base_')
#dp_canvas_mod.canvas_settings.canvas_surfaces[0].brush_collection = bpy.data.collections['sh000_mayaCaches']

bpy.context.scene.frame_end = render_end
bpy.context.scene.frame_current = 0
bpy.context.view_layer.update()
canvas.update_tag()

#mybake = bpy.ops.dpaint.bake()
mybake = do_the_bake()

if mybake:
    bpy.context.view_layer.objects.active = None
    print("COMPLETED: ", cache.name)
    
'''
# CLEAN UP CODE
# COPY TO A BLANK SCRIPT WINDOW AND EXECUTE BEFORE RUNNING DYNAPAINT AGAIN
import bpy
for o in bpy.data.objects:
    if len(o.modifiers) > 0:
        if o.modifiers[0].type == 'MESH_SEQUENCE_CACHE' and not(o.modifiers[0].cache_file.frame_offset == 0.0):
            _offset = o.modifiers[0].cache_file.frame_offset
            o.modifiers[0].cache_file.frame_offset = 0
        if 'DP Displace' in o.modifiers:
            o.modifiers.remove(o.modifiers['DP Displace'])
        if 'Dynamic Paint Canvas' in o.modifiers:
            o.modifiers.remove(o.modifiers['Dynamic Paint Canvas'])
        if 'Dynamic Paint Brush' in o.modifiers:
            o.modifiers.remove(o.modifiers['Dynamic Paint Brush'])
    if o.animation_data is not None and o.animation_data.action is not None:
        for fc in o.animation_data.action.fcurves:
            if fc.data_path == 'scale':
                o.animation_data.action.fcurves.remove(fc)
        o.scale = (1.0,1.0,1.0)
'''