import bpy

color_attr_ground = {"Color:Riverbed":['POINT','FLOAT_COLOR'],"Color:RiverbedLow":['POINT','FLOAT_COLOR'],"Color:GroundShade":['POINT','FLOAT_COLOR']}
color_attr_water = {"weight":['POINT','FLOAT_COLOR'],"weight2":['POINT','FLOAT_COLOR']}

def set_col_attribs(objs,attribs):
    for ob in objs:
        for attr in attribs.keys():
            if not(attr in ob.data.attributes):
                print("ADD", attr)
                ob.data.attributes.new(name=attr, type=attribs[attr][1], domain=attribs[attr][0])
            else:
                print("FOUND", attr)
                if ob.data.attributes[attr].domain == attribs[attr][0] and ob.data.attributes[attr].data_type == attribs[attr][1]:
                    print("CHECKS PASSED", attr)
                else:
                    print("UPDATE", attr, "\n", ob.data.attributes[attr].domain, "\n", ob.data.attributes[attr].data_type)
                    ob.data.attributes[attr].domain = attribs[attr][0]
                    ob.data.attributes[attr].data_type = attribs[attr][1]
                
if __name__ == "__main__":
    set_col_attribs(bpy.context.selected_objects,color_attr_water)
            