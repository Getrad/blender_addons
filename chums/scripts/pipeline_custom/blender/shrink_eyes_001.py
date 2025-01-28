"""
shrink_eyes_001.py
v0.0.2
Copyright 2025 Conrad Dueck, Darren Place
CONFIDENTIAL AND PROPRIETARY
"""

# input variables
ob_list = ['chr_flieswitheagles_scene_ma:eye_R',
           'chr_flieswitheagles_scene_ma:eye_L',]
displace_stength = -0.065
displace_midlevel = 0.0

# import
import os
import sys
import bpy

from launchpad.dcc.blender.publishing import publishEntity
from launchpad.dcc.blender.saving import versionUpBlendFile
from launchpad.helpers import log
from launchpad.helpers.action import getActionParameters
from launchpad.helpers.entity import getLangShorthand

action = getActionParameters(sys.argv)
entity = action["entity"]
lang = getLangShorthand(action["lang"])

def doAction():
    for ob in bpy.data.objects:
        if ob.name in ob_list:
            bpy.context.view_layer.objects.active = ob
            if "Displace" in ob.modifiers:
                dispmod = ob.modifiers['Displace']
            else:
                dispmod = ob.modifiers.new(name="Displace", type="DISPLACE")
            bpy.ops.object.modifier_move_to_index(modifier="Displace", index=1)
            dispmod.strength = displace_stength
            dispmod.mid_level = displace_midlevel
    return 0

def saveBlendFile():
    basePath, blendName = os.path.split(bpy.data.filepath)
    fileName = f'{entity}_{lang}.blend'
    versionUpBlendFile(basePath, fileName, dryRun=False)
    
    return None

if __name__ == "__main__":
    try:
        doAction()
        saveBlendFile()
        publishEntity(comment="Published From a Custom Script")
    except Exception as e:
        log.error(e)
        