import bpy 

print("\n\nRunning Library Check\n\n")

libdict = {}
cursel = bpy.context.selected_objects
listobjects = 0

for o in cursel:
    if o.instance_collection is not None:
        if o.instance_collection.library.filepath not in libdict.keys():
            libdict[o.instance_collection.library.filepath] = []
        if o.instance_collection.library.filepath in libdict.keys():
            if listobjects:
                for ob in o.instance_collection.objects:
                    if not ob.name in libdict[o.instance_collection.library.filepath]:
                        libdict[o.instance_collection.library.filepath].append(ob.name)
            else:
                if not o.name in libdict[o.instance_collection.library.filepath]:
                    libdict[o.instance_collection.library.filepath].append(o.name)
            
print(libdict)
