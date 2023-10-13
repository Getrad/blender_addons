import bpy

print('HELLO')

the_feet = ['chr_flieswitheagles_scene_ma:legs','chr_luna_scene_ma:foot_R','chr_luna_scene_ma:foot_L','chr_ira_scene_ma:body']

for foot in the_feet:
    footobj = bpy.data.objects[foot]
    footobj.select_set(True)
    modindex = 0
    print(len(footobj.modifiers))
    for mod in footobj.modifiers:
        if mod.type == 'MESH_SEQUENCE_CACHE' and not(modindex == (len(footobj.modifiers)-1)):
            print(modindex, mod.type, "  >  ",  footobj.modifiers[modindex + 1].type)
        modindex += 1
    