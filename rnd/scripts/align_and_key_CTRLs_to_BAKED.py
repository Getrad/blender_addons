import bpy

for i in bpy.data.objects:
    if i.type == 'EMPTY' and ('_CTRL' in i.name) and not(i.name.startswith('nul.')):
        testname = ('nul.'+i.name+'.BAKED.000')
        if testname in bpy.data.objects:
            tgtobj = bpy.data.objects[testname]
            i.location = tgtobj.location
            i.rotation_euler = tgtobj.rotation_euler
            if tgtobj.animation_data:
                for crv in tgtobj.animation_data.action.fcurves:
                    for pt in crv.keyframe_points:
                        mytime = pt.co[0]
                        tgtobj.keyframe_insert(data_path="location",frame=mytime)
                        tgtobj.keyframe_insert(data_path="rotation_euler",frame=mytime)
                        