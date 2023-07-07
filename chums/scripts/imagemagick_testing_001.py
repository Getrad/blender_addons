import bpy
import subprocess
from pathlib import Path
#imagick = Path("C:/temp/ImageMagick-7.1.1-Q16-HDRI\magick/.exe")
imagick = Path("C:/Program Files/ImageMagick-7.1.1-Q16-HDRI\magick.exe")

def convert_to_exr(image):
    import os
    img_path = image.filepath
    img_name = os.path.basename(img_path)
    img_dir = os.path.dirname(img_path)
    tgt_path = (img_path[:-4] + "GOING2" + ".exr")
    img_cmd = (str(imagick) + " \"" + img_path + "\" -compress zip -depth 16 \"" + tgt_path + "\"")
    print(img_cmd)
    running = subprocess.Popen(img_cmd)
    running.wait()
    print(running.returncode)
    return img_cmd

convert_to_exr(bpy.data.images[0])

