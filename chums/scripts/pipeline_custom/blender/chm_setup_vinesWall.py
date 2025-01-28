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


def setupVinesWall():
    src_nodegrp = "X:/projects/chums_season3/onsite/_prod/assets/helpers/setups/fx/204_03_080_vinesWall_vines_scatter.blend"
    src_vines = "X:/projects/chums_season3/onsite/_prod/assets/props/prp_vinesWall_01/30_texture/publish/blender/prp_vinesWall_01_v005.blend"
    tgt_vines = [o for o in bpy.data.objects if ('prp_vinesWall_01:vine') in o.name]
    # append vines collection if not preset
    if len(tgt_vines) < 1:
        the_asset_coll = "prp_vinesWall_01:asset_prod"
        with bpy.data.libraries.load(src_vines, link=False) as (data_src, data_dst):
            data_dst.collections = data_src.collections
        for coll in data_dst.collections:
            if (coll.name == the_asset_coll or coll.name == "asset_prod"):
            #if (coll == the_asset_coll or coll == "asset_prod"):
                coll.name = "prp_vinesWall_01:asset_prod_appended"
                #coll = "prp_vinesWall_01:asset_prod_appended"
                bpy.context.scene.collection.children.link(coll)
    # position vines wall assuming it's landing in default lakeRockyShore env asset in Blender
    if 'prp_vinesWall_01:vine1' in bpy.data.objects:
        topnode = bpy.data.objects['prp_vinesWall_01:vine1'].parent.parent
        topnode.location = (-7.26,0.3,-0.09)
        topnode.rotation_euler.z = -4.5814125
    tgt_vines = [o for o in bpy.data.objects if ('prp_vinesWall_01:vine') in o.name]
    # import scatter system if needed
    if not('vines_scatter' in bpy.data.node_groups):
        with bpy.data.libraries.load(src_nodegrp, link=False) as (data_from, data_to):
                    data_to.node_groups = [
                        name for name in data_from.node_groups if name == ("vines_scatter")]
    # add modifiers as needed
    for o in tgt_vines:
        if len(o.modifiers) == 0 or not(o.modifiers[-1].type == 'NODES'):
            o.modifiers.new('GeometryNodes', 'NODES')
    # add scatter system to mod and update settings
        o.modifiers[-1].node_group = bpy.data.node_groups['vines_scatter']
        my_number = int(o.name.split('1:vine')[-1])
        o.modifiers[-1]["Socket_2"] = my_number


def saveBlendFile():
    basePath, blendName = os.path.split(bpy.data.filepath)
    fileName = f'{entity}_{lang}.blend'
    versionUpBlendFile(basePath, fileName, dryRun=False)

if __name__ == "__main__":

    try:
        setupVinesWall()
        saveBlendFile()
        publishEntity(comment="Published From a Custom Script!")

    except Exception as e:
        log.error(e)