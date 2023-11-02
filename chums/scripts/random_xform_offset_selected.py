import bpy
import random as rd

offset_max = 0.1
rotate_max = 360
scale_max = 0.2

for i in bpy.context.selected_objects:
    a = ((1-(2.0*rd.random()))*offset_max)
    b = ((1-(2.0*rd.random()))*offset_max)
    c = (i.location.x + b,i.location.y + a,i.location.z)
    i.location = c
    
    rx = ((1-(2.0*rd.random()))*rotate_max)
    ry = ((1-(2.0*rd.random()))*rotate_max)
    rz = ((1-(2.0*rd.random()))*rotate_max)
    rc = (i.rotation_euler[0] + rx,i.rotation_euler[1] + ry,i.rotation_euler[2] + rz)
    i.rotation_euler = rc
    
    sx = ((1-(2.0*rd.random()))*scale_max)
    sy = ((1-(2.0*rd.random()))*scale_max)
    sz = ((1-(2.0*rd.random()))*scale_max)
    sc = (i.scale[0] + sx,i.scale[1] + sy,i.scale[2] + sz)
    i.scale = sc