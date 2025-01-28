"""
disable_canopy_foliage_in_vp.py
v0.0.2
Copyright 2025 Conrad Dueck, Darren Place
CONFIDENTIAL AND PROPRIETARY
"""

# input variables

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

def localize_parent(ob):
    pobj = ob.parent
    pobj.make_local()
    if pobj.parent is not None:
        localize_parent(pobj)

def doAction():
    for o in bpy.data.objects:
        if ":chums_tree_foliage_" in o.name:
            if "GeoNodes - Foliage Leafer" in o.modifiers:
                o.modifiers["GeoNodes - Foliage Leafer"].show_viewport = False
        
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
