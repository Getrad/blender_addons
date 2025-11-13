import bpy
import os


# USER OPTIONS
## res 1 = hires /0 = lores
## frm 1 = full frame range / 0 = first middle last
## render priority = integer between 0 and 100
usropt = [1,1,50]



# VARAIBLES
scn = bpy.context.scene
lyr = scn.view_layers[0]
rndr = scn.render
cyc = scn.cycles
flam = scn.flamenco_job_settings

# FORMAT
rndr.image_settings.file_format = 'OPEN_EXR_MULTILAYER'

# OVERRIDES
rndr.use_compositing = True
rndr.use_stamp_note = True
if usropt[0] == 1:
    lyr.samples = 0
    rndr.stamp_note_text = "1024 Samples"
    scn.flamenco_job_name = (os.path.basename(bpy.data.filepath).split(".")[0]+"_1024rays")
else:
    lyr.samples = 16
    rndr.stamp_note_text = "16 Samples"
    scn.flamenco_job_name = (os.path.basename(bpy.data.filepath).split(".")[0]+"_16rays")
if usropt[1] == 1:
    flam.autoeval_frames = True
    scn.flamenco_job_name += "_FFR"
else:
    flam.autoeval_frames = False
    flam.frames = (""+str(scn.frame_start)+","+(str((scn.frame_start+int((scn.frame_end-scn.frame_start)/2))))+","+str(scn.frame_end)+"")
    scn.flamenco_job_name += "_FML"
scn.flamenco_job_priority = usropt[2]

# cycles settings
cyc.samples = 1024

# layers
lyr.use_pass_ambient_occlusion = False
lyr.use_pass_combined = True
lyr.use_pass_cryptomatte_accurate = False
lyr.use_pass_cryptomatte_asset = False
lyr.use_pass_cryptomatte_material = True
lyr.use_pass_cryptomatte_object = False
lyr.pass_cryptomatte_depth = 3
lyr.use_pass_diffuse_color = True
lyr.use_pass_diffuse_direct = True
lyr.use_pass_diffuse_indirect = True
lyr.use_pass_emit = False
lyr.use_pass_environment = True
lyr.use_pass_glossy_color = True
lyr.use_pass_glossy_direct = True
lyr.use_pass_glossy_indirect = True
lyr.use_pass_grease_pencil = False
lyr.use_pass_material_index = False
lyr.use_pass_mist = True
lyr.use_pass_normal = True
lyr.use_pass_object_index = False
lyr.use_pass_position = True
lyr.use_pass_shadow = True
lyr.use_pass_subsurface_color = True
lyr.use_pass_subsurface_direct = True
lyr.use_pass_subsurface_indirect = True
lyr.use_pass_transmission_color = True
lyr.use_pass_transmission_direct = True
lyr.use_pass_transmission_indirect = True
lyr.use_pass_uv = True
lyr.use_pass_vector = True
lyr.use_pass_z = True
