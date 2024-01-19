"""
update_rockSitting_naterial.py
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
entity = args["entity"]
lang = lp.getLangShorthand(args["lang"])
shotBaseDir, shotName = lp.getLatestShotConform(entity)
shotLightingDir, shotLightName = lp.getLatestShotLighting(entity, lang)
eObj = lp.breakdownEntityName(f'{shotName[:-5]}_{lang}_{shotName[-4:]}')

def doAction():
    mtl = bpy.data.materials["prx_rockSitting_01:rock"]
    ramp_node = mtl.node_tree.nodes["ColorRamp.001"].color_ramp
    ramp_node.elements[0].color = (0,0,0,1)
    ramp_node.elements[0].position = 0.0375
    ramp_node.elements[1].color = (0.95,0.95,0.95,1)
    range_node = mtl.node_tree.nodes["Map Range.001"]
    range_node.inputs[4].default_value = 0.25
    print("Updated Material: ", mtl.name)
    return 0

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
    saveLightingBlendFileAs() # comment out when prototyping


main()