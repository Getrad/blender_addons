"""
update_holerim_cutters.py
v0.0.2
Copyright 2025 Conrad Dueck, Darren Place
CONFIDENTIAL AND PROPRIETARY
"""

# input variables
#groundList = ["env_chumsClearing_01_fallwet:gp_main",]
groundList = ["gp_main","mud_base_001","mud_base_002"]
solverType = 'EXACT'
col_name = "env"

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
    for o in objs:
        if o.parent is not None:
            print("Clearing parent ", o.parent.name, " on: ", o.name)
            if o.name in bpy.context.view_layer.objects:
                try:
                    wld = o.matrix_world
                    bpy.context.view_layer.objects.active = o
                    bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
                    o.parent = None
                    o.matrix_world = wld
                    bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
                    print(o.name, " unparented to: ", str(o.matrix_world))
                except:
                    print("Error about object not in view layer on: ", o.name)

def collectFamTree(ob,famTree):
    while ob.parent is not None:
        if not(ob.parent in famTree):
            famTree.insert(0, ob.parent)
        ob = ob.parent
        collectFamTree(ob,famTree)
    return famTree

def localize_parent(ob):
    pobj = ob.parent
    pobj.make_local()
    if pobj.parent is not None:
        localize_parent(pobj)     

def localize_object(objs):
    for ob in objs:
        if ob.name in bpy.context.view_layer.objects:
            print("Localizing: ", ob.name)
            ob.make_local()
            if ob.data:
                ob.data.make_local()

def localizeGPs(objects_localize):
    for obj_name in objects_localize:
        myFamTree = []
        groundmatched = [o for o in bpy.data.objects if o.name.endswith(obj_name)]
        for obj in groundmatched:
            for col in bpy.data.collections:
                if obj.name in col.all_objects:
                    print('   Localizing Collection: ', col.name)
                    col.make_local()
            myFamTree = collectFamTree(obj,[])
            myFamTree.append(obj)
            localize_object(myFamTree)
            clear_parent(myFamTree)

def libOR(objects_localize):
    for obj_name in objects_localize:
        groundmatched = [o for o in bpy.data.objects if o.name.endswith(obj_name)]
        for obj in groundmatched:
            bpy.context.view_layer.objects.active = obj
            #obj.override_hierarchy_create(bpy.context.scene, bpy.context.view_layer, do_fully_editable = True)
            for o in bpy.data.objects:
                if o == obj:
                    o.select_set(True)
                else:
                    o.select_set(False)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.make_override_library()
            obj.data.update()
            print(obj.name)

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
                if 'Processong' in obj.modifiers:
                    modifierPos = (obj.modifiers.find('Processing') + 1)
                boolmod.solver = solverType
                boolmod.operation = 'DIFFERENCE'
                boolmod.operand_type = 'OBJECT'
                boolmod.object = bpy.data.objects[cutName]
                bpy.context.view_layer.objects.active = obj
                obj.modifiers.move(obj.modifiers.find(modName), modifierPos)
                #bpy.ops.object.modifier_move_to_index(modifier=(boolmod.name), index=1)
                #print(obj.modifiers[modName].name, obj.modifiers.find(modName))

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
        saveBlendFile()
        publishEntity(comment="Published From a Custom Script")
    except Exception as e:
        log.error(e)
