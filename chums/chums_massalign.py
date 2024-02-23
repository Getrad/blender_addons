######################## NOTES ##############################
# v1.4
# added simple align, to quickly align selected to active
# v1.5
# added simple parent/constraint align selected to active
# V4.0
# updated to Blender 4.1.0 beta
# fixed bug where multiple inactive selections don't properly
#    link/constrain to active object in the quick align area

bl_info = {
    "name": "MassAlign",
    "author": "Conrad Dueck",
    "version": (4,0),
    "blender": (4, 1, 0),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Align one set of objects to another.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}


import bpy, random
from bpy import context
from random import randint


####    GLOBAL VARIABLES    ####
vsn = '4.0'
basictrs = ['location','rotation_euler','scale']


####    CLASSES    ####
#   PROPERTY_GROUP OBJECT_PG_mass_align
class OBJECT_PG_mass_align(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="test prop", default="unknown")
#bpy.utils.register_class(OBJECT_PG_mass_align)

#   OPERATOR BUTTON_OT_clear_src_button
class BUTTON_OT_clear_src_button(bpy.types.Operator):
    '''Clear any previously tagged SOURCE objects.'''
    bl_idname = "massalign.clearsrc"
    bl_label = "X"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        tempsel = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.thesource.clear()
        bpy.ops.massalign.source()
        for a in tempsel:
            a.select_set(True)
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_clear_tgt_button
class BUTTON_OT_clear_tgt_button(bpy.types.Operator):
    '''Clear any previously tagged TARGET objects.'''
    bl_idname = "massalign.cleartgt"
    bl_label = "X"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        tempsel = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.thetarget.clear()
        bpy.ops.massalign.target()
        for a in tempsel:
            a.select_set(True)
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_source_button
class BUTTON_OT_source_button(bpy.types.Operator):
    '''SET/SELECT current source array'''
    bl_idname = "massalign.source"
    bl_label = "Tag Source(s)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        numsel = 0
        numsel = len(context.selected_objects)
        numstored = len(context.scene.thesource)
        # ignoreobjects in thetargetarray
        if (numstored > 0) and (numsel > 0):
            bpy.ops.object.select_all(action='DESELECT')
            for a in range(numstored):
                bpy.ops.object.select_pattern(pattern=context.scene.thesource[a].name)
        elif (numstored == 0) and (numsel >= 1):
            for a in context.selected_objects:
                if not a.name in context.scene.thetarget.keys():
                    newitem = context.scene.thesource.add()
                    newitem.name = a.name
        elif (numstored > 0) and (numsel == 0):
            bpy.ops.object.select_all(action='DESELECT')
            for a in range(numstored):
                bpy.ops.object.select_pattern(pattern=context.scene.thesource[a].name)
        else:
            context.scene.thesource.clear()
        # update source button label
        if (len(context.scene.thesource)) >= 1:
            self.__class__.bl_label = (str(len(context.scene.thesource))+" source(s)")
        else:
            self.__class__.bl_label = "Tag Source(s)"
        self.report({'INFO'}, self.__class__.bl_label)
        
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_target_button
class BUTTON_OT_target_button(bpy.types.Operator):
    '''SET/SELECT current target array'''
    bl_idname = "massalign.target"
    bl_label = "Tag Target(s)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        numsel = 0
        numsel = len(context.selected_objects)
        numstored = len(context.scene.thetarget)
        # ignore objects in thesource array
        if (numstored > 0) and (numsel > 0):
            bpy.ops.object.select_all(action='DESELECT')
            for a in range(numstored):
                bpy.ops.object.select_pattern(pattern=context.scene.thetarget[a].name)
        elif (numstored == 0) and (numsel >= 1):
            for a in context.selected_objects:
                if not a.name in context.scene.thesource.keys():
                    newitem = context.scene.thetarget.add()
                    newitem.name = a.name
        elif (numstored > 0) and (numsel == 0):
            bpy.ops.object.select_all(action='DESELECT')
            for a in range(numstored):
                bpy.ops.object.select_pattern(pattern=context.scene.thetarget[a].name)
        else:
            context.scene.thetarget.clear()
        # update target button label
        if (len(context.scene.thetarget)) >= 1:
            self.__class__.bl_label = (str(len(context.scene.thetarget))+" target(s)")
        else:
            self.__class__.bl_label = "Tag Target(s)"
        self.report({'INFO'}, self.__class__.bl_label)
        
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_go_button
class BUTTON_OT_go_button(bpy.types.Operator):
    '''Align the source tagged objects to the target tagged objects.'''
    bl_idname = "massalign.go"
    bl_label = "Go!"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thematched = 0
        thesourcecount = (len(context.scene.thesource)-1)
        theconstrainedx = []
        theconstrainedy = []
        if (len(context.scene.thesource) >= 1) and (len(context.scene.thetarget) >= 1):
            ## get the number of objects to align (therange), using thetarget count if add instances is enabled, or thesource count if not.
            if bpy.context.scene.cdma_add:
                therange = len(context.scene.thetarget)
            else:
                therange = len(context.scene.thesource)
            ## if add instances is enabled, instance random source objects and add them to thesource until there are enough (matching therange)
            if therange > len(context.scene.thesource):
                for thecounter in range(0, therange):
                    ## Set thissource object based on whether cycling thru source array or picking from thesource based on Cycle or not
                    if thecounter > thesourcecount:
                        if bpy.context.scene.cdma_cycle:
                            ## if CYCLE is turned on, get the next object in the source list
                            thisrand = int((thecounter-((int(thecounter/(thesourcecount + 1)))*(thesourcecount + 1))))
                        else:
                            ## otherwise, pick a random object from the source array
                            thisrand = randint(0, (len(context.scene.thesource)-1))
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.ops.object.select_pattern(pattern=(context.scene.thesource[thisrand].name))
                        bpy.ops.object.duplicate(linked=True, mode='DUMMY')
                        thissource = bpy.context.selected_objects[0]
                        newitem = context.scene.thesource.add()
                        newitem.name = thissource.name
            thesourcecount = (len(context.scene.thesource)-1)
            ## use therange to go thru thetarget array and align thesource objects
            for thecounter in range(0, therange):
                ## define thissource as thecounter index of thesource array
                thissource = bpy.data.objects[context.scene.thesource[thecounter].name]
                print('\nthissource = ', thissource.name)
                
                ## find a target object to align the source object
                ## if we have more targets than the current source object count (and add instances is NOT enabled)
                if (not bpy.context.scene.cdma_random) and (len(context.scene.thetarget) >= len(context.scene.thesource)):
                    thistarget = bpy.data.objects[context.scene.thetarget[thecounter].name]
                    
                ## less targets than sources and we're not randomizing targets, need to loop back to start of target object array
                elif (not bpy.context.scene.cdma_random) and (len(context.scene.thetarget) < len(context.scene.thesource)):
                    if thematched >= len(context.scene.thetarget):
                        thematched = 0
                        thistarget = bpy.data.objects[context.scene.thetarget[thematched].name]
                        thematched += 1
                    else:
                        thistarget = bpy.data.objects[context.scene.thetarget[thematched].name]
                        thematched += 1
                ## truly random targeting
                else:
                    b = randint(0, (len(context.scene.thetarget)-1))
                    thistarget = bpy.data.objects[context.scene.thetarget[b].name]
                    while thistarget == thissource and (thematched < therange):
                        b = randint(0, (len(context.scene.thetarget)-1))
                        thistarget = bpy.data.objects[context.scene.thetarget[b].name]
                        thematched += 1
                print('thistarget = ', thistarget.name)
                
                print("bpy.context.scene.cdma_constrain = ", bpy.context.scene.cdma_constrain)
                ## CONSTRAIN
                if bpy.context.scene.cdma_constrain == 'constrain':
                    print('constraining ', thissource.name, ' to ', thistarget.name)
                    bpy.context.view_layer.objects.active = thissource
                    ## constraints inherently handle the alignment by overriding the local transforms on thissource
                    ## specific alignment not required
                    ## use a COPY_TRANSFORMS constraint if location, rotation and scale are enabled
                    if (bpy.context.scene.cdma_location) and (bpy.context.scene.cdma_rotation) and (bpy.context.scene.cdma_scale):
                        if not(thissource in theconstrainedx):
                            bpy.context.view_layer.objects.active = thissource
                            objs = thissource.constraints.new(type='COPY_TRANSFORMS')
                            objs.name = 'MA_CopyTransforms'
                            objs.target = context.scene.objects.get(thistarget.name)
                            theconstrainedx.append(thissource)
                        else:
                            if thissource.constraints['MA_CopyTransforms']:
                                thissource.constraints['MA_CopyTransforms'].target = context.scene.objects.get(thistarget.name)
                    ## use COPY_LOCATION, COPY_ROTATION, COPY_SCALE constraints as needed if not all transforms are selected
                    else:
                        if not(thissource in theconstrainedy):
                            if (bpy.context.scene.cdma_location):
                                bpy.context.view_layer.objects.active = thissource
                                objs = thissource.constraints.new(type='COPY_LOCATION')
                                objs.name = 'MA_CopyLocation'
                                objs.target = context.scene.objects.get(thistarget.name)
                            if (bpy.context.scene.cdma_rotation):
                                bpy.context.view_layer.objects.active = thissource
                                objs = thissource.constraints.new(type='COPY_ROTATION')
                                objs.name = 'MA_CopyRotation'
                                objs.target = context.scene.objects.get(thistarget.name)
                            if (bpy.context.scene.cdma_scale):
                                bpy.context.view_layer.objects.active = thissource
                                objs = thissource.constraints.new(type='COPY_SCALE')
                                objs.name = 'MA_CopyScale'
                                objs.target = context.scene.objects.get(thistarget.name)
                            theconstrainedy.append(thissource)
                        else:
                            if thissource.constraints['MA_CopyLocation']:
                                thissource.constraints['MA_CopyLocation'].target = context.scene.objects.get(thistarget.name)
                            if thissource.constraints['MA_CopyRotation']:
                                thissource.constraints['MA_CopyRotation'].target = context.scene.objects.get(thistarget.name)
                            if thissource.constraints['MA_CopyScale']:
                                thissource.constraints['MA_CopyScale'].target = context.scene.objects.get(thistarget.name)
                ## Align thissource to thistarget and PARENT
                elif bpy.context.scene.cdma_constrain == 'parent':
                    print('as it prevents accurate temporal alignment, removing any local animation from thissource ', thissource.name)
                    if thissource.animation_data is not None and thissource.animation_data.action is not None:
                        for fcrv in thissource.animation_data.action.fcurves:
                            if fcrv.data_path in basictrs:
                                thissource.animation_data.action.fcurves.remove(fcrv)
                    print('aligning ', thissource.name, ' to ', thistarget.name)
                    if bpy.context.scene.cdma_location:
                        thissource.location = thistarget.location
                    if bpy.context.scene.cdma_rotation:
                        thissource.rotation_euler = thistarget.rotation_euler
                    if bpy.context.scene.cdma_scale:
                        thissource.scale = thistarget.scale
                    print('parenting ', thissource.name, ' to ', thistarget.name)
                    thissource.parent = thistarget
                    thissource.matrix_parent_inverse = thistarget.matrix_world.inverted()
                ## Align thissource to thistarget ONLY
                else:
                    print('only aligning ', thissource.name, ' to ', thistarget.name)
                    if bpy.context.scene.cdma_location:
                        thissource.location = thistarget.location
                    if bpy.context.scene.cdma_rotation:
                        thissource.rotation_euler = thistarget.rotation_euler
                    if bpy.context.scene.cdma_scale:
                        thissource.scale = thistarget.scale
            for ob in bpy.context.scene.thesource:
                ob.select = True
        else:
            print('Ensure objects are tagged for BOTH source and target')
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_simple_align_only
class BUTTON_OT_simple_align_only(bpy.types.Operator):
    '''Quickly align the SELECTED objects to the ACTIVE object.'''
    bl_idname = "massalign.go_simple"
    bl_label = "Simple Align SELECTED to ACTIVE!"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thesourceobjs = []
        theactiveobj = []
        
        theactiveobj = bpy.context.view_layer.objects.active
        for ob in bpy.context.selected_objects:
            if not(ob == theactiveobj):
                thesourceobjs.append(ob)
        for thissource in thesourceobjs:
            print('simple aligning ', thissource.name, ' to ', theactiveobj.name)
            if bpy.context.scene.cdma_location:
                thissource.location = theactiveobj.location
            if bpy.context.scene.cdma_rotation:
                thissource.rotation_euler = theactiveobj.rotation_euler
            if bpy.context.scene.cdma_scale:
                thissource.scale = theactiveobj.scale
        return{'FINISHED'}
    
#   OPERATOR BUTTON_OT_simple_align_attach
class BUTTON_OT_simple_align_attach(bpy.types.Operator):
    '''Quickly align the SELECTED objects to the ACTIVE object and attach them using optional Parent/Child or Constraint.'''
    bl_idname = "massalign.go_simple_attach"
    bl_label = "Simple Align SELECTED and LINK to ACTIVE!"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thesourceobjs = []
        theactiveobj = bpy.context.view_layer.objects.active
        for ob in bpy.context.selected_objects:
            if not(ob == theactiveobj):
                thesourceobjs.append(ob)
        for thissource in thesourceobjs:
            print('simple aligning ', thissource.name, ' to ', theactiveobj.name)
            if bpy.context.scene.cdma_location:
                thissource.location = theactiveobj.location
            if bpy.context.scene.cdma_rotation:
                thissource.rotation_euler = theactiveobj.rotation_euler
            if bpy.context.scene.cdma_scale:
                thissource.scale = theactiveobj.scale
            if bpy.context.scene.cdma_constrain == 'constrain':
                print('constraining ', thissource.name, ' to ', theactiveobj.name)
                bpy.context.view_layer.objects.active = thissource
                #if (bpy.context.scene.cdma_location) and (bpy.context.scene.cdma_rotation) and (bpy.context.scene.cdma_scale):
                if (bpy.context.scene.cdma_location):
                    objs = thissource.constraints.new(type='COPY_LOCATION')
                    objs.name = 'MA_CopyLocation'
                    objs.target = context.scene.objects.get(theactiveobj.name)
                if (bpy.context.scene.cdma_rotation):
                    objs = thissource.constraints.new(type='COPY_ROTATION')
                    objs.name = 'MA_CopyRotation'
                    objs.target = context.scene.objects.get(theactiveobj.name)
                if (bpy.context.scene.cdma_scale):
                    objs = thissource.constraints.new(type='COPY_SCALE')
                    objs.name = 'MA_CopyScale'
                    objs.target = context.scene.objects.get(theactiveobj.name)
            else:
                print('parenting ', thissource.name, ' to ', theactiveobj.name)
                thissource.parent = theactiveobj
                thissource.matrix_parent_inverse = theactiveobj.matrix_world.inverted()
        return{'FINISHED'}
    
#   PANEL VIEW3D_PT_mass_align_panel
class VIEW3D_PT_mass_align_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Mass Align "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        if (len(context.scene.thesource) >= 1):
            srctags = (str(len(context.scene.thesource))+" source(s)")
        else:
            srctags = BUTTON_OT_source_button.bl_label
        if (len(context.scene.thetarget) >= 1):
            tgttags = (str(len(context.scene.thetarget))+" target(s)")
        else:
            tgttags = BUTTON_OT_target_button.bl_label
        obj = context.selected_objects
        layout = self.layout
        split = layout.split(factor=0.75, align=True)
        col = split.column()
        col.label(text="Sel. Count:", icon='OBJECT_DATA')
        col = split.column()
        col.label(text=str(len(obj)))
        split = layout.split(factor=0.85, align=True)
        col = split.column(align=True)
        col.operator("massalign.source", text=srctags)
        col = split.column(align=True)
        col.operator("massalign.clearsrc", text=(BUTTON_OT_clear_src_button.bl_label))
        col = layout.column()
        col.prop(context.scene, "cdma_constrain")
        col.prop(context.scene, "cdma_add")
        col.prop(context.scene, "cdma_cycle")
        layout.separator()
        split = layout.split(factor=0.85, align=True)
        col = split.column(align=True)
        col.operator("massalign.target", text=tgttags)
        col = split.column(align=True)
        col.operator("massalign.cleartgt", text=(BUTTON_OT_clear_tgt_button.bl_label))
        col = layout.column()
        col.prop(context.scene, "cdma_random")
        layout.separator()
        col = layout.column()
        col.label(text="Align:")
        col.prop(context.scene, "cdma_location")
        col.prop(context.scene, "cdma_rotation")
        col.prop(context.scene, "cdma_scale")
        layout.separator()
        layout.operator("massalign.go", text=(BUTTON_OT_go_button.bl_label))
        layout.operator("massalign.go_simple", text=(BUTTON_OT_simple_align_only.bl_label))
        layout.operator("massalign.go_simple_attach", text=(BUTTON_OT_simple_align_attach.bl_label))
        


#       REGISTER

classes = [ OBJECT_PG_mass_align, VIEW3D_PT_mass_align_panel,
            BUTTON_OT_clear_src_button, BUTTON_OT_clear_tgt_button, 
            BUTTON_OT_source_button, BUTTON_OT_target_button, 
            BUTTON_OT_go_button, BUTTON_OT_simple_align_only, 
            BUTTON_OT_simple_align_attach ]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.cdma_constrain = bpy.props.EnumProperty(
        name="Parent/Constrain",
        description="Optionally constrain or paarent the source to the it's alignment target.",
        items=[ ('align', "Align Only", "Just align, don\'t connect."),
                ('parent', "Parent", "Connect the aligned source object to the target object via parenting"),
                ('constrain', "Constrain", "Connect the aligned source object to the target object via transform constraint"),
               ]
        )
    bpy.types.Scene.cdma_add = bpy.props.BoolProperty \
        (
        name = "Add Instances",
        description = "Generate instanced copies of source array objects to align all targets",
        default = False
        )
    bpy.types.Scene.cdma_cycle = bpy.props.BoolProperty \
        (
          name = "Cycle",
          description = "ON cycles through array for instances, OFF adds random source instances",
          default = False
        )
    bpy.types.Scene.cdma_random = bpy.props.BoolProperty \
        (
          name = "Random Targets",
          description = "Align to random targets vs using array order. WARNING: this can target the same object mulitiple times.",
          default = False
        )
    bpy.types.Scene.cdma_location = bpy.props.BoolProperty \
        (
          name = "Location",
          description = "Align Location",
          default = True
        )
    bpy.types.Scene.cdma_rotation = bpy.props.BoolProperty \
        (
          name = "Rotation",
          description = "Align Rotation",
          default = True
        )
    bpy.types.Scene.cdma_scale = bpy.props.BoolProperty \
        (
          name = "Scale",
          description = "Align Scale",
          default = True
        )
    bpy.types.Scene.thesource = bpy.props.CollectionProperty(type=OBJECT_PG_mass_align)
    bpy.types.Scene.thetarget = bpy.props.CollectionProperty(type=OBJECT_PG_mass_align)


#       UNREGISTER
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
    del bpy.types.Scene.cdma_add
    del bpy.types.Scene.cdma_constrain
    del bpy.types.Scene.cdma_random
    del bpy.types.Scene.cdma_cycle
    del bpy.types.Scene.cdma_location
    del bpy.types.Scene.cdma_rotation
    del bpy.types.Scene.cdma_scale
    del bpy.types.Scene.thesource
    del bpy.types.Scene.thetarget
    

if __name__ == "__main__":
    register()
    
