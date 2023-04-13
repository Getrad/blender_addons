# made in response to --
# Attach particle geometry to baked animated objects - empties or geometry
# v0.5 - updated for 2.80

bl_info = {
    "name": "Proximity Parent",
    "author": "conrad dueck",
    "version": (0,0,5),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > Tangent",
    "description": "Parent source objects under nearest target objects",
    "warning": "",
    "wiki_url": "https://tangentanimation.sharepoint.com/wiki/Pages/Proximity%20Parent.aspx",
    "tracker_url": "",
    "category": "Tangent"}

import bpy, math, mathutils

####    GLOBAL VARIABLES    ####
vsn='0.5'
supported_fcurves = ['location']
thesources = []


####    FUNCTIONS    ####
def get_distance(first, second):
    locx = second[0] - first[0]
    locy = second[1] - first[1]
    locz = second[2] - first[2]
    distance = math.sqrt((locx)**2 + (locy)**2 + (locz)**2)
    #print('get_distance returns: ', str(distance))
    return distance

def get_relative_offset(master, slave):
    mastermatrix = master.matrix_world.inverted()
    slaveoffset = mastermatrix * slave.matrix_world.translation
    theoffset = [slaveoffset[0],slaveoffset[1],slaveoffset[2]]
    #print('get_relative_offset returns: ', str(theoffset))
    return theoffset

def get_object_center(theobj):
    from mathutils import Vector
    themin = [theobj.location.x,theobj.location.y,theobj.location.z]
    themax = [theobj.location.x,theobj.location.y,theobj.location.z]
    thematrix = theobj.matrix_world
    if theobj.type == 'MESH':
        #print('\nget_object_center function on MESH object ', theobj.name)
        if len(theobj.data.vertices) >= 1:
            thefirstloc = theobj.data.vertices[0].co @ thematrix
            themin = [thefirstloc.x,thefirstloc.y,thefirstloc.z]
            themax = [thefirstloc.x,thefirstloc.y,thefirstloc.z]
            #print('\nget_object_center function on MESH object ', theobj.name)
            for vertex in theobj.data.vertices:
                theloc = vertex.co @ thematrix
                if theloc[0] > themax[0]:
                    themax[0] = theloc[0]
                if theloc[0] < themin[0]:
                    themin[0] = theloc[0]
                if theloc[1] > themax[1]:
                    themax[1] = theloc[1]
                if theloc[1] < themin[1]:
                    themin[1] = theloc[1]
                if theloc[2] > themax[2]:
                    themax[2] = theloc[2]
                if theloc[2] < themin[2]:
                    themin[2] = theloc[2]
        else:
            #print('get_object_center function on MESH object with 0 vertices, utilizing the bounding volume which DOES define verts for ', theobj.name)
            for vertex in theobj.bound_box:
                theloc = thematrix @ Vector((vertex[0],vertex[1],vertex[2]))
                if theloc[0] > themax[0]:
                    themax[0] = theloc[0]
                if theloc[0] < themin[0]:
                    themin[0] = theloc[0]
                if theloc[1] > themax[1]:
                    themax[1] = theloc[1]
                if theloc[1] < themin[1]:
                    themin[1] = theloc[1]
                if theloc[2] > themax[2]:
                    themax[2] = theloc[2]
                if theloc[2] < themin[2]:
                    themin[2] = theloc[2]
        print(themin, '\n', themax)
        thesize = [(themax[0]-themin[0]),(themax[1]-themin[1]),(themax[2]-themin[2])]
        #print('thesize = ', thesize)
        thecenter = ([((themin[0]+themax[0])/2),((themin[1]+themax[1])/2),((themin[2]+themax[2])/2)])
    else:
        #thecenter = [theobj.location.x,theobj.location.y,theobj.location.z]
        thecenter = theobj.matrix_world.to_translation
    print('get_object_center for ',theobj.type, ' - ', theobj.name, ' returning: ', str(thecenter))
    return thecenter

####    CLASSES    ####
#   PROPERTY GROUP OBJECT_PG_proximityparent
class OBJECT_PG_proximityparent(bpy.types.PropertyGroup):
    #name = bpy.props.StringProperty(name="test prop", default="unknown")
    name: bpy.props.StringProperty()
#bpy.utils.register_class(OBJECT_PG_proximityparent)

#   BUTTON BUTTON_OT_proximityparent_gobutton
class BUTTON_OT_proximityparent_gobutton(bpy.types.Operator):
    bl_idname = 'proximityparent.gobutton'
    bl_label = 'Go'
    bl_description = 'Parent selected objects to the nearest Target object from the tagged Targets.'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('START')
        thesources = []
        thecurrentframe = bpy.context.scene.frame_current
        for ob in bpy.context.selected_objects:
            if not(ob.name in bpy.context.scene.BUTTON_OT_proximityparent_target):
                thesources.append(ob)
                print('valid selection: ', ob.name)
            else:
                print('invalid selection: ', ob.name, ' (it\'s tagged as a target)')
        bpy.ops.object.select_all(action='DESELECT')
        #   Loop thru thesources and find nearest targets
        for srcob in thesources:
            print('\nprocess: ', srcob)
            srcob.select_set(True)
            bpy.context.view_layer.objects.active = srcob
            #   Determine current source object location in world space (center of mass or pivot based on UI selection)
            if (context.scene.proximityparent_targetpoint == 'COM') and (srcob.type == 'MESH'):
                thesrccom = get_object_center(srcob)
                print(srcob.name, '\t', srcob.type, '\t', 'using COM location of ', str(thesrccom))
            else:
                thesrccom = [srcob.matrix_world.translation[0],srcob.matrix_world.translation[1],srcob.matrix_world.translation[2]]
                print(srcob.name, '\t', srcob.type, '\t', 'using Pivot location of ', str(thesrccom))
            #   measure the distance from the source object location (returned above) to the tagged target objects
            thedistance = 10000000000.0
            for thetarget in context.scene.BUTTON_OT_proximityparent_target:
                thistarget = bpy.data.objects[thetarget.name]
                #thetgtcom = get_object_center(bpy.data.objects[obname.name])
                #   Determine current target object location in world space (center of mass or pivot based on UI selection)
                if (context.scene.proximityparent_targetpoint == 'Center of Mass') and (thistarget.type == 'MESH'):
                    thetgtcom = get_object_center(thistarget)
                    print(thistarget.name, '\t', thistarget.type, '\t', 'using COM location of ', str(thetgtcom))
                else:
                    thetgtcom = [thistarget.matrix_world.translation[0],thistarget.matrix_world.translation[1],thistarget.matrix_world.translation[2]]
                    print(thistarget.name, '\t', thistarget.type, '\t', 'using Pivot location of ', str(thetgtcom))
                thisdistance = get_distance(thetgtcom, thesrccom)
                if thisdistance <= thedistance:
                    thedistance = thisdistance
                    #print('thedistance is: ', thedistance)
                    tgtob = bpy.data.objects[thistarget.name]
            
            #print(srcob.name, ' ', context.scene.proximityparent_type, ' ', tgtob.name)
            #thetype = context.scene.proximityparent_type
            thetype = 'Parent/Child'
            if thetype == 'Parent/Child':
                srcob.parent = tgtob
                srcob.matrix_parent_inverse = tgtob.matrix_world.inverted()
            else:
                bpy.context.view_layer.objects.active = srcob
                if srcob.animation_data is not None and srcob.animation_data.action is not None:
                    thekeyframes = []
                    thefcurves = []
                    for fcrv in srcob.animation_data.action.fcurves:
                        if fcrv.data_path in supported_fcurves:
                            for thiskey in fcrv.keyframe_points:
                                if thiskey.co[0] not in thekeyframes:
                                    thekeyframes.append(thiskey.co[0])
                                    thefcurves.append(fcrv.data_path)
                    for thiskeyindex in range(len(thekeyframes)):
                        context.scene.frame_current = thekeyframes[thiskeyindex]
                        thisoffsetmatrix = srcob.matrix_world - tgtob.matrix_world
                        srcob.location = thisoffsetmatrix.to_translation()
                        srcob.keyframe_insert(thefcurves[thiskeyindex], frame=thekeyframes[thiskeyindex])
                else:
                    thisoffsetmatrix = srcob.matrix_world - tgtob.matrix_world
                    srcob.location = thisoffsetmatrix.to_translation()
                obconst = srcob.constraints.new(type='CHILD_OF')
                obconst.target = context.scene.objects.get(tgtob.name)
        bpy.context.scene.frame_current = thecurrentframe
        print('FINISHED')
        return{'FINISHED'}

#  BUTTON BUTTON_OT_proximityparent_target
class BUTTON_OT_proximityparent_target(bpy.types.Operator):
    '''SET/SELECT current target array'''
    bl_idname = "proximityparent.target"
    bl_label = "Tag Target(s)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        numsel = 0
        numsel = len(context.selected_objects)
        numstored = len(context.scene.BUTTON_OT_proximityparent_target)
        # ignore objects in thesource array
        if (numstored > 0) and (numsel > 0):
            bpy.ops.object.select_all(action='DESELECT')
            for a in range(numstored):
                bpy.ops.object.select_pattern(pattern=context.scene.BUTTON_OT_proximityparent_target[a].name)
        elif (numstored == 0) and (numsel >= 1):
            for a in context.selected_objects:
                newitem = context.scene.BUTTON_OT_proximityparent_target.add()
                newitem.name = a.name
        elif (numstored > 0) and (numsel == 0):
            bpy.ops.object.select_all(action='DESELECT')
            for a in range(numstored):
                bpy.ops.object.select_pattern(pattern=context.scene.BUTTON_OT_proximityparent_target[a].name)
        else:
            context.scene.BUTTON_OT_proximityparent_target.clear()
        
        # update target button label
        if (len(context.scene.BUTTON_OT_proximityparent_target) >= 1):
            self.__class__.bl_label = (str(len(context.scene.BUTTON_OT_proximityparent_target))+" target(s)")
        else:
            self.__class__.bl_label = "Tag Target(s)"
        self.report({'INFO'}, self.__class__.bl_label)
        
        return{'FINISHED'}

#   BUTTON BUTTON_OT_proximityparent_cleartargets
class BUTTON_OT_proximityparent_cleartargets(bpy.types.Operator):
    '''Clear any previously tagged objects.'''
    bl_idname = "proximityparent.cleartgt"
    bl_label = "X"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        tempsel = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.BUTTON_OT_proximityparent_target.clear()
        bpy.ops.proximityparent.target()
        for a in tempsel:
            a.select_set(True)
        return{'FINISHED'}

#   PANEL VIEW3D_PT_proximityparent_panel
class VIEW3D_PT_proximityparent_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Proximity Parent "+vsn)
    bl_context = "objectmode"
    bl_category = 'Tangent'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        if (len(context.scene.BUTTON_OT_proximityparent_target) >= 1):
            tags = (str(len(context.scene.BUTTON_OT_proximityparent_target))+" target(s)")
        else:
            tags = BUTTON_OT_proximityparent_target.bl_label
        scn = context.scene
        layout = self.layout
        layout.separator()
        split = layout.split(factor=0.85, align=True)
        col = split.column(align=True)
        col.operator("proximityparent.target", text=(tags))
        col = split.column(align=True)
        col.operator("proximityparent.cleartgt", text=(BUTTON_OT_proximityparent_cleartargets.bl_label))
        row = layout.row()
        row.prop(context.scene, "proximityparent_targetpoint")
        #row = layout.row()
        #row.prop(context.scene, "proximityparent_type")
        row = layout.row()
        row.operator("proximityparent.gobutton", text=(BUTTON_OT_proximityparent_gobutton.bl_label))


#       REGISTER

classes = [ OBJECT_PG_proximityparent, BUTTON_OT_proximityparent_gobutton,
            BUTTON_OT_proximityparent_target, BUTTON_OT_proximityparent_cleartargets,
            VIEW3D_PT_proximityparent_panel ]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.proximityparent_targetpoint = bpy.props.EnumProperty \
        (
          name = 'Selected Point',
          description = "Select whether to use Selected Center Of Mass OR Selected Object Pivot point.   Non-mesh Targets will always use the Target Pivot location.",
          items = (('COM', 'Center Of Mass', 'Use selected object\'s (source object) averaged vertex position to find closest Target.'),
                   ('Pivot', 'Pivot', 'Use the selected object\'s (source object) pivot point to find the nearest Target location.')
                  ),
          default = 'COM'
        )
    bpy.types.Scene.BUTTON_OT_proximityparent_target = bpy.props.CollectionProperty(type=OBJECT_PG_proximityparent)
    #bpy.types.Scene.proximityparent_type = bpy.props.EnumProperty \
    #    (
    #      name = 'Connection Type',
    #      description = 'Use transform constraint or parent/child relationship.',
    #      items = (('Constraint', 'Constraint', 'Constrain and ALIGN geometry of selected object to nearest Target.\nOverrides object offset and aligns to closest target.'),
    #               ('Parent/Child', 'Parent/Child', 'Normal Parent/Child relationship between Target and nearest source.\nRetains object offset from closest target.')
    #              ),
    #      default = 'Parent/Child'
    #    )


#       UNREGISTER
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
    del bpy.types.Scene.proximityparent_targetpoint
    #del bpy.types.Scene.proximityparent_targets
    del bpy.types.Scene.proximityparent_type
    

if __name__ == "__main__":
    register()
