"""
update_holerim_cutters.py
v0.0.2
Copyright 2025 Conrad Dueck, Darren Place
CONFIDENTIAL AND PROPRIETARY
"""

# input variables
groundList = ["gp_main","mud_base_001","mud_base_002", "BeaverDamSnowLayer"]
solverType = 'EXACT'
col_name = "env"
stackBaseMod = 'Processing'
stackTop = False

# import
import os
import sys
import bpy
from mathutils import *

from launchpad.dcc.blender.publishing import publishEntity
from launchpad.dcc.blender.saving import versionUpBlendFile
from launchpad.helpers import log
from launchpad.helpers.action import getActionParameters
from launchpad.helpers.entity import getLangShorthand

action = getActionParameters(sys.argv)
entity = action["entity"]
lang = getLangShorthand(action["lang"])

def clear_parent(objs):
    #print("Executing clear_parent function")
    for o in objs:
        if o.parent is not None:
            #print("Executing clear_parent function on ", o.name)
            #print("Fighting with View Layer ", bpy.context.view_layer.name)
            #print("Clearing parent ", o.parent.name, " on: ", o.name)
            if o.name in bpy.context.view_layer.objects:
                #print("Found ", o.name, " in view layer ", bpy.context.view_layer.name)
                wld = o.matrix_world
                #print("set wld")
                bpy.context.view_layer.objects.active = bpy.data.objects.get(o.name) # re-reference the object to handle a potential race condition
                o = bpy.context.view_layer.objects.active
                #print("set acive object")
                o.select_set(True)
                #print("select object")
                bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
                #print("transform applied")
                o.parent = None
                #print("set parent to None")
                o.matrix_world = wld
                #print("set offset matrix_world to wld")
                bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
                #print(o.name, " unparented to: ", str(o.matrix_world))
            else:
                print("Skipping clear_parent function for ", o.name, " parent ", o.parent.name)
    #print("Completed run of clear_parent function")

def collectFamTree(ob,famTree):
    while ob.parent is not None:
        if not(ob.parent in famTree):
            famTree.insert(0, ob.parent)
        ob = ob.parent
        collectFamTree(ob,famTree)
    return famTree

def localize_parent(ob):
    pobj = ob.parent
    if not(pobj.name in bpy.context.view_layer.objects):
        bpy.context.view_layer.active_layer_collection.collection.objects.link(pobj)
        if pobj.name in bpy.context.view_layer.objects:
            print("Added ", ob.name, " PARENT ", pobj.name, " to view layer ", bpy.context.view_layer.name)
    if pobj.library is not None:
        #print("    Localizing PARENT: ", pobj.name)
        pobj.make_local()
    if pobj.parent is not None:
        localize_parent(pobj)
    #print("Completed run of localize_parent function")

def localize_object(objs):
    #print("Executing localize_object function")
    for ob in objs:
        if ob.name in bpy.context.view_layer.objects:
            if ob.library is not None:
                #print("    Localizing OBJECT: ", ob.name)
                ob.make_local()
            if ob.data:
                ob.data.make_local()
    #print("Completed run of localize_object function")

def add_to_view_layer(objects_list):
    #print("Executing add_to_view_layer to localize objects from myFamTree collected hierarchical list")
    for ob in objects_list:
        if not(ob.name in bpy.context.view_layer.objects):
            #print("    ", ob.name, " NOT found in view layer")
            bpy.context.view_layer.active_layer_collection.collection.objects.link(ob)
            if ob.name in bpy.context.view_layer.objects:
                print("Added ", ob.name, " to view layer ", bpy.context.view_layer.name)
    bpy.context.view_layer.update()
    #print("Completed run of add_to_view_layer function")

def localize_collections(ob):
    #print("Executing localize_collections function for object ", ob.name)
    for col in bpy.data.collections:
        if ob.name in col.all_objects:
            if col.library is not None:
                #print('   Localizing COLLECTION: ', col.name)
                col.make_local()
    #print("Completed run of localize_collections function")

def localizeGPs(objects_localize):
    #print("Executing localizeGPs")
    for obj_name in objects_localize:
        myFamTree = []
        groundmatched = [o for o in bpy.data.objects if o.name.endswith(obj_name)]
        for obj in groundmatched:
            localize_collections(obj)
            myFamTree = collectFamTree(obj,[])
            myFamTree.append(obj)
            add_to_view_layer(myFamTree)
            localize_object(myFamTree)
            clear_parent(myFamTree)

def libOR(objects_localize):
    for obj_name in objects_localize:
        groundmatched = [o for o in bpy.data.objects if o.name.endswith(obj_name)]
        for obj in groundmatched:
            bpy.context.view_layer.objects.active = bpy.data.objects.get(obj.name) # re-reference the object to handle a potential race condition
            obj = bpy.context.view_layer.objects.active
            for o in bpy.data.objects:
                if o == obj:
                    o.select_set(True)
                else:
                    o.select_set(False)
            bpy.context.view_layer.objects.active = bpy.data.objects.get(obj.name) # re-reference the object to handle a potential race condition
            obj = bpy.context.view_layer.objects.active
            bpy.ops.object.make_override_library()
            obj.data.update()
            #print(obj.name)

def libORcol(colName):
    col = bpy.data.collections[colName].children[0]
    col.override_hierarchy_create(bpy.context.scene, bpy.context.view_layer, do_fully_editable = True)
    print(col.name)

def updateBooleans(objects_apply):
    cutNames = [ob.name for ob in bpy.data.objects if "prx_holerim_01:bool_cutter_" in ob.name]
    for obj_name in objects_apply:
        groundmatched = [o for o in bpy.data.objects if o.name.endswith(obj_name)]
        for obj in groundmatched:
            stackBaseMod = 'Processing'
            modifierPos = 1
            for cutName in cutNames:
                modName = (cutName.split(":")[-1])
                if modName in obj.modifiers:
                    boolmod = obj.modifiers[modName]
                else:
                    boolmod = obj.modifiers.new(modName, 'BOOLEAN')
                boolmod.solver = solverType
                boolmod.operation = 'DIFFERENCE'
                boolmod.operand_type = 'OBJECT'
                boolmod.object = bpy.data.objects[cutName]
                bpy.context.view_layer.objects.active = bpy.data.objects.get(obj.name) # re-reference the object to handle a potential race condition
                obj = bpy.context.view_layer.objects.active
                if ((stackBaseMod in obj.modifiers) and (stackTop == False)):
                    modifierPos = (obj.modifiers.find(stackBaseMod) + 1)
                    obj.modifiers.move(obj.modifiers.find(modName), modifierPos)

def winterize(objects_apply):
    if "prx_holerim_01:asset_prod" in bpy.data.collections:
        holerimCol = bpy.data.collections["prx_holerim_01:asset_prod"]
        for obj_name in objects_apply:
            groundmatched = [o for o in bpy.data.objects if o.name.endswith(obj_name)]
            for obj in groundmatched:
                if "Winterizer" in obj.modifiers:
                    obj.modifiers["Winterizer"]["Socket_2"] = holerimCol
                    print("assigned holerim collection to heatmap slot on Winterizer for: ", obj.name)

def saveBlendFile():
    basePath, blendName = os.path.split(bpy.data.filepath)
    fileName = f'{entity}_{lang}.blend'
    versionUpBlendFile(basePath, fileName, dryRun=False)
    
    return None

if __name__ == "__main__":
    try:
        localizeGPs(groundList)     # localize all the ground plane objects found in groundList
        #libOR(groundList)          # testing library override OBJECT approach that appears to work IN UI - but sadly doesn't seem to work from API
        #libORcol(col_name)         # testing library override COLLECTION approach that appears to work IN UI - but sadly doesn't seem to work from API
        updateBooleans(groundList)
        winterize(groundList)
        saveBlendFile()
        publishEntity(comment="Published From a Custom Script")
    except Exception as e:
        log.error(e)
        log.traceback()
