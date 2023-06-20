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

def do_the_bake():
    bpy.ops.dpaint.bake()
    return "done"

print('HELLO')
brushes = ['chr_flieswitheagles_scene_ma:legs','chr_luna_scene_ma:foot_R','chr_luna_scene_ma:foot_L','chr_ira_scene_ma:body']
canvas = bpy.data.objects['env.loonbeach:ground.002']
#shots = {'020':10,'030':10,'050':10}
shots = {'010':146,'020':198,'030':64,'050':124,'070':280,'080':262,'090':43,'110':73,'120':172}
#shots = {'010':146,'020':198,'030':64}
#shots = {'030':10}
paintpath = ''
viewlayer = bpy.context.view_layer.name

#collect all the mayaCache collections in the file
caches = [c for c in bpy.data.collections if ("_mayaCache" in c.name and not("Caches" in c.name))]
print(caches)

last_shot = ''
shot_end = 0
cache_offset = 0
render_end = 0
for shot in shots.keys():
    cachefiles = []
    shot_end = shots[shot]
    #find mayaCache for current shot
    for cache in caches:
        #deselect all objects
        for ob in bpy.data.objects:
            ob.select_set(False)
        if ("_sh"+shot) in cache.name:
            set_collection_excluded(bpy.context.scene, viewlayer, cache.name, False)
            print("\n\n", shot, cache.name, shot_end, cache_offset)
            #set putput paintpath for image sequence path
            paintpath = os.path.join(os.path.dirname(bpy.data.filepath), "dynamic_paint_test", "all")
            print('paintpath: ', paintpath)
            #handle output path existence
            if not(os.path.exists(paintpath)):
                os.makedirs(paintpath)
            #setup BRUSHes
            for brush in brushes:
                print('brush: ', brush)
                for obj in cache.objects:
                    if brush in obj.name and obj.name in bpy.context.view_layer.objects:
                        bpy.context.scene.frame_current += 1
                        brush_obj = obj
                        print('brush_obj: ',brush_obj)
                        brush_obj.select_set(True)
                        bpy.context.view_layer.objects.active = brush_obj
                        modindex = 0
                        cacheindex = -1
                        for mod in brush_obj.modifiers:
                            print("mod:", mod.name)
                            if mod.type == 'MESH_SEQUENCE_CACHE':
                                cacheindex = modindex
                                if not(mod.cache_file in cachefiles):
                                    cachefiles.append(mod.cache_file)
                                mod.cache_file.frame_offset = cache_offset
                                print("OFFSET ", brush_obj.name, " BY ", cache_offset ," TO ", mod.cache_file.frame_offset)
                                brush_obj.update_tag()
                            modindex += 1
                        if cacheindex >= 0:
                            if not('DP Displace' in brush_obj.modifiers):
                                print("add displace mod to: ",brush_obj) 
                                dp_br_displace = brush_obj.modifiers.new(name='DP Displace',type='DISPLACE')
                                bpy.ops.object.modifier_move_up(modifier='DP Displace')
                                dp_br_displace.strength = 1.0
                        if not('Dynamic Paint Brush' in brush_obj.modifiers):
                            dp_brush_mod = brush_obj.modifiers.new(name='Dynamic Paint Brush',type='DYNAMIC_PAINT')
                        else:
                            dp_brush_mod = brush_obj.modifiers['Dynamic Paint Brush']
                        dp_brush_mod.ui_type = 'BRUSH'
                        bpy.context.view_layer.objects.active = brush_obj
                        brush_obj.modifiers.active = brush_obj.modifiers['Dynamic Paint Brush']
                        print('BRUSH bpy.context.view_layer.objects.active:', bpy.context.view_layer.objects.active)
                        if dp_brush_mod.brush_settings == None:
                            bpy.ops.dpaint.type_toggle(type='BRUSH')
                        dp_brush_mod.brush_settings.paint_source = 'VOLUME'
                        dp_brush_mod.brush_settings.paint_color = (1.0,1.0,1.0)
                        dp_brush_mod.brush_settings.paint_alpha = 1.0   
    render_end += shot_end
    if last_shot == '':
        last_shot = shot
        cache_offset = shots[last_shot]
    else:
        cache_offset += shots[last_shot]

#setup CANVAS
canvas.select_set(True)
bpy.context.view_layer.objects.active = canvas
if not('DP Displace' in canvas.modifiers):
    print("add displace mod to: ",canvas) 
    dp_cv_displace = canvas.modifiers.new(name='DP Displace',type='DISPLACE')
    bpy.ops.object.modifier_move_up(modifier='DP Displace')
    dp_cv_displace.strength = 0.01
    dp_cv_displace.mid_level = 0.0
print('canvas: ', canvas.name)
if not('Dynamic Paint New' in canvas.modifiers):
    dp_canvas_mod = canvas.modifiers.new(name='Dynamic Paint New',type='DYNAMIC_PAINT')
else:
    dp_canvas_mod = canvas.modifiers['Dynamic Paint New']
print('CANVAS bpy.context.view_layer.objects.active:', bpy.context.view_layer.objects.active)
dp_canvas_mod.ui_type = 'CANVAS'
if dp_canvas_mod.canvas_settings == None:
    bpy.ops.dpaint.type_toggle(type='CANVAS')
dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_start = 1
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

bpy.context.view_layer.update()
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
