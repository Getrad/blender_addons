"""
chm_disableLightTree.py
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


def saveBlendFile():
    basePath, blendName = os.path.split(bpy.data.filepath)
    fileName = f'{entity}_{lang}.blend'
    versionUpBlendFile(basePath, fileName, dryRun=False)

if __name__ == "__main__":

    try:
        if bpy.context.scene.cycles.use_light_tree:
            log.warn("Light Tree is enabled! Disabling / re-publishing shot...")
            bpy.context.scene.cycles.use_light_tree = False
            saveBlendFile()
            publishEntity(comment="Automated Disable Light Tree (Custom Script).")
        else:
            log.info("Light Tree was not enabled. The shot will not be re-published.")


    except Exception as e:
        log.error(e)