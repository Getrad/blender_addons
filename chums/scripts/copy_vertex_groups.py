import bpy

def copy_vertex_groups(src,tgts):
    for tgt in tgts:
        for vgrp in src.vertex_groups:
            if not(vgrp.name in tgt.vertex_groups):
                ngrp = tgt.vertex_groups.new()
                ngrp.name = vgrp.name
        
        
if __name__ == "__main__":
    copy_vertex_groups((bpy.context.object),[i for i in bpy.context.selected_objects if not i == (bpy.context.object)])
    