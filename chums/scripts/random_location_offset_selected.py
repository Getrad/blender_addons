import bpy
import random as rd

offset_max = 0.01

for i in bpy.context.selected_objects:
    a = ((1-(2.0*rd.random()))*offset_max)
    b = ((1-(2.0*rd.random()))*offset_max)
    c = (i.location.x + b,i.location.y + a,i.location.z)
    i.location = c
    