"""
force_texture_limit.py
v0.0.2
Copyright 2025 Launchpad. Conrad Dueck
CONFIDENTIAL AND PROPRIETARY
"""

# input variables
TEXTURE_SIZE_LIMIT_PX = 2048

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
    bpy.context.scene.render.use_simplify = True
    bpy.context.scene.cycles.texture_limit_render = str(TEXTURE_SIZE_LIMIT_PX)
    print(f"Forced texture size limit to {TEXTURE_SIZE_LIMIT_PX}px on {entity}")

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
