"""
add subdiv mod to objects by found name pattern
v0.0.2
Copyright 2025 Conrad Dueck, Darren Place
CONFIDENTIAL AND PROPRIETARY
"""

# input variables
string_patterns = ["Rim_01:dirt_"]
input_add = 1
input_override = 1
input_disableRender = False

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

def doAction(pattern,level_add,level_override):
    for ob in [o for o in bpy.data.objects if pattern in o.name]:
        if not("Subdivision" in ob.modifiers):
            subdivMod = ob.modifiers.new("Subdivision", 'SUBSURF')
        else:
            subdivMod = ob.modifiers["Subdivision"]
        print('found:', ob.name, subdivMod.name)
        print(level_override)
        if subdivMod:
            if level_add > 0:
                subdivMod.levels += level_add
                subdivMod.render_levels += level_add
            if level_override > 0:
                subdivMod.levels = level_override
                subdivMod.render_levels = level_override
            subdivMod.show_viewport = False
            if input_disableRender == True:
                subdivMod.show_render = False
            else:
                subdivMod.show_render = True
        
def saveBlendFile():
    basePath, blendName = os.path.split(bpy.data.filepath)
    fileName = f'{entity}_{lang}.blend'
    versionUpBlendFile(basePath, fileName, dryRun=False)
    
    return None

if __name__ == "__main__":
    try:
        for string_pattern in string_patterns:
            if len(string_pattern) > 0:
                doAction(string_pattern,input_add,input_override)
            saveBlendFile()
            publishEntity(comment="Published From a Custom Script")
    except Exception as e:
        log.error(e)
