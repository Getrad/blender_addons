

bl_info = {
    "name": "Replace Names",
    "author": "conrad dueck",
    "version": (0,1,0),
    "blender": (4, 1, 0),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Replace one string with another in scene or selected objects, materials, uvs.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

import bpy, re
from bpy import context

####    GLOBAL VARIABLES    ####l
vsn = '1.0'


####    FUNCTIONS    ####
def replacenametrim(theobj, thehead, thetail):
    if thehead >= 1:
        theobj = theobj[thehead:]
    if thetail >= 1:
        theobj = theobj[:-(thetail)]
    return theobj

def replacemyname(thisobj, 
                  replacenameold, 
                  replacenamenew, 
                  replacenamecase,
                  replacenameobjdata):
    print('entering replacemyname')
    thecurrentname = thisobj.name
    thematerials = bpy.data.materials
    thedatacases = ['MESH']
    if replacenamecase:
        theoldstring = replacenameold
        thecurname = thecurrentname
    else:
        theoldstring = replacenameold.casefold()
        thecurname = thecurrentname.casefold()
    thisobj.name = thecurname.replace(theoldstring, replacenamenew)
    if (replacenameobjdata):
        print("handling enabled object data for\n thisobj: ", thisobj)
        if not(thisobj.name in thematerials):
            if (thisobj.type in thedatacases) and thisobj.data:
                thisobj.data.name = thisobj.name
                if thisobj.type == 'MESH':
                    thisobj.data.name = thisobj.data.name.replace('geo.', 'msh.')
    
    print('exiting replacemyname')

        
def presuf(thisobj,
           replacenameprefix, 
           replacenamesuffix, 
           replacenameobjdata):
    thematerials = bpy.data.materials
    thedatacases = ['MESH']
    print('Running presuf function')
    if len(replacenameprefix) >= 1:
        thisobj.name = replacenameprefix + thisobj.name
    if len(replacenamesuffix) >= 1:
        thisobj.name = thisobj.name + replacenamesuffix
    while '..' in thisobj.name:
        thisobj.name = thisobj.name.replace('..', '.')
    if replacenameobjdata:
        if not(thisobj.name in thematerials):
            if (thisobj.type in thedatacases) and thisobj.data:
                thisobj.data.name = thisobj.name
    
    return thisobj.name

    

####    CLASSES    ####
#   OPERATOR BUTTON_OT_replacenamereplace REPLACE
class BUTTON_OT_replacenamereplace(bpy.types.Operator):
    '''Replace Source string with Target string'''
    bl_idname = "replacename.replace"
    bl_label = "Replace"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if len(bpy.context.scene.replacenameold) >= 1:
            print('\n\nrunning REPLACE function\n\n')
            #   gather scene bone names
            thebonelist = []
            if len(bpy.data.armatures) >= 1:
                for thearm in bpy.data.armatures:
                    if (len(thearm.bones) >= 1):
                        for thebone in thearm.bones:
                            thebonelist.append(thebone.name)
            #   gather scene vertex group names
            thevtxlist = []
            for theobj in bpy.data.objects:
                if len(theobj.vertex_groups) >= 1:
                    for thevtx in theobj.vertex_groups:
                        theentry= (theobj.name + ';:;' + thevtx.name)
                        thevtxlist.append(theentry)
            #   gather scene collection names
            thecollections = []
            #   set testing object and collection arrays based on Only Selected user option
            if bpy.context.scene.replacenameselected:
                theobjs = bpy.context.selected_objects
                for thiscollection in bpy.data.collections:
                    if not(thiscollection.library):
                        allin = 0
                        for theobj in bpy.context.selected_objects:
                            if theobj.name in thiscollection.objects:
                                allin += 1
                                thecollections.append(thiscollection.name)
            else:
                theobjs = bpy.context.scene.objects
                for thiscollection in bpy.data.collections:
                    if not(thiscollection.library):
                        thecollections.append(thiscollection.name)
            
            #   collections
            if bpy.context.scene.replacenamecollections:
                print('\nfirst line of the function call in BUTTON_OT_replacenamereplace')
                for cnt in range(len(thecollections)):
                    print('thecount =', cnt)
                    thecollection = bpy.data.collections[thecollections[cnt]]
                    print('\nthecollection =', thecollection)
                    replacemyname(thecollection, bpy.context.scene.replacenameold, 
                                  bpy.context.scene.replacenamenew, 
                                  bpy.context.scene.replacenamecase,
                                  0)
            
            #   objects    
            for theobj in theobjs:
                #   reset thenewstring
                thenewstring = ""
                #   'Replace with' accepts a blank string to remove the search string
                thenewstring = bpy.context.scene.replacenamenew
                #   objects
                if ((theobj.type == "MESH") or (theobj.type == "EMPTY")) and bpy.context.scene.replacenameobjects:
                    replacemyname(theobj, bpy.context.scene.replacenameold, 
                                  bpy.context.scene.replacenamenew, 
                                  bpy.context.scene.replacenamecase,
                                  bpy.context.scene.replacenameobjdata)
                #   lights
                if (theobj.type == "LIGHT") and bpy.context.scene.replacenamelights:
                    replacemyname(theobj, bpy.context.scene.replacenameold, 
                                  bpy.context.scene.replacenamenew, 
                                  bpy.context.scene.replacenamecase,
                                  bpy.context.scene.replacenameobjdata)
                #   cameras
                if (theobj.type == "CAMERA") and bpy.context.scene.replacenamecameras:
                    replacemyname(theobj, bpy.context.scene.replacenameold, 
                                  bpy.context.scene.replacenamenew, 
                                  bpy.context.scene.replacenamecase,
                                  bpy.context.scene.replacenameobjdata)
                #   armatures
                if (theobj.type == "ARMATURE") and bpy.context.scene.replacenamebones:
                    replacemyname(theobj, bpy.context.scene.replacenameold, 
                                  bpy.context.scene.replacenamenew, 
                                  bpy.context.scene.replacenamecase,
                                  bpy.context.scene.replacenameobjdata)
                    #   bones within the armature   
                    if (len(theobj.data.bones) >= 1):
                        for thebone in theobj.data.bones:
                            if not(thebone.name in thevtxlist):
                                replacemyname(thebone, bpy.context.scene.replacenameold, 
                                              bpy.context.scene.replacenamenew, 
                                              bpy.context.scene.replacenamecase,
                                              0)
                            else:
                                for theentry in thevtxlist:
                                    thisobj = theentry.split(';:;')[0]
                                    thisvtx = theentry.split(';:;')[1]
                                    if thebone.name == thisvtx:
                                        print('SKIPPING ', thebone.name, ' in the ', theobj.name, ' armature, since it conflicts with a vertex group on ', thisobj)
                #   vertex groups
                if (theobj.type == 'MESH') and bpy.context.scene.replacenamevertexgroups and (len(theobj.vertex_groups) >= 1):
                    isitskinned = 0
                    theskinvertexgroups = []
                    therigname = ''
                    for themod in theobj.modifiers:
                        if themod.type == 'ARMATURE':
                            if themod.object:
                                therigname = themod.object.name
                                for thebone in themod.object.data.bones:
                                    theskinvertexgroups.append(thebone.name)
                    for thisvertexgroup in theobj.vertex_groups:
                        if not(thisvertexgroup.name in theskinvertexgroups):
                            replacemyname(thisvertexgroup, bpy.context.scene.replacenameold, 
                                          bpy.context.scene.replacenamenew, 
                                          bpy.context.scene.replacenamecase,
                                          0)
                        else:
                            print('SKIPPING ', thisvertexgroup.name, ' - it matches a bone in ', therigname, ' which is controlling ', theobj.name)
                #   empties
                if(theobj.type == "EMPTY") and bpy.context.scene.replacenameempty:
                    replacemyname(theobj, bpy.context.scene.replacenameold, 
                                  bpy.context.scene.replacenamenew, 
                                  bpy.context.scene.replacenamecase,
                                  bpy.context.scene.replacenameobjdata)
                #   lattices
                if(theobj.type == "LATTICE") and bpy.context.scene.replacenamelattice:
                    replacemyname(theobj, bpy.context.scene.replacenameold, 
                                  bpy.context.scene.replacenamenew, 
                                  bpy.context.scene.replacenamecase,
                                  bpy.context.scene.replacenameobjdata)
                #   materials
                if (theobj.type != 'ARMATURE') and bpy.context.scene.replacenamematerials and (len(theobj.material_slots) >=1 ):
                    thesemats = theobj.material_slots
                    themats = []
                    for themat in thesemats:
                        themats.append(themat.material)
                    for thismat in themats:
                        if (thismat):
                            replacemyname(thismat, bpy.context.scene.replacenameold, 
                                          bpy.context.scene.replacenamenew, 
                                          bpy.context.scene.replacenamecase,
                                          bpy.context.scene.replacenameobjdata)
                #   uv maps
                if (theobj.type == 'MESH') and bpy.context.scene.replacenameuvs and (len(theobj.data.uv_layers) >= 1):
                    for thisuvs in theobj.data.uv_layers:
                        replacemyname(thisuvs, bpy.context.scene.replacenameold, 
                                      bpy.context.scene.replacenamenew, 
                                      bpy.context.scene.replacenamecase,
                                      0)
                #   shape keys
                try:
                    if (theobj.type == 'MESH') and bpy.context.scene.replacenameshapekeys and (len(theobj.data.shape_keys.key_blocks) >= 1):
                        for thiskey in theobj.data.shape_keys.key_blocks:
                            replacemyname(thiskey, bpy.context.scene.replacenameold, 
                                          bpy.context.scene.replacenamenew, 
                                          bpy.context.scene.replacenamecase,
                                          0)
                except:
                    print('failed shape keys')
                #   curves
                if(theobj.type == "CURVE") and bpy.context.scene.replacenamecurves:
                    replacemyname(theobj, bpy.context.scene.replacenameold, 
                                  bpy.context.scene.replacenamenew, 
                                  bpy.context.scene.replacenamecase,
                                  bpy.context.scene.replacenameobjdata)
                
        return{'FINISHED'}

# OPERATOR BUTTON_OT_replacenameselect SELECT
class BUTTON_OT_replacenameselect(bpy.types.Operator):
    '''Replace Source string with Target string'''
    bl_idname = "replacename.select"
    bl_label = "Select"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('\n\nrunning SELECT function\n\n')
        thenewsel = []
        themats = []
        if bpy.context.scene.replacenameselected:
            theobjs = bpy.context.selected_objects
        else:
            theobjs = bpy.context.scene.objects
            themats = bpy.data.materials
        if bpy.context.scene.replacenamecase:
            theteststr = bpy.context.scene.replacenameold
        else:
            theteststr = bpy.context.scene.replacenameold.casefold()
        
        for theobj in theobjs:
            if not(theobj.is_library_indirect):
                if bpy.context.scene.replacenamecase:
                    thenamestr = theobj.name
                else:
                    thenamestr = theobj.name.casefold()
                #   objects
                if bpy.context.scene.replacenameobjects:
                    if (theteststr in thenamestr) and (theobj.type == "MESH"):
                        thenewsel.append(theobj.name)
                #   lights
                if bpy.context.scene.replacenamelights:
                    if (theteststr in thenamestr) and (theobj.type == "LIGHT"):
                        thenewsel.append(theobj.name)
                #   cameras
                if bpy.context.scene.replacenamecameras:
                    if (theteststr in thenamestr) and (theobj.type == "CAMERA"):
                        thenewsel.append(theobj.name)
                #   bones
                if bpy.context.scene.replacenamebones:
                    if (theteststr in thenamestr) and (theobj.type == "ARMATURE"):
                        thenewsel.append(theobj.name)
                #   empty
                if bpy.context.scene.replacenameempty:
                    if (theteststr in thenamestr) and (theobj.type == "EMPTY"):
                        thenewsel.append(theobj.name)
                #   lattice
                if bpy.context.scene.replacenamelattice:
                    if (theteststr in thenamestr) and (theobj.type == "LATTICE"):
                        thenewsel.append(theobj.name)
                #   materials
                if bpy.context.scene.replacenamematerials:
                    for theslot in theobj.material_slots:
                        themat = theslot.material
                        if bpy.context.scene.replacenamecase:
                            thematstr = themat.name
                        else:
                            thematstr = themat.name.casefold()
                        if theteststr in thematstr:
                            if theobj.name not in thenewsel:
                                thenewsel.append(theobj.name)
                #   uv maps
                if bpy.context.scene.replacenameuvs:
                    if (theobj.type == 'MESH') and (len(theobj.data.uv_layers) >= 1):
                        for thisuvs in theobj.data.uv_layers:
                            if bpy.context.scene.replacenamecase:
                                thenamestr = thisuvs.name
                                theteststr = bpy.context.scene.replacenameold
                            else:
                                thenamestr = thisuvs.name.casefold()
                                theteststr = bpy.context.scene.replacenameold.casefold()
                            if theteststr in thenamestr:
                                thenewsel.append(theobj.name)
                #   vertex groups
                if bpy.context.scene.replacenamevertexgroups:
                    if (theobj.type == 'MESH') and (len(theobj.vertex_groups) >= 1):
                        theskinvertexgroups = []
                        therigname = ''
                        for themod in theobj.modifiers:
                            if themod.type == 'ARMATURE':
                                if themod.object:
                                    therigname = themod.object.name
                                    for thebone in themod.object.data.bones:
                                        theskinvertexgroups.append(thebone.name)
                        for thisvertexgroups in theobj.vertex_groups:
                            if not(thisvertexgroups.name in theskinvertexgroups):
                                if bpy.context.scene.replacenamecase:
                                    thenamestr = thisvertexgroups.name
                                    theteststr = bpy.context.scene.replacenameold
                                else:
                                    thenamestr = thisvertexgroups.name.casefold()
                                    theteststr = bpy.context.scene.replacenameold.casefold()
                                if theteststr in thenamestr:
                                    thenewsel.append(theobj.name)
                            else:
                                print('SKIPPING ', thisvertexgroups.name, ' - it matches a bone in ', therigname, ' which is controlling ', theobj.name)
                #   shape keys
                if bpy.context.scene.replacenameshapekeys:
                    if (theobj.type == 'MESH') and (theobj.data.shape_keys) and (len(theobj.data.shape_keys.key_blocks) >= 1):
                        for thiskey in theobj.data.shape_keys.key_blocks:
                            if bpy.context.scene.replacenamecase:
                                thenamestr = thiskey.name
                                theteststr = bpy.context.scene.replacenameold
                            else:
                                thenamestr = thiskey.name.casefold()
                                theteststr = bpy.context.scene.replacenameold.casefold()
                            if theteststr in thenamestr:
                                thenewsel.append(theobj.name)
                #   curves
                if bpy.context.scene.replacenamecurves:
                    if (theobj.type == 'CURVE'):
                        if bpy.context.scene.replacenamecase:
                            thenamestr = theobj.name
                            theteststr = bpy.context.scene.replacenameold
                        else:
                            thenamestr = theobj.name.casefold()
                            theteststr = bpy.context.scene.replacenameold.casefold()
                        if theteststr in thenamestr:
                            thenewsel.append(theobj.name)
                
            bpy.ops.object.select_all(action='DESELECT')
            for a in thenewsel:
                bpy.ops.object.select_pattern(pattern=a)
        return{'FINISHED'}

# OPERATOR BUTTON_OT_replacenametrim TRIM
class BUTTON_OT_replacenametrim(bpy.types.Operator):
    '''Trim from head or tail of name, limited by checked object type and search string (if any)'''
    bl_idname = "replacename.trim"
    bl_label = "Trim"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('\n\nrunning TRIM function\n\n')
        #   check for selected only option
        if bpy.context.scene.replacenameselected:
            theobjs = bpy.context.selected_objects
            thecollections = []
            for thiscollection in bpy.data.collections:
                allin = 0
                for theobj in bpy.context.selected_objects:
                    if theobj.name in thiscollection.objects:
                        allin += 1
                if len(bpy.context.selected_objects) == allin:
                    thecollections.append(thiscollection)
        else:
            theobjs = bpy.context.scene.objects
            thecollections = bpy.data.collections
        #   collections
        if bpy.context.scene.replacenamecollections:
            for thecollection in thecollections:
                if not(thecollection.library):
                    thecollection.name = replacenametrim(thecollection.name, 
                                         bpy.context.scene.replacenamehead, 
                                         bpy.context.scene.replacenametail)
        #   objects
        for theobj in theobjs:
            if not(theobj.is_library_indirect):
                #   objects
                if bpy.context.scene.replacenameobjects:
                    if theobj.type == 'MESH':
                        theobj.name = replacenametrim(theobj.name, 
                                                      bpy.context.scene.replacenamehead, 
                                                      bpy.context.scene.replacenametail)
                        if bpy.context.scene.replacenameobjdata:
                            theobj.data.name = replacenametrim(theobj.data.name, 
                                                               bpy.context.scene.replacenamehead, 
                                                               bpy.context.scene.replacenametail)
                #   lights
                if bpy.context.scene.replacenamelights:
                    if theobj.type == 'LIGHT':
                        theobj.name = replacenametrim(theobj.name, 
                                                      bpy.context.scene.replacenamehead, 
                                                      bpy.context.scene.replacenametail)    
                #   cameras
                if bpy.context.scene.replacenamecameras:
                    if theobj.type == 'CAMERA':
                        theobj.name = replacenametrim(theobj.name, 
                                                      bpy.context.scene.replacenamehead, 
                                                      bpy.context.scene.replacenametail)    
                #   bones
                if bpy.context.scene.replacenamebones:
                    if theobj.type == 'ARMATURE':
                        theobj.name = replacenametrim(theobj.name, 
                                                      bpy.context.scene.replacenamehead, 
                                                      bpy.context.scene.replacenametail)
                        if (len(theobj.data.bones) >= 1):
                            for thebone in theobj.data.bones:
                                thebone.name = replacenametrim(thebone.name, 
                                                               bpy.context.scene.replacenamehead, 
                                                               bpy.context.scene.replacenametail)
                #   empty
                if bpy.context.scene.replacenameempty:
                    if theobj.type == 'EMPTY':
                        theobj.name = replacenametrim(theobj.name, 
                                                      bpy.context.scene.replacenamehead, 
                                                      bpy.context.scene.replacenametail)    
                #   lattice
                if bpy.context.scene.replacenamelattice:
                    if theobj.type == 'LATTICE':
                        theobj.name = replacenametrim(theobj.name, 
                                                      bpy.context.scene.replacenamehead, 
                                                      bpy.context.scene.replacenametail)    
                #   materials
                if bpy.context.scene.replacenamematerials:
                    for theslot in theobj.material_slots:
                        themat = theslot.material
                        themat.name = replacenametrim(themat.name, 
                                                      bpy.context.scene.replacenamehead, 
                                                      bpy.context.scene.replacenametail)    
                #   uv maps
                if bpy.context.scene.replacenameuvs:
                    if (theobj.type == 'MESH') and (len(theobj.data.uv_layers) >= 1):
                        for thisuvs in theobj.data.uv_layers:
                            thisuvs.name = replacenametrim(thisuvs.name, 
                                                           bpy.context.scene.replacenamehead, 
                                                           bpy.context.scene.replacenametail)    
                #   vertex groups
                if bpy.context.scene.replacenamevertexgroups:
                    if (theobj.type == 'MESH') and (len(theobj.vertex_groups) >= 1):
                        isitskinned = 0
                        theskinvertexgroups = []
                        therigname = ''
                        for themod in theobj.modifiers:
                            if themod.type == 'ARMATURE':
                                if themod.object:
                                    therigname = themod.object.name
                                    for thebone in themod.object.data.bones:
                                        theskinvertexgroups.append(thebone.name)
                        for thisvertexgroup in theobj.vertex_groups:
                            if not(thisvertexgroup.name in theskinvertexgroups):
                                thisvertexgroup.name = replacenametrim(thisvertexgroup.name, 
                                                                       bpy.context.scene.replacenamehead, 
                                                                       bpy.context.scene.replacenametail)
                            else:
                                print('SKIPPING ', thisvertexgroup.name, ' - it matches a bone in ', therigname, ' which is controlling ', theobj.name)
                #   shape keys
                if bpy.context.scene.replacenameshapekeys:
                    if (theobj.type == 'MESH') and (theobj.data.shape_keys) and (len(theobj.data.shape_keys.key_blocks) >= 1):
                        for thiskey in theobj.data.shape_keys.key_blocks:
                            thiskey.name = replacenametrim(thiskey.name, 
                                                           bpy.context.scene.replacenamehead, 
                                                           bpy.context.scene.replacenametail)    
                #   curves
                if bpy.context.scene.replacenamecurves:
                    if (theobj.type == 'CURVE'):
                        theobj.name = replacenametrim(theobj.name, 
                                                      bpy.context.scene.replacenamehead, 
                                                      bpy.context.scene.replacenametail) 
            
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_replacenamepresuf PRESUF
class BUTTON_OT_replacenamepresuf(bpy.types.Operator):
    '''Set Prefix or Suffix'''
    bl_idname = "replacename.presuf"
    bl_label = "Insert Prefix/Suffix"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('\n\nrunning PREFIX/SUFFIX function:  BUTTON_OT_replacenamepresuf\n\n')
        if bpy.context.scene.replacenamecase:
            thesearchstr = bpy.context.scene.replacenameold
        else:
            thesearchstr = bpy.context.scene.replacenameold.casefold()
        if bpy.context.scene.replacenameselected:
            theobjs = bpy.context.selected_objects
            thecollections = []
            for thiscollection in bpy.data.collections:
                allin = 0
                for theobj in bpy.context.selected_objects:
                    if theobj.name in thiscollection.objects:
                        if not(thiscollection in thecollections):
                            thecollections.append(thiscollection)
        else:
            theobjs = bpy.context.scene.objects
            thecollections = bpy.data.collections
        
        #   collections
        if bpy.context.scene.replacenamecollections:
            processcount = 0
            for thecollection in thecollections:
                thenewname = thecollection.name
                if not(thecollection.library):
                    print('BUTTON_OT_replacenamepresuf  COLLECTIONS  at ', thecollection.name)
                    if len(thesearchstr) >= 1:
                        if thesearchstr in thecollection.name:
                            thenewname = presuf(thecollection, bpy.context.scene.replacenameprefix,
                                   bpy.context.scene.replacenamesuffix, 
                                   0)
                    else:
                        thenewname = ''.join([bpy.context.scene.replacenameprefix, 
                                              thecollection.name, bpy.context.scene.replacenamesuffix])
                    thecollection.name = thenewname
                processcount += 1
                if processcount == len(bpy.data.collections):
                    break
                    
        #   objects
        for theobj in theobjs:
            # if the object is not indirect
            if not(theobj.is_library_indirect):
                print('BUTTON_OT_replacenamepresuf  OBJECTS  at ', theobj.name)
                mytype = theobj.type
                #   objects
                if bpy.context.scene.replacenameobjects:
                    if mytype == 'MESH':
                        if len(thesearchstr) >= 1:
                            if thesearchstr in theobj.name:
                                presuf(theobj, bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       bpy.context.scene.replacenameobjdata)
                        else:
                            presuf(theobj, bpy.context.scene.replacenameprefix, 
                                   bpy.context.scene.replacenamesuffix, 
                                   bpy.context.scene.replacenameobjdata)
                #   lights
                if bpy.context.scene.replacenamelights:
                    if mytype == 'LIGHT':
                        if len(thesearchstr) >= 1:
                            if thesearchstr in theobj.name:
                                presuf(theobj, bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       bpy.context.scene.replacenameobjdata)
                        else:
                            presuf(theobj, bpy.context.scene.replacenameprefix, 
                                   bpy.context.scene.replacenamesuffix, 
                                   bpy.context.scene.replacenameobjdata)
                #   cameras
                if bpy.context.scene.replacenamecameras:
                    if mytype == 'CAMERA':
                        if len(thesearchstr) >= 1:
                            if thesearchstr in theobj.name:
                                presuf(theobj, bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       bpy.context.scene.replacenameobjdata)
                        else:
                            presuf(theobj, bpy.context.scene.replacenameprefix, 
                                   bpy.context.scene.replacenamesuffix, 
                                   bpy.context.scene.replacenameobjdata)
                #   bones
                if bpy.context.scene.replacenamebones:
                    if mytype == 'ARMATURE':
                        if len(thesearchstr) >= 1:
                            if thesearchstr in theobj.name:
                                presuf(theobj, bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       bpy.context.scene.replacenameobjdata)
                        else:
                            presuf(theobj, bpy.context.scene.replacenameprefix, 
                                   bpy.context.scene.replacenamesuffix, 
                                   bpy.context.scene.replacenameobjdata)
                        if (len(theobj.data.bones) >= 1):
                            for thebone in theobj.data.bones:
                                if len(thesearchstr) >= 1:
                                    if thesearchstr in theobj.name:
                                        presuf(thebone, bpy.context.scene.replacenameprefix, 
                                               bpy.context.scene.replacenamesuffix, 
                                               bpy.context.scene.replacenameobjdata)
                                else:
                                    presuf(thebone, bpy.context.scene.replacenameprefix, 
                                           bpy.context.scene.replacenamesuffix, 
                                           0)
                #   empty
                if bpy.context.scene.replacenameempty:
                    if mytype == 'EMPTY':
                        if len(thesearchstr) >= 1:
                            if thesearchstr in theobj.name:
                                presuf(theobj, bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       bpy.context.scene.replacenameobjdata)
                        else:
                            presuf(theobj, bpy.context.scene.replacenameprefix, 
                                   bpy.context.scene.replacenamesuffix, 
                                   bpy.context.scene.replacenameobjdata)
                #   lattice
                if bpy.context.scene.replacenamelattice:
                    if mytype == 'LATTICE':
                        if len(thesearchstr) >= 1:
                            if thesearchstr in theobj.name:
                                presuf(theobj, bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       bpy.context.scene.replacenameobjdata)
                        else:
                            presuf(theobj, bpy.context.scene.replacenameprefix, 
                                   bpy.context.scene.replacenamesuffix, 
                                   bpy.context.scene.replacenameobjdata)
                
                #   materials
                if bpy.context.scene.replacenamematerials:
                    for theslot in theobj.material_slots:
                        themat = theslot.material
                        if themat:
                            if len(thesearchstr) >= 1:
                                if thesearchstr in themat.name:
                                    presuf(themat, bpy.context.scene.replacenameprefix, 
                                           bpy.context.scene.replacenamesuffix, 
                                           0)
                            else:
                                presuf(themat, bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       0)
                #   uv maps
                if bpy.context.scene.replacenameuvs:
                    if (mytype == 'MESH') and (len(theobj.data.uv_layers) >= 1):
                        for thisuvs in theobj.data.uv_layers:
                            if len(thesearchstr) >= 1:
                                if thesearchstr in thisuvs.name:
                                    presuf(thisuvs, 
                                           bpy.context.scene.replacenameprefix, 
                                           bpy.context.scene.replacenamesuffix, 
                                           0)
                            else:
                                presuf(thisuvs, 
                                       bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       0)
                #   vertex groups
                if bpy.context.scene.replacenamevertexgroups:
                    if (mytype == 'MESH') and (len(theobj.vertex_groups) >= 1):
                        isitskinned = 0
                        theskinvertexgroups = []
                        therigname = ''
                        for themod in theobj.modifiers:
                            if themod.type == 'ARMATURE':
                                if themod.object:
                                    therigname = themod.object.name
                                    for thebone in themod.object.data.bones:
                                        theskinvertexgroups.append(thebone.name)
                        for thisvertexgroup in theobj.vertex_groups:
                            if not(thisvertexgroup.name in theskinvertexgroups):
                                if len(thesearchstr) >= 1:
                                    if thesearchstr in thisvertexgroup.name:
                                        presuf(thisvertexgroup, 
                                               bpy.context.scene.replacenameprefix, 
                                               bpy.context.scene.replacenamesuffix, 
                                               0)
                                else:
                                    presuf(thisvertexgroup, 
                                           bpy.context.scene.replacenameprefix, 
                                           bpy.context.scene.replacenamesuffix, 
                                           0)
                            else:
                                print('SKIPPING ', thisvertexgroup.name, ' - it matches a bone in ', therigname, ' which is controlling ', theobj.name)
                #   shape keys
                if bpy.context.scene.replacenameshapekeys:
                    if (mytype == 'MESH') and (theobj.data.shape_keys) and (len(theobj.data.shape_keys.key_blocks) >= 1):
                        for thiskey in theobj.data.shape_keys.key_blocks:
                            if len(thesearchstr) >= 1:
                                if thesearchstr in thiskey.name:
                                    presuf(thiskey, 
                                           bpy.context.scene.replacenameprefix, 
                                           bpy.context.scene.replacenamesuffix, 
                                           0)
                            else:
                                presuf(thiskey, 
                                       bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       0)
                #   curves
                if bpy.context.scene.replacenamecurves:
                    if mytype == 'CURVE':
                        if len(thesearchstr) >= 1:
                            if thesearchstr in theobj.name:
                                presuf(theobj, 
                                       bpy.context.scene.replacenameprefix, 
                                       bpy.context.scene.replacenamesuffix, 
                                       bpy.context.scene.replacenameobjdata)
                        else:
                            presuf(theobj, 
                                   bpy.context.scene.replacenameprefix, 
                                   bpy.context.scene.replacenamesuffix, 
                                   bpy.context.scene.replacenameobjdata)
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_replacenamereset RESET
class BUTTON_OT_replacenamereset(bpy.types.Operator):
    '''Reset all the fields'''
    bl_idname = "replacename.reset"
    bl_label = "Reset ALL Fields"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.replacenamehead = 0
        bpy.context.scene.replacenametail = 0
        bpy.context.scene.replacenameold = ''
        bpy.context.scene.replacenamenew = ''
        bpy.context.scene.replacenameprefix = ''
        bpy.context.scene.replacenamesuffix = ''
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_replacenameall FILTER ALL
class BUTTON_OT_replacenameall(bpy.types.Operator):
    '''Turn all types ON'''
    bl_idname = "replacename.all"
    bl_label = "All Types"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.replacenameobjects = True
        bpy.context.scene.replacenamelights = True
        bpy.context.scene.replacenamecameras = True
        bpy.context.scene.replacenamecollections = True
        bpy.context.scene.replacenamebones = True
        bpy.context.scene.replacenameempty = True
        bpy.context.scene.replacenamelattice = True
        bpy.context.scene.replacenamematerials = True
        bpy.context.scene.replacenameuvs = True
        bpy.context.scene.replacenamevertexgroups = True
        bpy.context.scene.replacenameshapekeys = True
        bpy.context.scene.replacenamecurves = True
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_replacenamenone FILTER NONE
class BUTTON_OT_replacenamenone(bpy.types.Operator):
    '''Turn all types OFF'''
    bl_idname = "replacename.none"
    bl_label = "None"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.replacenameobjects = False
        bpy.context.scene.replacenamelights = False
        bpy.context.scene.replacenamecameras = False
        bpy.context.scene.replacenamecollections = False
        bpy.context.scene.replacenamebones = False
        bpy.context.scene.replacenameempty = False
        bpy.context.scene.replacenamelattice = False
        bpy.context.scene.replacenamematerials = False
        bpy.context.scene.replacenameuvs = False
        bpy.context.scene.replacenamevertexgroups = False
        bpy.context.scene.replacenameshapekeys = False
        bpy.context.scene.replacenamecurves = False
        return{'FINISHED'}

#   OPERATOR BUTTON_OT_replacenamelower LOWER CASE ALL
class BUTTON_OT_replacenamelower(bpy.types.Operator):
    '''make all names lower case only'''
    bl_idname = "replacename.lower"
    bl_label = "force lower case"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #   set testing object and collection arrays based on Only Selected user option
        if bpy.context.scene.replacenameselected:
            theobjs = bpy.context.selected_objects
            thecollections = []
            for thiscollection in bpy.data.collections:
                allin = 0
                for theobj in bpy.context.selected_objects:
                    if theobj.name in thiscollection.objects:
                        allin += 1
                if len(bpy.context.selected_objects) == allin:
                    thecollections.append(thiscollection)
        else:
            theobjs = bpy.context.scene.objects
            thecollections = bpy.data.collections
        
        #   collections
        if bpy.context.scene.replacenamecollections:
            for thecollection in thecollections:
                if not(thecollection.library):
                    thecollection.name = thecollection.name.lower()
        #   objects    
        for theobj in theobjs:
            if not(theobj.is_library_indirect):
                #   objects
                if ((theobj.type == "MESH") and bpy.context.scene.replacenameobjects):
                    theobj.name = theobj.name.lower()
                    if bpy.context.scene.replacenameobjdata:
                        theobj.data.name = theobj.data.name.lower()
                #   lights
                if (theobj.type == "LIGHT") and bpy.context.scene.replacenamelights:
                    theobj.name = theobj.name.lower()
                    if bpy.context.scene.replacenameobjdata:
                        theobj.data.name = theobj.data.name.lower()
                #   cameras
                if (theobj.type == "CAMERA") and bpy.context.scene.replacenamecameras:
                    theobj.name = theobj.name.lower()
                    if bpy.context.scene.replacenameobjdata:
                        theobj.data.name = theobj.data.name.lower()
                #   armatures
                if (theobj.type == "ARMATURE") and bpy.context.scene.replacenamebones:
                    theobj.name = theobj.name.lower()
                   #   bones within the armature   
                    if (len(theobj.data.bones) >= 1):
                        for thebone in theobj.data.bones:
                            thebone.name = thebone.name.lower()
                    if bpy.context.scene.replacenameobjdata:
                        theobj.data.name = theobj.data.name.lower()
                #   empties
                if(theobj.type == "EMPTY") and bpy.context.scene.replacenameempty:
                    theobj.name = theobj.name.lower()
                #   lattices
                if(theobj.type == "LATTICE") and bpy.context.scene.replacenamelattice:
                    theobj.name = theobj.name.lower()
                #   materials
                if (theobj.type != 'ARMATURE') and bpy.context.scene.replacenamematerials and (len(theobj.material_slots) >=1 ):
                    thesemats = theobj.material_slots
                    themats = []
                    for themat in thesemats:
                        themats.append(themat.material)
                    for thismat in themats:
                        #if (thismat) and (thismat.type != 'NoneType'):
                        if (thismat):
                            thismat.name = thismat.name.lower()
                #   uv maps
                if (theobj.type == 'MESH') and bpy.context.scene.replacenameuvs and (len(theobj.data.uv_layers) >= 1):
                    for thisuvs in theobj.data.uv_layers:
                        thisuvs.name = thisuvs.name.lower()
                #   vertex groups
                if (theobj.type == 'MESH') and bpy.context.scene.replacenamevertexgroups and (len(theobj.vertex_groups) >= 1):
                    for thisvertexgroups in theobj.vertex_groups:
                        thisvertexgroups.name = thisvertexgroups.name.lower()
                #   shape keys
                try:
                    if (theobj.type == 'MESH') and bpy.context.scene.replacenameshapekeys and (len(theobj.data.shape_keys.key_blocks) >= 1):
                        for thiskey in theobj.data.shape_keys.key_blocks:
                            thiskey.name = thiskey.name.lower()
                except:
                    print('failed shape keys')
                #   curves
                if(theobj.type == "CURVE") and bpy.context.scene.replacenamecurves:
                    theobj.name = theobj.name.lower()
                    if bpy.context.scene.replacenameobjdata:
                        theobj.data.name = theobj.data.name.lower()
        
        return{'FINISHED'}


#   PANEL VIEW3D_PT_replacenamereplacename
class VIEW3D_PT_replacenamereplacename(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ("Replace Names "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        split = layout.split(factor=0.5, align=True)
        col = split.column(align=True)
        col.prop(context.scene, "replacenameobjects")
        col.prop(context.scene, "replacenamelights")
        col.prop(context.scene, "replacenamecameras")
        col.prop(context.scene, "replacenamecollections")
        col.prop(context.scene, "replacenamebones")
        col.prop(context.scene, "replacenameempty")
        col.prop(context.scene, "replacenamelattice")
        col = split.column(align=True)
        col.prop(context.scene, "replacenamematerials")
        col.prop(context.scene, "replacenameuvs")
        col.prop(context.scene, "replacenamevertexgroups")
        col.prop(context.scene, "replacenameshapekeys")
        col.prop(context.scene, "replacenamecurves")
        split = layout.split(factor=0.5, align=True)
        col = split.column(align=True)
        col.operator("replacename.all", text=(BUTTON_OT_replacenameall.bl_label))
        col = split.column(align=True)
        col.operator("replacename.none", text=(BUTTON_OT_replacenamenone.bl_label))
        layout.separator()
        col = layout.column(align=True)
        col.prop(context.scene, "replacenameobjdata")
        col.prop(context.scene, "replacenameselected")
        layout.separator()
        split = layout.split(factor=0.5, align=True)
        col = split.column(align=True)
        col.prop(context.scene, "replacenamehead")
        col = split.column(align=True)
        col.prop(context.scene, "replacenametail")
        layout.operator("replacename.trim", text=(BUTTON_OT_replacenametrim.bl_label))
        
        layout.separator()
        split = layout.split(factor=0.35, align=True)
        col = split.column(align=True)
        col.label(text="Search for:")
        col.label(text="Replace with:")
        col = split.column(align=True)
        col.prop(context.scene, "replacenameold")
        col.prop(context.scene, "replacenamenew")
        layout.prop(context.scene, "replacenamecase")
        layout.operator("replacename.replace", text=(BUTTON_OT_replacenamereplace.bl_label))
        layout.operator("replacename.select", text=(BUTTON_OT_replacenameselect.bl_label))
        
        layout.separator()
        col = layout.column(align=True)
        split = col.split(align=True, factor=0.2)
        col = split.column()
        col.label(text="Prefix:")
        col.label(text="Suffix:")
        col = split.column(align=True)
        col.prop(context.scene, "replacenameprefix")
        col.prop(context.scene, "replacenamesuffix")
        
        layout.operator("replacename.presuf", text=(BUTTON_OT_replacenamepresuf.bl_label))
        layout.separator()
        layout.operator("replacename.reset", text=(BUTTON_OT_replacenamereset.bl_label))
        layout.separator()
        layout.operator("replacename.lower", text=(BUTTON_OT_replacenamelower.bl_label))

# PROPERTYGROUP ReplaceNameProperties
class ReplaceNameProperties(bpy.types.PropertyGroup):
    bpy.types.Scene.replacenameobjects = bpy.props.BoolProperty \
        (
          name = "Objects",
          description = "Search and Replace on Objects",
          default = True
        )
    bpy.types.Scene.replacenamelights = bpy.props.BoolProperty \
        (
          name = "Lights",
          description = "Search and Replace on Lights",
          default = True
        )
    bpy.types.Scene.replacenamecameras = bpy.props.BoolProperty \
        (
          name = "Cameras",
          description = "Search and Replace on Cameras",
          default = True
        )
    bpy.types.Scene.replacenamecollections = bpy.props.BoolProperty \
        (
          name = "Collections",
          description = "Search and Replace on collections",
          default = True
        )
    bpy.types.Scene.replacenamebones = bpy.props.BoolProperty \
        (
          name = "Bones",
          description = "Search and Replace on Armatures and Bones",
          default = True
        )
    bpy.types.Scene.replacenameempty = bpy.props.BoolProperty \
        (
          name = "Empty",
          description = "Search and Replace on Empty objects",
          default = True
        )
    bpy.types.Scene.replacenamelattice= bpy.props.BoolProperty \
        (
          name = "Lattices",
          description = "Search and Replace on Lattice objects",
          default = True
        )
    bpy.types.Scene.replacenamematerials = bpy.props.BoolProperty \
        (
          name = "Materials",
          description = "Search and Replace on Materials",
          default = True
        )
    bpy.types.Scene.replacenameuvs = bpy.props.BoolProperty \
        (
          name = "UV Maps",
          description = "Search and Replace on UV Maps",
          default = True
        )
    bpy.types.Scene.replacenamevertexgroups = bpy.props.BoolProperty \
        (
          name = "Vertex Groups",
          description = "Search and Replace on Vertex Groups",
          default = True
        )
    bpy.types.Scene.replacenameshapekeys = bpy.props.BoolProperty \
        (
          name = "Shape Keys",
          description = "Search and Replace on Shape Keys",
          default = True
        )
    bpy.types.Scene.replacenamecurves = bpy.props.BoolProperty \
        (
          name = "Curves",
          description = "Search and Replace on Curves",
          default = True
        )
    bpy.types.Scene.replacenameobjdata = bpy.props.BoolProperty \
        (
          name = "Include Object Data",
          description = "Include Object Data when replacing object names",
          default = True
        )
    bpy.types.Scene.replacenameselected = bpy.props.BoolProperty \
        (
          name = "Only Selected",
          description = "Only act on selected objects and/or their materials",
          default = False
        )
    bpy.types.Scene.replacenamehead = bpy.props.IntProperty \
        (
          name = "Head",
          description = "Trim from Head",
          default = 0,
          min = 0,
          max = 100000000,
          step = 1
        )
    bpy.types.Scene.replacenametail = bpy.props.IntProperty \
        (
          name = "Tail",
          description = "Trim from tail",
          default = 0,
          min = 0,
          max = 100000000,
          step = 1
        )
    bpy.types.Scene.replacenamecase = bpy.props.BoolProperty \
        (
          name = "Case Sensitive",
          description = "",
          default = False
        )
    bpy.types.Scene.replacenameold = bpy.props.StringProperty \
        (
          name = "",
          description = "Search string",
        )
    bpy.types.Scene.replacenamenew = bpy.props.StringProperty \
        (
          name = "",
          description = "New string",
        )
    bpy.types.Scene.replacenameprefix = bpy.props.StringProperty \
        (
          name = "",
          description = "Add Prefix"
        )
    bpy.types.Scene.replacenamesuffix = bpy.props.StringProperty \
        (
          name = "",
          description = "Add Suffix"
        )
    
    

####    REGISTRATION    ####

classes = [ ReplaceNameProperties, BUTTON_OT_replacenamereplace, 
            BUTTON_OT_replacenameselect, BUTTON_OT_replacenametrim, 
            BUTTON_OT_replacenamepresuf, BUTTON_OT_replacenamereset,
            BUTTON_OT_replacenameall, BUTTON_OT_replacenamenone,
            VIEW3D_PT_replacenamereplacename, BUTTON_OT_replacenamelower ]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        print(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    
if __name__ == "__main__":
    register()
