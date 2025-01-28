"""
setMaxBounces.py
v0.0.2
Copyright 2025 Launchpad. Conrad Dueck
CONFIDENTIAL AND PROPRIETARY
"""

# input variables
maxbounces = 16

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
    bpy.context.scene.cycles.transparent_max_bounces = maxbounces

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
