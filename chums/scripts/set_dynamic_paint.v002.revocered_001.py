import bpy
import os

print('HELLO')
brushes = ['chr_flieswitheagles_scene_ma:legs','chr_luna_scene_ma:foot_R','chr_luna_scene_ma:foot_L','chr_ira_scene_ma:body']
canvas = bpy.data.objects['env.loonbeach:ground.002']
#shots = ['010','020','030','050']
#frames = [146,198,63,123]
shots = ['020','030','050']
frames = [10,10,10]
#shots = ['010']
paintpath = ''


#collect all the mayaCache collections in the file
caches = [c for c in bpy.data.collections if ("_mayaCache" in c.name and not("Caches" in c.name))]
print(caches)


#find mayaCache for current shot
for cache in caches:
    for shot in shots:
        if ("sh"+shot) in cache.name:
            end = frames[shots.index(shot)]
            print(shot, cache.name, end)
            paintpath = os.path.join(os.path.dirname(bpy.data.filepath), "dynamic_paint_test", shot)
            print('paintpath: ', paintpath)
            #ensure output path for image sequences
            if not(os.path.exists(paintpath)):
                os.makedirs(paintpath)
            
            #setup BRUSH
            for brush in brushes:
                print('brush: ', brush)
                for obj in cache.objects:
                    if brush in obj.name and obj.name in bpy.context.view_layer.objects:
                        bpy.context.scene.frame_current += 1
                        brush_obj = obj
                        brush_obj.select_set(True)
                        bpy.context.view_layer.objects.active = brush_obj
                        #bpy.context.scene.frame_current += 1
                        #bpy.context.scene.frame_current -= 1
                        modindex = 0
                        cacheindex = -1
                        for mod in brush_obj.modifiers:
                            #bpy.context.view_layer.update()
                            if mod.type == 'MESH_SEQUENCE_CACHE':
                                cacheindex = modindex
                            modindex += 1
                        if cacheindex >= 0:
                            if not('DP Displace' in brush_obj.modifiers):
                                dp_br_displace = brush_obj.modifiers.new(name='DP Displace',type='DISPLACE')
                                bpy.ops.object.modifier_move_up(modifier='DP Displace')
                                dp_br_displace.strength = 5.0
                        if not('Dynamic Paint Brush' in brush_obj.modifiers):
                            dp_brush_mod = brush_obj.modifiers.new(name='Dynamic Paint Brush',type='DYNAMIC_PAINT')
                            bpy.ops.dpaint.type_toggle(type='BRUSH')
                        else:
                            dp_brush_mod = brush_obj.modifiers['Dynamic Paint Brush']
                        dp_brush_mod.ui_type = 'BRUSH'
                        brush_obj.select_set(True)
                        bpy.context.view_layer.objects.active = brush_obj
                        try:
                            bpy.ops.dpaint.type_toggle(type='BRUSH')
                            bpy.context.view_layer.update()
                            dp_brush_mod.brush_settings.paint_source = 'VOLUME'
                            dp_brush_mod.brush_settings.paint_color = (1.0,1.0,1.0)
                            dp_brush_mod.brush_settings.paint_alpha = 1.0
                            brush_obj.select_set(True)
                        except:
                            bpy.ops.dpaint.type_toggle(type='BRUSH')
                            bpy.context.view_layer.update()
                            dp_brush_mod.brush_settings.paint_source = 'VOLUME'
                            dp_brush_mod.brush_settings.paint_color = (1.0,1.0,1.0)
                            dp_brush_mod.brush_settings.paint_alpha = 1.0
                            brush_obj.select_set(True)
                        
                        bpy.context.view_layer.objects.active = brush_obj
                        #bpy.context.view_layer.update()
                        
                   
            #setup CANVAS
            bpy.context.view_layer.objects.active = canvas
            canvas.select_set(True)
            if not('Dynamic Paint New' in canvas.modifiers):
                dp_canvas_mod = canvas.modifiers.new(name='Dynamic Paint New',type='DYNAMIC_PAINT')
                bpy.ops.dpaint.type_toggle(type='CANVAS')
            else:
                dp_canvas_mod = canvas.modifiers['Dynamic Paint New']
            dp_canvas_mod.ui_type = 'CANVAS'
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_start = 1
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].frame_end = end
            #bpy.context.view_layer.update()
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].surface_format = 'IMAGE'
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].image_resolution = 2048
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_antialiasing = True
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].image_output_path = paintpath
            #bpy.context.view_layer.update()
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].uv_layer = 'UVMap'
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].use_output_a = True
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].output_name_a = (cache.name.replace('_mayaCache','_') + 'paintmap_base_')
            dp_canvas_mod.canvas_settings.canvas_surfaces[0].brush_collection = cache
            bpy.context.view_layer.objects.active = canvas
            canvas.select_set(False)
            bpy.context.view_layer.objects.active = canvas
            #bpy.context.scene.frame_current += 1
            canvas.select_set(True)
            bpy.context.view_layer.objects.active = canvas
            #bpy.context.scene.frame_current += 1
            #bpy.context.view_layer.update()
            #bpy.context.scene.frame_current += 1
            bpy.context.scene.frame_current = 0
            #bpy.context.view_layer.update()
            
            bpy.ops.dpaint.bake()


                    