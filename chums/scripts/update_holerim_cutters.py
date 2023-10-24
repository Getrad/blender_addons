import bpy

def localize_parent(ob):
    pobj = ob.parent
    pobj.make_local()
    if pobj.parent is not None:
        localize_parent(pobj)
            
objects_localize = ["ground.master",]
cutter_names = [ob.name for ob in bpy.data.objects if "prx_holeRim_01:bool_cutter_" in ob.name]

for obj_name in objects_localize:
    if obj_name in bpy.data.objects:
        obj = bpy.data.objects[obj_name]
        for col in bpy.data.collections:
            if obj_name in col.all_objects:
                col.make_local()
        if obj.parent is not None:
            localize_parent(obj)
        obj.make_local()
        
        for cutname in cutter_names:
            
            if bpy.data.objects[cutname]:
                boolmod = obj.modifiers.new("Boolean", 'BOOLEAN')
                boolmod.solver = 'FAST'
                boolmod.operation = 'DIFFERENCE'
                boolmod.operand_type = 'OBJECT'
                boolmod.object = bpy.data.objects[cutname]
                
