import bpy
import os

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
    print("\n\n", shot, cache.name, shot_end, cache_offset)
    #setup BRUSH es
    for brush in _brushes:
        print('brush: ', brush)
        for obj in _cache.objects:
            if obj.type == 'MESH':
                obj.scale = (0.0,0.0,0.0)
                obj.keyframe_insert(data_path="scale", frame=(offset-1))
                obj.scale = (1.0,1.0,1.0)
                obj.keyframe_insert(data_path="scale", frame=(offset))
            if brush in obj.name and obj.name in bpy.context.view_layer.objects:
                bpy.context.scene.frame_current += 1
                brush_obj = obj
                print('brush_obj: ',brush_obj)
                brush_obj.select_set(True)
                bpy.context.view_layer.objects.active = brush_obj
                #offset mesh cache
                for mod in brush_obj.modifiers:
                    print("mod:", mod.name)
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
                #create duplicate and inflate for rim
                brush_rim = brush_obj.copy()
                print("brush_rim: ", brush_rim.name)
                bpy.context.collection.objects.link(brush_rim)
                for col in bpy.data.collections:
                    if (brush_rim.name in col.objects) and not(col == _cache):
                        col.objects.unlink(brush_rim)
                    else:
                        if not(brush_rim.name in col.objects) and (col == _cache):
                            col.objects.link(brush_rim)
                #displace brush_rim
                if not('DP Displace' in brush_rim.modifiers):
                    print("add displace mod to: ", brush_rim) 
                    dp_br_displace = brush_rim.modifiers.new(name='DP Displace',type='DISPLACE')
                    while brush_rim.modifiers.find('DP Displace') > 1:
                        bpy.context.view_layer.objects.active = brush_rim
                        brush_rim.modifiers.active = brush_rim.modifiers['DP Displace']
                        bpy.ops.object.modifier_move_up(modifier='DP Displace')
                    dp_br_displace.strength = 5.0
                brush_rim.modifiers['Dynamic Paint Brush'].brush_settings.paint_color = (1.0,1.0,1.0)
    return 0

def do_the_bake():
    bpy.ops.dpaint.bake()
    return "done"

print('\n\nHELLO')
brushes = ['chr_flieswitheagles_scene_ma:legs','chr_luna_scene_ma:foot_R','chr_luna_scene_ma:foot_L','chr_ira_scene_ma:body']
canvas = bpy.data.objects['env.loonbeach:ground.002']
this_pass = "dynamic_paint_rim_"
#shots = {'020':10,'030':10,'050':10}
shots = {'010':146,'020':198,'030':64,'050':124,'070':280,'080':262,'090':43,'110':73,'120':172}
#shots = {'010':146,'020':198,'030':64}
#shots = {'030':10}
paintpath = ''
viewlayer = bpy.context.view_layer.name

last_shot = ''
shot_end = 0
cache_offset = 0
render_end = 0
#define brush objects
brushes = ['chr_flieswitheagles_scene_ma:legs','chr_luna_scene_ma:foot_R','chr_luna_scene_ma:foot_L','chr_ira_scene_ma:body']
#collect all the mayaCache collections in the file
caches = [c for c in bpy.data.collections if ("_mayaCache" in c.name and not("Caches" in c.name))]
print(caches)

#process shots
for shot in shots.keys():
    shot_end = shots[shot]
    #find mayaCache for current shot
    for cache in caches:
        if ("_sh"+shot+"_") in cache.name:
            dp_brush_setup(brushes,cache,cache_offset)
    #deselect all objects
    for ob in bpy.data.objects:
        ob.select_set(False)
    render_end += (shot_end + 1)
    if last_shot == '':
        last_shot = shot
        cache_offset = shots[last_shot]
    else:
        cache_offset += shots[last_shot]

#setup CANVAS
canvas.select_set(True)
bpy.context.view_layer.objects.active = canvas
print('canvas: ', canvas.name)

#set output paintpath for image sequence output
this_version = ''
for i in os.path.basename(bpy.data.filepath).split("_"):
    if i.startswith("v") and i[-1] in "0123456789":
        this_version += i
print(this_version)
paintpath = os.path.join(os.path.dirname(bpy.data.filepath), (this_pass+this_version), "all")
print('paintpath: ', paintpath)

#handle output path existence
if not(os.path.exists(paintpath)):
    os.makedirs(paintpath)
#displace ground to catch floaters
if not('DP Displace' in canvas.modifiers):
    print("add displace mod to: ",canvas) 
    dp_cv_displace = canvas.modifiers.new(name='DP Displace',type='DISPLACE')
    bpy.ops.object.modifier_move_up(modifier='DP Displace')
    dp_cv_displace.strength = 0.02
    dp_cv_displace.mid_level = 0.0
#dynamic paint canvas modifier
if not('Dynamic Paint New' in canvas.modifiers):
    dp_canvas_mod = canvas.modifiers.new(name='Dynamic Paint New',type='DYNAMIC_PAINT')
else:
    dp_canvas_mod = canvas.modifiers['Dynamic Paint New']
print('CANVAS bpy.context.view_layer.objects.active:', bpy.context.view_layer.objects.active)
dp_canvas_mod.ui_type = 'CANVAS'
#initialize canvas if none found
if dp_canvas_mod.canvas_settings == None:
    bpy.ops.dpaint.type_toggle(type='CANVAS')
dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_start = 0
dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_end = render_end
dp_canvas_mod.canvas_settings.canvas_surfaces[0].surface_format = 'IMAGE'
dp_canvas_mod.canvas_settings.canvas_surfaces[0].image_resolution = 2048
dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_antialiasing = True
dp_canvas_mod.canvas_settings.canvas_surfaces[0].image_output_path = paintpath
dp_canvas_mod.canvas_settings.canvas_surfaces[0].uv_layer = 'UVMap'
dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_output_a = True
dp_canvas_mod.canvas_settings.canvas_surfaces[0].output_name_a = (cache.name.replace('_mayaCache','')[:-6] + '_paintmap_base_')
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
    
#for o in bpy.data.objects:
#    if len(o.modifiers) > 0 and o.modifiers[0].type == 'MESH_SEQUENCE_CACHE' and not(o.modifiers[0].cache_file.frame_offset == 0.0):
#        _offset = o.modifiers[0].cache_file.frame_offset
#        o.modifiers[0].cache_file.frame_offset = 0
#        print("OFFSET ", o.name, " FROM ", _offset, " TO ", o.modifiers[0].cache_file.frame_offset)
