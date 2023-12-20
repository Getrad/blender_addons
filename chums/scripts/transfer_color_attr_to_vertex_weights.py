import bpy

def convert_attrib(dom,dtype):
    bpy.ops.geometry.attribute_convert(domain=dom,data_type=dtype)
    return 0
    

def attribute_to_vertexgroup(obj, attrib):
    for _colattr in obj.data.color_attributes:
        colattr = _colattr.name
        vgroupname = (colattr+"_copy")

        if (len(obj.vertex_groups) < 1) or not(vgroupname in obj.vertex_groups):
            vgroup = obj.vertex_groups.new(name=vgroupname)
        vgroup = obj.vertex_groups[vgroupname]

        for vv in obj.data.vertices:
            vi = vv.index
            mycol = obj.data.color_attributes[colattr].data[vi].color
            rndvalue = ((mycol[0]+mycol[1]+mycol[2])/3.0)
            if rndvalue > 0:
                obj.data.vertices[vi].select = True
                vgroup.add([vi], rndvalue,  'REPLACE')
            else:
                obj.data.vertices[vi].select = False
    return 0

 
for ob in bpy.context.selected_objects:
    if ob.type == 'MESH' and len(ob.data.attributes) > 0:
        for att in ob.data.attributes:
            bpy.context.view_layer.objects.active = ob
            orig_domain = att.domain
            orig_data_type = att.data_type
            convert_attrib('POINT','FLOAT_COLOR')
            attribute_to_vertexgroup(ob, att)
            #convert_attrib(orig_domain,orig_data_type)
