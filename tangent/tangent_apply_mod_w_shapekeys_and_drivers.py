bl_info = {
    "name": "Apply Mod w/Shapekeys",
    "author": "james paskaruk",
    "version": (0,0,6),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > Tangent",
    "description": "Apply Modifier when shapekeys/drivers exist.",
    "warning": "",
    #"wiki_url": "",
    "tracker_url": "",
    "category": "Tangent"}
    
import bpy

### Functions 


### Classes
#   OPERATOR applymodwshapekeys APPLY
class BUTTON_OT_applymodwshapekeysapplymodifier(bpy.types.Operator):
    '''apply Modifier'''
    bl_idname = "applymodwshapekeys.applymodifier" 
    bl_label = "Select & Apply"
    bl_options = {'REGISTER', 'UNDO'}
    
    prop0: bpy.props.BoolProperty(name='prop0')
    prop1: bpy.props.BoolProperty(name='prop1')
    prop2: bpy.props.BoolProperty(name='prop2')
    prop3: bpy.props.BoolProperty(name='prop3')
    prop4: bpy.props.BoolProperty(name='prop4')
    prop5: bpy.props.BoolProperty(name='prop5')
    prop6: bpy.props.BoolProperty(name='prop6')
    prop7: bpy.props.BoolProperty(name='prop7')
    prop8: bpy.props.BoolProperty(name='prop8')
    prop9: bpy.props.BoolProperty(name='prop9')
    
        
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        proplist = [self.prop0, self.prop1, self.prop2, self.prop3, self.prop4, self.prop5, self.prop6, self.prop7, self.prop8, self.prop9]
        print(str(proplist))
        targetObject = bpy.context.active_object
        basisname = targetObject.data.shape_keys.key_blocks[0].name
        
        if targetObject.type != 'MESH':
            self.report({'ERROR_INVALID_INPUT'}, "Active object must be a mesh!")
            return {'CANCELLED'}
        elif sum(proplist) > 1:
            self.report({'ERROR_INVALID_INPUT'}, "Only one Modifier can be applied at a time.")
            return {'CANCELLED'}
        elif sum(proplist) == 0:
            self.report({'ERROR_INVALID_INPUT'}, "Please choose a modifier.")
            return {'CANCELLED'}
        else:
            count = 0
            for prop in proplist:
                if prop == True:
                    modToApply = bpy.context.active_object.modifiers[count]
                count += 1
            print(modToApply.name + " will be applied!")
            
            origName = targetObject.name
            targetObject.name = 'DUPLICATING'
            print(targetObject.data.shape_keys.key_blocks.items())

            ### Store driver info, if Drivers exist.
            drivers = {}
            try:
                if len(targetObject.data.shape_keys.animation_data.drivers) > 0:
                    for drv in targetObject.data.shape_keys.animation_data.drivers:
                        drdict = {}
                        drdict['expression'] = drv.driver.expression
                        drdict['vartype'] = drv.driver.variables[0].type
                        drdict['vartargetid'] = drv.driver.variables[0].targets[0].id
                        drdict['vartargetdata_path'] = drv.driver.variables[0].targets[0].data_path
                        shapekey = drv.data_path.split('[')[1][1:].split(']')[0][:-1]
                        drivers[shapekey] = drdict
                print("Driver info stored:")
            except:
                pass
            print(drivers)

            ### Duplicate Objects for keys, remove extraneous keys
            print(targetObject.data.shape_keys.key_blocks.items())
            for key in targetObject.data.shape_keys.key_blocks:
                if key.name == basisname:
                    pass
                else:
                    bpy.ops.object.select_all(action='DESELECT')
                    targetObject.select_set(True)
                    bpy.ops.object.duplicate()
                    bpy.ops.object.select_all(action='DESELECT')
                    newOb = bpy.data.objects[targetObject.name + '.001']
                    newOb.name = targetObject.name + '____' + key.name
                    for newObKey in newOb.data.shape_keys.key_blocks:
                        if newObKey.name != key.name:
                            newOb.shape_key_remove(newObKey)
                    targetObject.shape_key_remove(key)
            print("There should be four of the active object at this point. bpy.data.objects:")
            for x in bpy.data.objects:
                print(x.name)

            ### Remove final key, apply modifier
            for obj in bpy.data.objects:
                print("Trying to remove final key from ", obj.name, obj.type)
                if targetObject.name in obj.name:
                    for key in obj.data.shape_keys.key_blocks:
                        obj.shape_key_remove(key)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=modToApply.name)
            #print("There should be no shapekeys. bpy.data.shape_keys[0].key_blocks.items:")
            #print(bpy.data.shape_keys[0].key_blocks.items())
            #print("There should be four of the active object at this point. bpy.data.objects:")
            #print(bpy.data.objects.items())

            ### Re-add shapekeys, set selected and active objects for join_shapes Operator
            targetObject.shape_key_add(name=basisname)
            for obj in bpy.data.objects:
                if '____' in obj.name:
                    keyname = obj.name.split('____')[-1]
                    obj.shape_key_add(name=keyname)
                    obj.select_set(True)
            bpy.context.view_layer.objects.active = targetObject

            ### Join shapes to original (active) object
            bpy.ops.object.join_shapes()
            #print("targetObject should now have shapekeys. targetObject.data.shape_keys.key_blocks.items():")
            #print(targetObject.data.shape_keys.key_blocks.items())

            ### Remove duplicate holder objects from scene
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.data.objects:
                if '____' in obj.name:
                    obj.select_set(True)
            bpy.ops.object.delete()
            #print("Holder objects should now be gone. bpy.data.objects:")
            #print(bpy.data.objects.items())

            ### Clean up shapekey names, restore object name
            targetObject.name = origName
            #print("Target object name: " + targetObject.name + "   " + origName)
            for key in targetObject.data.shape_keys.key_blocks:
                if '____' in key.name:
                    key.name = key.name.split('____')[-1]
            #print("Names should now be restored to original. bpy.data.objects:")
            #print(bpy.data.objects.items())
            #print("targetObject.data.shape_keys.key_blocks.items():")
            #print(targetObject.data.shape_keys.key_blocks.items())

            ### Restore driver connections, if extant
            if len(drivers) > 0:
                count = 0
                for shky in drivers:
                    targetObject.data.shape_keys.key_blocks[shky].driver_add("value")
                    targetObject.data.shape_keys.animation_data.drivers[count].driver.expression = drivers[shky]['expression']
                    targetObject.data.shape_keys.animation_data.drivers[count].driver.variables.new()
                    targetObject.data.shape_keys.animation_data.drivers[count].driver.variables[0].type = drivers[shky]['vartype']
                    targetObject.data.shape_keys.animation_data.drivers[count].driver.variables[0].targets[0].id = drivers[shky]['vartargetid']
                    targetObject.data.shape_keys.animation_data.drivers[count].driver.variables[0].targets[0].data_path = drivers[shky]['vartargetdata_path']
                    count += 1

        self.prop0 = False
        self.prop1 = False
        self.prop2 = False
        self.prop3 = False
        self.prop4 = False
        self.prop5 = False
        self.prop6 = False
        self.prop7 = False
        self.prop8 = False
        self.prop9 = False

        print('End of Execute:' + str(self.prop0) + ', ' + str(self.prop1) + ', ' + str(self.prop2) + ', ' + str(self.prop3) + ', ' + str(self.prop4) + ', ' + str(self.prop5) + ', ' + str(self.prop6) + ', ' + str(self.prop7) + ', ' + str(self.prop8) + ', ' + str(self.prop9))
        
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        modlist = []
        for mod in bpy.context.active_object.modifiers:
            modlist.append(mod.name)
        
        self.layout.label(text="Select Modifier to Apply:")
        try:
            self.layout.prop(self, "prop0", text=modlist[0])
        except:
            pass
        try:
            self.layout.prop(self, "prop1", text=modlist[1])
        except:
            pass
        try:
            self.layout.prop(self, "prop2", text=modlist[2])
        except:
            pass
        try:
            self.layout.prop(self, "prop3", text=modlist[3])
        except:
            pass
        try:
            self.layout.prop(self, "prop4", text=modlist[4])
        except:
            pass
        try:
            self.layout.prop(self, "prop5", text=modlist[5])
        except:
            pass
        try:
            self.layout.prop(self, "prop6", text=modlist[6])
        except:
            pass
        try:
            self.layout.prop(self, "prop7", text=modlist[7])
        except:
            pass
        try:
            self.layout.prop(self, "prop8", text=modlist[8])
        except:
            pass
        try:
            self.layout.prop(self, "prop9", text=modlist[9])
        except:
            pass
        
    
                
#   PANEL applymodwshapekeys
class VIEW3D_PT_applymodwshapekeys(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Apply Mod w/Shapekeys")
    bl_context = "objectmode"
    bl_category = 'Tangent'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.operator("applymodwshapekeys.applymodifier", text=(BUTTON_OT_applymodwshapekeysapplymodifier.bl_label))
        #layout.operator("applymodwshapekeys.apply", text=(BUTTON_OT_applymodwshapekeysapply.bl_label))


#   Registration
classes = ( BUTTON_OT_applymodwshapekeysapplymodifier, VIEW3D_PT_applymodwshapekeys )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
if __name__ == "__main__":
    register()
