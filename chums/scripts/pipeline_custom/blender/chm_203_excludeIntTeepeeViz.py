"""
chm_203_disableIntTeepeeViz.py
v1.0.0
Copyright 2024 Darren Place
CONFIDENTIAL AND PROPRIETARY
"""

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

HARDCODE_COL_NAME = "env_int_kohkumTeepee_01:asset_prod"

def hideCollectionInViewLayer(layerCollection, colName):
    if layerCollection.collection.name == colName:
        layerCollection.exclude = True
        log.info(f"{colName} is now excluded from the view layer")
        return True
    
    for child in layerCollection.children:
        if hideCollectionInViewLayer(child, colName):
            return True
    
    return False

def saveBlendFile():
    basePath, blendName = os.path.split(bpy.data.filepath)
    fileName = f'{entity}_{lang}.blend'
    versionUpBlendFile(basePath, fileName, dryRun=False)

if __name__ == "__main__":

    try:
        found = hideCollectionInViewLayer(bpy.context.view_layer.layer_collection, HARDCODE_COL_NAME)
        if found:
            saveBlendFile()
            publishEntity(comment="Published From a Custom Script!")
        else:
            log.warn(f"No collection {HARDCODE_COL_NAME} was found. The shot will not be versioned up.")

    except Exception as e:
        log.error(e)