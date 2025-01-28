"""
chm_example_publishShot.py
v1.0.0
Copyright 2024 Launchpad, FRANK Labs
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
        saveBlendFile()
        publishEntity(comment="Published From a Custom Script!")

    except Exception as e:
        log.error(e)