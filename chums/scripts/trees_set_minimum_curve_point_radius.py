import bpy

obs = bpy.context.selected_objects
for ob in obs:
    if ob.type == 'CURVE':
        for sp in ob.data.splines:
            for pt in sp.bezier_points:
                print(pt.radius)
                if pt.radius < 0.5:
                    pt.radius = 0.5
                    
                    
