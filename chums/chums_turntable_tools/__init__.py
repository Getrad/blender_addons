from importlib import reload
import bpy


bl_info = {
    "name": "TurnTable Tools",
    "author": "Conrad Dueck, Darren Place",
    "version": (0, 2, 1),
    "blender": (3, 3, 1),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Turntable Convenience Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

def register():
    from chums_turntable_tools import chums_turntable_tools
    reload(chums_turntable_tools)
    return chums_turntable_tools.register()


def unregister():
    from chums_turntable_tools import chums_turntable_tools
    return chums_turntable_tools.unregister()


if __name__ == "__main__":
    register()
    
