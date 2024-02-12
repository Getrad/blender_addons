import bpy
from pathlib import Path
import os
import time
import shutil
import datetime

now = datetime.datetime.now()
theDate = (str(now.year)+'-'+str(now.month).zfill(2)+'-'+str(now.day).zfill(2))
theTime = (str(now.hour).zfill(2)+'-'+str(now.minute).zfill(2)+'-'+str(now.second).zfill(2))

# get username and blender version to build path to startup file
uname = os.getlogin()
bl_version = (str(bpy.app.version[0]) + "." + str(bpy.app.version[1]))
cur_string = ('C:/Users/' + uname + '/AppData/Roaming/Blender Foundation/Blender/' + str (bl_version) + '/config/startup.blend')

# back up current startup file
bak_filename = (theDate + '_' + theTime + '_startup')
bak_string = cur_string.replace("startup",bak_filename)

# new path
bak_path = Path(bak_string)
cur_path = Path(cur_string)
new_path = shutil.copy(cur_path,bak_path)

# overewrite startup file
bpy.ops.wm.save_homefile()