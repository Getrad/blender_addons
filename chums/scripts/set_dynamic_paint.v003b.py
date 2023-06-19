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

print('HELLO')
brushes = ['chr_flieswitheagles_scene_ma:legs','chr_luna_scene_ma:foot_R','chr_luna_scene_ma:foot_L','chr_ira_scene_ma:body']
canvas = bpy.data.objects['env.loonbeach:ground.002']
#shots = ['010','020','030','050']
#frames = [146,198,63,123]
#shots = {'020':10,'030':10,'050':10}
shots = {'020':10,'030':10}
frames = [10,10,10]
#shots = ['010']
paintpath = ''
viewlayer = bpy.context.view_layer.name

#collect all the mayaCache collections in the file
caches = [c for c in bpy.data.collections if ("_mayaCache" in c.name and not("Caches" in c.name))]
print(caches)


for shot in shots.keys():
    dg = bpy.context.evaluated_depsgraph_get() #getting the dependency graph
    #find mayaCache for current shot
    for cache in caches:
        #deselect all objects
        for ob in bpy.data.objects:
            ob.select_set(False)
        if ("sh"+shot) in cache.name:
            #set_collection_excluded(bpy.context.scene, viewlayer, cache.name, False)
            end = shots[shot]
            print("\n\n", shot, cache.name, end)
            #set putput paintpath for image sequence path
            paintpath = os.path.join(os.path.dirname(bpy.data.filepath), "dynamic_paint_test", shot)
            print('paintpath: ', paintpath)
            #handle output path existence
            if not(os.path.exists(paintpath)):
                os.makedirs(paintpath)
            
            #setup CANVAS
            canvas.select_set(True)
            bpy.context.view_layer.objects.active = canvas
            print('canvas: ', canvas.name)
            if not('Dynamic Paint New' in canvas.modifiers):
                dp_canvas_mod = canvas.modifiers.new(name='Dynamic Paint New',type='DYNAMIC_PAINT')
            else:
                dp_canvas_mod = canvas.modifiers['Dynamic Paint New']
            print('CANVAS bpy.context.view_layer.objects.active:', bpy.context.view_layer.objects.active)
            dp_canvas_mod.ui_type = 'CANVAS'
            bpy.ops.dpaint.type_toggle(type='CANVAS')
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_start = 1
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_end = end
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].surface_format = 'IMAGE'
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].image_resolution = 2048
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_antialiasing = True
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].image_output_path = paintpath
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].uv_layer = 'UVMap'
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_output_a = True
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].output_name_a = (cache.name.replace('_mayaCache','_') + 'paintmap_base_')
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].brush_collection = cache
            bpy.context.view_layer.objects.active = None
            canvas.select_set(False)
                        
            #setup BRUSH
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
                            modindex += 1
                        if cacheindex >= 0:
                            if not('DP Displace' in brush_obj.modifiers):
                                print("add displace mod to: ",brush_obj) 
                                dp_br_displace = brush_obj.modifiers.new(name='DP Displace',type='DISPLACE')
                                bpy.ops.object.modifier_move_up(modifier='DP Displace')
                                dp_br_displace.strength = 5.0
                        if not('Dynamic Paint Brush' in brush_obj.modifiers):
                            dp_brush_mod = brush_obj.modifiers.new(name='Dynamic Paint Brush',type='DYNAMIC_PAINT')
                        else:
                            dp_brush_mod = brush_obj.modifiers['Dynamic Paint Brush']
                        dp_brush_mod.ui_type = 'BRUSH'
                        bpy.context.view_layer.objects.active = brush_obj
                        brush_obj.modifiers.active = brush_obj.modifiers['Dynamic Paint Brush']
                        print('BRUSH bpy.context.view_layer.objects.active:', bpy.context.view_layer.objects.active)
                        bpy.ops.dpaint.type_toggle(type='BRUSH')
                        try:
                            bpy.context.view_layer.update()
                        except:
                            print("failed on brush add for :", brush_obj.name) 
                        dp_brush_mod.brush_settings.paint_source = 'VOLUME'
                        dp_brush_mod.brush_settings.paint_color = (1.0,1.0,1.0)
                        dp_brush_mod.brush_settings.paint_alpha = 1.0
            bpy.context.view_layer.objects.active = canvas
            canvas.select_set(True)
            bpy.context.view_layer.objects.active = canvas       
            bpy.context.scene.frame_current = 0
            #bpy.context.view_layer.update()
            bpy.ops.dpaint.bake()
            bpy.context.view_layer.objects.active = None
            print("COMPLETED: ", cache.name)
        


                    