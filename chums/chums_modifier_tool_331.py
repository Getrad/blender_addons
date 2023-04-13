# made in response to --
# Andy Carney request for an easy toggle for all scene wireframe modifiers
# v1.6 - add option to make single users for apply function
# v2.5 - update to blender 2.8
# v3.0 - for chums and up to 3.3
# v3.1 - patched view_layer bug; need to better address data level (maybe)



bl_info = {
    "name": "Modifier Tool",
    "author": "conrad dueck",
    "version": (0,3,1),
    "blender": (3, 30, 1),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Affect multiple scene or selected modifiers en masse.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

import bpy
from bpy import context

####    GLOBAL VARIABLES    ####
vsn = '3.1'

####    CLASSES    ####
#   OPERATOR BUTTON_OT_modtooldelete
class BUTTON_OT_modtooldelete(bpy.types.Operator):
    '''Delete all these modifiers.'''
    bl_idname = "modtool.delete"
    bl_label = "Delete"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thetype = bpy.context.scene.modtoolsel
        if bpy.context.scene.modtoolmode:
            theobjs = bpy.context.selected_objects
        else:
            theobjs = bpy.context.scene.objects
        for theobj in theobjs:
            themods = theobj.modifiers
            for themod in themods:
                if themod.type == thetype:
                    theobj.modifiers.remove(themod)
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_modtoolonview
class BUTTON_OT_modtoolonview(bpy.types.Operator):
    '''Turn ON these modifiers in viewport.'''
    bl_idname = "modtool.onview"
    bl_label = "On"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thetype = bpy.context.scene.modtoolsel
        if bpy.context.scene.modtoolmode:
            theobjs = bpy.context.selected_objects
        else:
            theobjs = bpy.context.scene.objects
        for theobj in theobjs:
            themods = theobj.modifiers
            for themod in themods:
                if themod.type == thetype:
                    themod.show_viewport = 1
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_modtooloffview
class BUTTON_OT_modtooloffview(bpy.types.Operator):
    '''Turn OFF these modifiers in viewport.'''
    bl_idname = "modtool.offview"
    bl_label = "Off"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thetype = bpy.context.scene.modtoolsel
        if bpy.context.scene.modtoolmode:
            theobjs = bpy.context.selected_objects
        else:
            theobjs = bpy.context.scene.objects
        for theobj in theobjs:
            themods = theobj.modifiers
            for themod in themods:
                if themod.type == thetype:
                    themod.show_viewport = 0
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_modtoolonrender
class BUTTON_OT_modtoolonrender(bpy.types.Operator):
    '''Turn ON these modifiers in render.'''
    bl_idname = "modtool.onrender"
    bl_label = "On"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thetype = bpy.context.scene.modtoolsel
        if bpy.context.scene.modtoolmode:
            theobjs = bpy.context.selected_objects
        else:
            theobjs = bpy.context.scene.objects
        for theobj in theobjs:
            themods = theobj.modifiers
            for themod in themods:
                if themod.type == thetype:
                    themod.show_render = 1
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_modtooloffrender
class BUTTON_OT_modtooloffrender(bpy.types.Operator):
    '''Turn OFF these modifiers in render.'''
    bl_idname = "modtool.offrender"
    bl_label = "Off"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thetype = bpy.context.scene.modtoolsel
        if bpy.context.scene.modtoolmode:
            theobjs = bpy.context.selected_objects
        else:
            theobjs = bpy.context.scene.objects
        for theobj in theobjs:
            themods = theobj.modifiers
            for themod in themods:
                if themod.type == thetype:
                    themod.show_render = 0
        
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_modtoolapply
class BUTTON_OT_modtoolapply(bpy.types.Operator):
    '''Apply these modifiers.'''
    bl_idname = "modtool.apply"
    bl_label = "Apply"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thetype = bpy.context.scene.modtoolsel
        if bpy.context.scene.modtoolmode:
            theobjs = bpy.context.selected_objects
        else:
            theobjs = bpy.context.scene.objects
        bpy.ops.object.select_all(action='DESELECT')
        for theobj in theobjs:
            themods = theobj.modifiers
            for themod in themods:
                if themod.type == thetype:
                    try:
                        bpy.context.view_layer.objects.active = theobj
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=themod.name)
                    except:
                        if bpy.context.scene.modtoolforcesingle:
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.context.view_layer.objects.active = theobj
                            theobj.select = True
                            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', obdata=True, object=True, material=False, texture=False, animation=False)
                        bpy.context.view_layer.objects.active = theobj
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=themod.name)
        if bpy.context.scene.modtoolmode:
            for theobj in theobjs:
                theobj.select_set(True)
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_modtoolselect
class BUTTON_OT_modtoolselect(bpy.types.Operator):
    '''Select just objects with these modifiers.'''
    bl_idname = "modtool.select"
    bl_label = "Select"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        thetype = bpy.context.scene.modtoolsel
        thelayerobjs = bpy.context.view_layer.objects
        if bpy.context.scene.modtoolmode:
            theobjs = bpy.context.selected_objects
        else:
            theobjs = bpy.context.scene.objects
        bpy.ops.object.select_all(action='DESELECT')
        for theobj in theobjs:
            themods = theobj.modifiers
            for themod in themods:
                if themod.type == thetype and theobj.name in thelayerobjs:
                    theobj.select_set(True)
                    bpy.context.view_layer.objects.active = theobj
        return{'FINISHED'}


#   PANEL VIEW3D_PT_modtoolmodtool
class VIEW3D_PT_modtoolmodtool(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Modifier Tool " + vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "modtoolmode")
        layout.separator()
        layout.prop(context.scene, "modtoolsel")
        layout.separator()
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="View")
        row.operator("modtool.onview", text=(BUTTON_OT_modtoolonview.bl_label))
        row.operator("modtool.offview", text=(BUTTON_OT_modtooloffview.bl_label))
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Render")
        row.operator("modtool.onrender", text=(BUTTON_OT_modtoolonrender.bl_label))
        row.operator("modtool.offrender", text=(BUTTON_OT_modtooloffrender.bl_label))
        layout.separator()
        layout.operator("modtool.apply", text=(BUTTON_OT_modtoolapply.bl_label))
        layout.prop(context.scene, "modtoolforcesingle")
        layout.operator("modtool.select", text=(BUTTON_OT_modtoolselect.bl_label))
        layout.operator("modtool.delete", text=(BUTTON_OT_modtooldelete.bl_label))
        

####    REGISTRATION    ####

classes = ( BUTTON_OT_modtooldelete, BUTTON_OT_modtoolselect, BUTTON_OT_modtoolapply, \
            BUTTON_OT_modtooloffrender, BUTTON_OT_modtoolonrender, BUTTON_OT_modtooloffview, \
            BUTTON_OT_modtoolonview, VIEW3D_PT_modtoolmodtool)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.modtoolsel = bpy.props.EnumProperty \
        (
          name = "",
          description = "Pick a modifier type",
          items = [("ARMATURE","Armature",""),
                   ("ARRAY","Array",""),
                   ("BEVEL","Bevel",""),
                   ("BOOLEAN","Boolean",""),
                   ("CAST","Cast",""),
                   ("CLOTH","Cloth",""),
                   ("CORRECTIVE_SMOOTH","Corrective Smooth",""),
                   ("CURVE","Curve",""),
                   ("DECIMATE","Decimate",""),
                   ("DISPLACE","Displace",""),
                   ("EDGE_SPLIT","Edge Split",""),
                   ("HOOK","Hook",""),
                   ("LAPLACIANSMOOTH","Laplacian Smooth",""),
                   ("LAPLACIANDEFORM","Laplacian Deform",""),
                   ("LATTICE","Lattice",""),
                   ("MASK","Mask",""),
                   ("MESH_DEFORM","Mesh Deform",""),
                   ("MIRROR","Mirror",""),
                   ("MULTIRES","MultiResolution",""),
                   ("NODES","Geometry Nodes",""),
                   ("OPENVDB","Open VDB",""),
                   ("REMESH","Remesh",""),
                   ("SCREW","Screw",""),
                   ("SHRINKWRAP","Shrinkwrap",""),
                   ("SIMPLE_DEFORM","Simple Deform",""),
                   ("SKIN","Skin",""),
                   ("SMOOTH","Smooth",""),
                   ("SOLIDIFY","Solidify",""),
                   ("SUBSURF","Subdivision Surface",""),
                   ("WARP","Warp",""),
                   ("WAVE","Wave",""),
                   ("WIREFRAME","WireFrame","")]
        )
    bpy.types.Scene.modtoolmode = bpy.props.BoolProperty \
        (
          name = "Only Selected",
          description = "Only act on selected objects",
          default = False
        )
    bpy.types.Scene.modtoolforcesingle = bpy.props.BoolProperty \
        (
          name = "Force Single User",
          description = "Force objects and object data to be single users to allow for applying modifiers",
          default = False
        )

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.modtoolsel
    del bpy.types.Scene.modtoolmode
    del bpy.types.Scene.modtoolforcesingle

if __name__ == "__main__":
    register()
