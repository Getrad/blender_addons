"""
update_holerim_cutters.py
v0.0.1
Copyright 2023 Conrad Dueck
CONFIDENTIAL AND PROPRIETARY
"""

# import launchpad utils
import imp
lp = imp.load_source(
    'lpUtils', r'Y:\projects\CHUMS_Onsite\pipeline\repos\launchpadRepository\api\launchpadUtils.py')

import sys
import os
import bpy

argv = sys.argv                     # recieve args from launchpad
argv = argv[argv.index("--") + 1:]  # get all args after "--"
args = lp.convertArgsToDict(argv)   # convert argv to python dictionary
#entity = args["entity"]
#lang = lp.getLangShorthand(args["lang"])
#shotBaseDir, shotName = lp.getLatestShotConform(entity)
#shotLightingDir, shotLightName = lp.getLatestShotLighting(entity, lang)
#eObj = lp.breakdownEntityName(f'{shotName[:-5]}_{lang}_{shotName[-4:]}')

def localize_parent(ob):
    pobj = ob.parent
    pobj.make_local()
    if pobj.parent is not None:
        localize_parent(pobj)


def doAction():
    #objects_localize = ["ground.master","gp_main",]    ###retains original naming
    objects_localize = ["gp_main","env.loonbeach:ground"]
    cutter_names = [ob.name for ob in bpy.data.objects if "prx_holeRim_01:bool_cutter_" in ob.name]

    for obj_name in objects_localize:
        if obj_name in bpy.data.objects:
            obj = bpy.data.objects[obj_name]
            for col in bpy.data.collections:
                if obj_name in col.all_objects:
                    if col.library is not None:
                        col.make_local()
            if obj.parent is not None and obj.parent.library is not None:
                localize_parent(obj)
            obj.make_local()
            
            for cutname in cutter_names:
                if bpy.data.objects[cutname]:
                    boolmod = obj.modifiers.new("Boolean", 'BOOLEAN')
                    boolmod.solver = 'EXACT'
                    boolmod.operation = 'DIFFERENCE'
                    boolmod.operand_type = 'OBJECT'
                    boolmod.object = bpy.data.objects[cutname]

def saveLightingBlendFileAs():
    filename = f'{eObj["projName"]}_{eObj["epNo"]}_{eObj["seqNo"]}_{eObj["shotNo"]}_{eObj["lang"]}_{eObj["vNo"]}.blend'
    savePath = os.path.join(shotLightingDir, filename)
    vNo = int(eObj["vNo"][1:])
    while os.path.exists(savePath) or not savePath.endswith('.blend'):
        vNo += 1
        filename = f'{eObj["projName"]}_{eObj["epNo"]}_{eObj["seqNo"]}_{eObj["shotNo"]}_{eObj["lang"]}_v{"{:03d}".format(vNo)}.blend'
        savePath = os.path.join(shotLightingDir, filename)
    thisOutputPath = ''
    renderBaseDir, outputName = lp.setLightingOutput(entity, eObj["lang"])
    thisOutputPath = os.path.join(renderBaseDir, f'{outputName}_####.png')
    bpy.context.scene.render.filepath = thisOutputPath
    bpy.ops.wm.save_as_mainfile(filepath=savePath)
    return None

def main():
    doAction()
    #saveLightingBlendFileAs() # comment out when prototyping


main()