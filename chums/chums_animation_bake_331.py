# update to 3.3.1

bl_info = {
    "name": "Animation Bake",
    "author": "conrad dueck",
    "version": (0,2,3),
    "blender": (3, 30, 1),
    "location": "View3D > Tool Shelf > Chums",
    "description": "Bake multiple objects at once.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Chums"}

import bpy, mathutils, random, math
from mathutils import Matrix


####    GLOBAL VARIABLES    ####
vsn='2.3'


####    FUNCTIONS    ####
def update_particles_ui(self, context):
    if self.animbake_particles:
        bpy.context.scene.animbake_objects = True

def update_particle_mesh_ui(self, context):
    if self.animbake_particles_mesh:
        if not(bpy.context.scene.animbake_particles):
            bpy.context.scene.animbake_particles = True
            
def update_topath_ui(self, context):
    if self.animbake_topath:
        bpy.context.scene.animbake_toempty = True
    else:
        bpy.context.scene.animbake_follow = False

def update_follow_ui(self, context):
    if self.animbake_follow:
        bpy.context.scene.animbake_toempty = True
        bpy.context.scene.animbake_topath = True
        
def update_objempty_ui(self, context):
    if not(self.animbake_toempty):
        bpy.context.scene.animbake_topath = False
        bpy.context.scene.animbake_follow = False
    else:
        bpy.context.scene.animbake_xforms = True

def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step

def float_to_int_decimal(_float):
    i = 0
    fl = 0.0
    i = int(math.floor(_float))
    fl = _float - i
    return [i, fl]

def bake_object_to_empty(ob, frmlist, tgtrot):
    scene = bpy.context.scene
    newname = ('nul.'+ob.name+'.BAKED.000')
    newempty = bpy.data.objects.new(newname, None)
    scene.collection.objects.link(newempty)
    bpy.context.view_layer.objects.active = newempty
    for theframe in frmlist:
        frm = float_to_int_decimal(theframe)[0]
        sub = float_to_int_decimal(theframe)[1]
        scene.frame_set(frm, subframe=sub)
        newempty.location = (ob.matrix_world.to_translation())
        newempty.keyframe_insert('location', frame=(frm+sub))
        newempty.rotation_mode = tgtrot
        if "Y" in tgtrot:
            newempty.rotation_euler = (ob.matrix_world.to_euler())
            newempty.keyframe_insert('rotation_euler', frame=(frm+sub))
        else:
            newempty.rotation_quaternion = ob.matrix_world.to_quaternion()
            newempty.keyframe_insert('rotation_quaternion', frame=(frm+sub))
        newempty.scale = (ob.matrix_world.to_scale())
        newempty.keyframe_insert('scale', frame=(frm+sub))
        bpy.ops.wm.redraw_timer(type='ANIM_STEP', iterations=1)
    return newempty

def has_keyframe(ob, attr):
    anim = ob.animation_data
    if anim is not None and anim.action is not None:
        for fcu in anim.action.fcurves:
            if fcu.data_path == attr:
                return len(fcu.keyframe_points) > 0
    return False

def transfer_trs_curves(obsrc, obtgt):
    tanim = obtgt.animation_data
    frm = bpy.context.scene.frame_current
    for chan in ['location','rotation_euler','scale']:
        if not(has_keyframe(obtgt, chan)) and (has_keyframe(obsrc, chan)):
            obtgt.keyframe_insert(chan, frame=frm)
            print('HAD TO SET KEYS ON ', obtgt.name, chan)
    for tfc in obtgt.animation_data.action.fcurves:
        if tfc.data_path in ['location','rotation_euler','scale']:
            dindex = tfc.array_index
            for sfc in obsrc.animation_data.action.fcurves:
                if (tfc.data_path == sfc.data_path) and (sfc.array_index == dindex):
                    print(obsrc.name, sfc.data_path, obtgt.name, tfc.data_path)
                    for point in sfc.keyframe_points:
                        tfc.keyframe_points.insert(frame=point.co.x, value=point.co.y)

def getedgelengths(obj):
    edge_lengths = [0.0]
    bpy.ops.object.select_all(action='DESELECT')
    depsgraph_01 = bpy.context.evaluated_depsgraph_get()
    tempmesh = obj.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph_01).copy()
    tempob = bpy.data.objects.new('tempob', tempmesh)
    bpy.context.scene.collection.objects.link(tempob)
    bpy.context.view_layer.objects.active = tempob
    tempob.select_set(True)
    if bpy.ops.object.convert.poll():
        bpy.ops.object.convert(target='MESH')
        for edge in tempob.data.edges:
            vert0 = tempob.data.vertices[edge.vertices[0]].co
            vert1 = tempob.data.vertices[edge.vertices[1]].co
            edge_lengths.append(edge_lengths[len(edge_lengths)-1] + ((vert0-vert1).length))
        bpy.ops.object.delete()
    else:
        print('POLLING OF CONVERT FUNCTION FAILED')
    #    return a list of all the edge lengths, compounded so the last one is the total length
    return edge_lengths

def createmotioncurve(animob,frmlist):
    scene = bpy.context.scene
    cname = ('crv.'+animob.name+'.000')
    thecount = len(frmlist)
    trucount = 0
    thetime = frmlist
    llist = []
    rlist = []
    slist = []
    #    create curve data
    ccurve = bpy.data.curves.new(cname, type='CURVE')
    ccurve.dimensions = '3D'
    curveob = bpy.data.objects.new(cname, ccurve)
    scene.collection.objects.link(curveob)
    #    create spline in curve
    pline = ccurve.splines.new('POLY')
    pline.points.add(thecount-1)
    #    loop thru frames, add points, position them to match ob location
    subcount = 0
    for theframe in frmlist:
        frm = float_to_int_decimal(theframe)[0]
        sub = float_to_int_decimal(theframe)[1]
        scene.frame_set(frm, subframe=sub)
        thisloc = animob.matrix_world.to_translation()
        llist.append(thisloc)
        rlist.append(animob.matrix_world.to_euler())
        slist.append(animob.matrix_world.to_scale())
        #pline.points[frm].co = (thisloc.x, thisloc.y, thisloc.z, 1)
        pline.points[subcount].co = (thisloc.x, thisloc.y, thisloc.z, 1)
        subcount += 1
    return (curveob,llist,rlist,slist,thecount)

def copymods(srcobj, tgtobj):
    for smod in srcobj.modifiers:
        tmod = tgtobj.modifiers.get(smod.name, None)
        if not tmod:
            tmod = tgtobj.modifiers.new(smod.name, smod.type)
        properties = [prop.identifier for prop in smod.bl_rna.properties if not prop.is_readonly]
        for prop in properties:
            setattr(tmod, prop, getattr(smod, prop))


####    CLASSES    ####
#   OPERATOR animbakebake INTO THE OVEN
class BUTTON_OT_animbakebake(bpy.types.Operator):
    '''Bake'''
    bl_idname = "animbake.bake"
    bl_label = "Into the Oven"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('\n\nSTART BAKE************************************************************************')
        scene = bpy.context.scene
        bakelist = []
        fulllist = []
        
        startframe = scene.frame_current
        tstart = scene.animbake_start
        tend = scene.animbake_end
        tstep = float_to_int_decimal(scene.animbake_step)[0]
        tsubstep = float_to_int_decimal(scene.animbake_step)[1]
        vkey = scene.animbake_vkey
        ccontraint = scene.animbake_clearconstraints
        cparent = scene.animbake_clearparents
        tgtrotation = scene.animbake_tgtrotation
        
        #    build the bakelist based on user set 'selected' toggle
        if scene.animbake_objects:
            for ob in bpy.context.selected_objects:
                bakelist.append(ob)
        else:
            for ob in bpy.data.objects:
                bakelist.append(ob)
        
        #    build the list of frames as floats to bake
        timerange = list(frange(tstart, (tend+2), scene.animbake_step))
        print('timerange =', timerange)
                            
        
        print('Handling these objects:\n', bakelist, '\n\n')
        
        bpy.ops.object.select_all(action='DESELECT')
        
        for ob in bakelist:
            if scene.animbake_xforms:
                newlist = []
                loclist = []
                rotlist = []
                scalist = []
                lenlist = []
                print('BAKING: ', ob.name, '\nFRAMES: ', timerange)
                ob.select_set(True)
                bpy.context.view_layer.objects.active = ob
                if not(ob.type == 'ARMATURE'):
                    ## OBJECT
                    if not(scene.animbake_toempty):
                        newempty = bake_object_to_empty(ob, timerange, tgtrotation)
                        transfer_trs_curves(newempty, ob)
                        bpy.ops.object.select_all(action='DESELECT')
                        newempty.select_set(True)
                        bpy.ops.object.delete()
                        ob.parent = None
                        if len(ob.constraints) >= 1:
                            for c in ob.constraints:
                                ob.constraints.remove(c)
                        if not(ob in fulllist):
                            fulllist.append(ob)
                    else:
                        ## BAKE OBJECT TO EMPTY
                        if not(scene.animbake_topath):
                            ## TO KEYFRAMES
                            newempty = bake_object_to_empty(ob, timerange, tgtrotation)
                            original_area_type = bpy.context.area.type
                            bpy.context.area.type = "GRAPH_EDITOR"
                            bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
                            bpy.ops.object.select_all(action='DESELECT')
                            newempty.select_set(True)
                            bpy.context.view_layer.objects.active = newempty
                            bpy.ops.graph.euler_filter()
                            bpy.context.area.type = original_area_type
                        else:
                            ## TO PATH
                            newname = ('nul.'+ob.name+'.BAKED.000')
                            newempty = bpy.data.objects.new(newname, None)
                            bpy.context.scene.collection.objects.link(newempty)
                            bpy.context.view_layer.objects.active = newempty
                            bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
                            bpy.context.object.constraints[0].target = ob
                            thepathdata = createmotioncurve(newempty,timerange)
                            thepath = thepathdata[0]
                            rotlist = thepathdata[2]
                            scalist = thepathdata[3]
                            thecount = thepathdata[4]
                            pathlength = getedgelengths(thepath)
                            print('pathlength =', pathlength)
                            for cnst in newempty.constraints:
                                newempty.constraints.remove(cnst)
                            newempty.constraints.new('FOLLOW_PATH')
                            newempty.constraints['Follow Path'].target = thepath
                            if scene.animbake_follow:
                                newempty.constraints['Follow Path'].use_curve_follow = True
                            listscount = 0
                            for theframe in timerange:
                                frm = float_to_int_decimal(theframe)[0]
                                sub = float_to_int_decimal(theframe)[1]
                                scene.frame_set(frm, subframe=sub)
                                #print('frm = ', frm)
                                if frm >= scene.animbake_end:
                                    thisframe = scene.animbake_end
                                else:
                                    thisframe = frm
                                if not(pathlength[len(pathlength)-1] == 0):
                                    theoffset = (-100 * (pathlength[listscount]/pathlength[len(pathlength)-1]))
                                else:
                                    theoffset = newempty.constraints['Follow Path'].offset
                                print('the offset = ', theoffset)
                                newempty.constraints['Follow Path'].offset = theoffset
                                newempty.constraints['Follow Path'].keyframe_insert('offset', frame=(frm+sub))
                                newempty.scale = scalist[listscount-1]
                                newempty.keyframe_insert('scale', frame=(frm+sub))
                                if not(scene.animbake_follow):
                                    newempty.rotation_euler = rotlist[listscount-1]
                                    newempty.keyframe_insert('rotation_euler', frame=(frm+sub))
                                listscount += 1
                            newlist.append(thepath)
                            thepath.data.use_path_follow = True
                            thepath.data.use_path_follow = False
                        newlist.append(newempty)
                        if not(newempty in fulllist):
                            fulllist.append(newempty)
                else:
                    ## ARMATURE
                    newlist = []
                    thebakebones = []
                    for bone in ob.pose.bones:
                        if bone.bone.select == True:
                            thebakebones.append(bone)
                    print('Baking ', len(thebakebones), ' bones on ', ob.name)
                    for bone in thebakebones:
                        newname = ('nul.'+ob.name+'_'+bone.name+'.000')
                        tempempty = bpy.data.objects.new(newname, None)
                        bpy.context.scene.collection.objects.link(tempempty)
                        bpy.context.view_layer.objects.active = tempempty
                        bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
                        bpy.context.object.constraints[0].target = ob
                        bpy.context.object.constraints[0].subtarget = bone.name
                        if not(scene.animbake_topath):
                            newempty = bake_object_to_empty(tempempty, timerange, tgtrotation)
                            bpy.ops.object.select_all(action='DESELECT')
                            tempempty.select_set(True)
                            bpy.ops.object.delete()
                        else:
                            ## TO PATH
                            newempty = tempempty
                            bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
                            bpy.context.object.constraints[0].target = ob
                            thepathdata = createmotioncurve(newempty,timerange)
                            thepath = thepathdata[0]
                            rotlist = thepathdata[2]
                            scalist = thepathdata[3]
                            thecount = thepathdata[4]
                            pathlength = getedgelengths(thepath)
                            for cnst in newempty.constraints:
                                newempty.constraints.remove(cnst)
                            newempty.constraints.new('FOLLOW_PATH')
                            newempty.constraints['Follow Path'].target = thepath
                            if scene.animbake_follow:
                                newempty.constraints['Follow Path'].use_curve_follow = True
                            for theframe in range(len(timerange)):
                                frm = float_to_int_decimal(timerange[theframe])[0]
                                sub = float_to_int_decimal(timerange[theframe])[1]
                                scene.frame_set(frm, subframe=sub)
                                if frm >= scene.animbake_end:
                                    frm = scene.animbake_end
                                if not(pathlength[len(pathlength)-1] == 0):
                                    theoffset = (-100 * (pathlength[theframe]/pathlength[len(pathlength)-1]))
                                else:
                                    theoffset = newempty.constraints['Follow Path'].offset
                                newempty.constraints['Follow Path'].offset = theoffset
                                newempty.constraints['Follow Path'].keyframe_insert('offset', frame=(frm+sub))
                                newempty.scale = scalist[theframe]
                                newempty.keyframe_insert('scale', frame=(frm+sub))
                                if not(scene.animbake_follow):
                                    newempty.rotation_euler = rotlist[theframe]
                                    newempty.keyframe_insert('rotation_euler', frame=(frm+sub))
                            newlist.append(thepath)
                            thepath.data.use_path_follow = True
                            thepath.data.use_path_follow = False
                        newlist.append(newempty)
                        fulllist.append(newempty)
            else:
                print('Skipping local object baking for ', ob.name)
            ## PARTICLES
            psys_bakelist = []
            if scene.animbake_particles:
                theprtsyslist = []
                ob.select_set(True)
                bpy.context.view_layer.objects.active = ob
                if len(ob.particle_systems) >= 1:
                    print('BAKING PARTICLE SYSTEMS FOUND ON: ', ob.name, '\nFRAMES: ', scene.animbake_start, ' to ' , scene.animbake_end)
                    psys_bakelist = []
                    print('filtering by ', scene.animbake_psysfilter)
                    for mod in ob.modifiers:
                        if mod.type == 'PARTICLE_SYSTEM':
                            print('processing modifier', ob.name, mod.name, mod.show_render, mod.show_viewport)
                            if scene.animbake_psysfilter == 'all':
                                psys_bakelist.append([mod.particle_system, mod.name, mod.show_viewport])
                                print('appending ', ob.name, mod.particle_system.name)
                            elif scene.animbake_psysfilter == 'both':
                                if mod.show_render and mod.show_viewport:
                                    psys_bakelist.append([mod.particle_system, mod.name, mod.show_viewport])
                                    print('appending ', ob.name, mod.particle_system.name)
                                else:
                                    print('skipped psys: ', ob.name, mod.particle_system.name)
                            elif scene.animbake_psysfilter == 'render':
                                if mod.show_render and not mod.show_viewport:
                                    psys_bakelist.append([mod.particle_system, mod.name, mod.show_viewport])
                                    print('appending ', ob.name, mod.particle_system.name)
                                else:
                                    print('skipped psys: ', ob.name, mod.particle_system.name)
                            elif scene.animbake_psysfilter == 'visible':
                                if mod.show_viewport and not mod.show_render:
                                    psys_bakelist.append([mod.particle_system, mod.name, mod.show_viewport])
                                    print('appending ', ob.name, mod.particle_system.name)
                                else:
                                    print('skipped psys: ', ob.name, mod.particle_system.name)
                    print('processing these particle systems on ', ob.name, '\n', psys_bakelist)
                    for prtsysset in psys_bakelist:
                        prtsys = prtsysset[0]
                        prtmodname = prtsysset[1]
                        prtmodvp = prtsysset[2]
                        newlist = []
                        thelive = ['ALIVE']
                        if prtsys.settings.use_dead:
                            thelive.append('DEAD')
                        if prtsys.settings.show_unborn:
                            thelive.append('UNBORN')
                        print('BAKING: ', prtsys.name)
                        random.seed(a=prtsys.seed)
                        ob.modifiers[prtmodname].show_viewport = True
                        ##  STILL NEED TO FIGURE OUT THE RANDOM METHOD BLENDER USES FOR ASSIGNING FROM THE GROUP
                        scene.frame_set(scene.animbake_start)
                        parentname = ('nul.'+ob.name+'.'+prtsys.name+'.parent.000')
                        parentempty = bpy.data.objects.new(parentname, None)
                        scene.collection.objects.link(parentempty)
                        depsgraph_01 = bpy.context.evaluated_depsgraph_get()
                        eval_ob = depsgraph_01.objects.get(ob.name, None)
                        prtsys = eval_ob.particle_systems[prtsys.name]
                        parentempty.location = (eval_ob.matrix_world.to_translation())
                        print('TRY SETTING NEW PARENT, ', parentname, ' AT CREATION TIME.')
                        for prt in range(0,len(prtsys.particles)):
                            newname = ('nul.'+ob.name+'.'+prtsys.name+'.BAKED.000')
                            print(prt, newname)
                            if scene.animbake_particles_mesh:
                                if prtsys.settings.render_type == 'OBJECT':
                                    theinstanceobj = prtsys.settings.instance_object.name
                                    thedata = bpy.data.objects[theinstanceobj].data
                                    newempty = bpy.data.objects.new(newname, thedata)
                                    print('NEW object duplicate CREATED: ', newname)
                                elif prtsys.settings.render_type == 'GROUP':
                                    thisgroup = prtsys.settings.instance_collection
                                    therand = random.randint(0,(len(thisgroup.objects)-1))
                                    theobjs = [thisgroup.name].objects
                                    thisobj = theobjs[therand]
                                    thedata = thisobj.data
                                    newempty = bpy.data.objects.new(newname, thedata)
                                    if len(thisobj.modifiers) >= 1:
                                        copymods(thisobj, newempty)
                                    print('NEW group member duplicate CREATED: ', newempty.name)
                                else:
                                    newempty = bpy.data.objects.new(newname, None)
                                    print('NEW empty CREATED: ', newempty.name)
                            else:
                                newempty = bpy.data.objects.new(newname, None)
                                print('NEW empty CREATED: ', newempty.name)
                            scene.collection.objects.link(newempty)
                            newlist.append(newempty)
                            fulllist.append(newempty)
                            newempty.parent = parentempty
                        print('ANIMATING ', len(newlist), ' OBJECTS FROM ', timerange[0], ' TO ', timerange[(len(timerange)-1)])
                        # for each frame, cycle thru point helpers and align to particles (counts should match)
                        for theframe in range(len(timerange)):
                            frm = float_to_int_decimal(timerange[theframe])[0]
                            sub = float_to_int_decimal(timerange[theframe])[1]
                            scene.frame_set(frm, subframe=sub)
                            depsgraph_01 = bpy.context.evaluated_depsgraph_get()
                            eval_ob = depsgraph_01.objects.get(ob.name, None)
                            for prt in range(0, prtsys.settings.count):
                                #print('PARTICLE: ', prt)
                                #print('OBJECT: ', newlist[prt].name)
                                thesize = (prtsys.particles[prt].size * 1.0)
                                
                                emit_loc, emit_rot, emit_scale = ob.matrix_world.decompose() 
                                emit_loc_mat = Matrix.Translation(emit_loc)
                                emit_rot_mat = emit_rot.to_matrix().to_4x4()
                                emit_scale_mat = (Matrix.Scale(emit_scale[0],4,(1,0,0))) @ (Matrix.Scale(emit_scale[1],4,(0,1,0))) @ (Matrix.Scale(emit_scale[2],4,(0,0,1)))
                                
                                prt_loc_mat = Matrix.Translation(prtsys.particles[prt].location)
                                prt_rot_mat = prtsys.particles[prt].rotation.to_matrix().to_4x4()
                                prt_scale_mat = (Matrix.Scale(thesize,4,(1,0,0))) @ (Matrix.Scale(thesize,4,(0,1,0))) @ (Matrix.Scale(thesize,4,(0,0,1)))
                                
                                if prtsys.settings.physics_type == 'BOIDS':
                                    newlist[prt].matrix_world = prt_loc_mat @ prt_rot_mat @ emit_rot_mat @ prt_scale_mat
                                else:
                                    newlist[prt].matrix_world = prt_loc_mat @ prt_rot_mat @ prt_scale_mat
                                
                                newlist[prt].keyframe_insert('location', frame=(frm+sub))
                                newlist[prt].keyframe_insert('rotation_euler', frame=(frm+sub))
                                newlist[prt].keyframe_insert('scale', frame=(frm+sub))
                                
                                if not(prtsys.particles[prt].alive_state in thelive):
                                    newlist[prt].hide_render = True
                                    #newlist[prt].hide_viewport = True
                                else:
                                    newlist[prt].hide_render = False
                                    newlist[prt].hide_viewport = False
                                
                                newlist[prt].keyframe_insert('hide_viewport', frame=(frm+sub))
                                newlist[prt].keyframe_insert('hide_render', frame=(frm+sub))
                        ob.modifiers[prtmodname].show_viewport = prtmodvp
            scene.frame_set(startframe)
            print('FINSHED BAKE************************************************************************\n')
        
        if len(fulllist) >= 1:
            bpy.ops.object.select_all(action='DESELECT')
            for ob in fulllist:
                ob.select_set(True)
                bpy.context.view_layer.objects.active = ob
        return{'FINISHED'}

#   OPERATOR animbakegettime MATCH TIMELINE
class BUTTON_OT_animbakegettime(bpy.types.Operator):
    '''Match Bake Time to Timeline'''
    bl_idname = "animbake.gettime"
    bl_label = "Match Timeline"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = bpy.context.scene
        scene.animbake_start = scene.frame_start
        scene.animbake_end = scene.frame_end
        timerange = list(frange(scene.animbake_start, (scene.animbake_end+1), scene.animbake_step))
        print('timerange =', timerange)
        print('DONE!')
        
        return{'FINISHED'}

#   PANEL animbake 
class VIEW3D_PT_animbake(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    #bl_region_type = 'TOOLS'
    bl_region_type = 'UI'
    #bl_region_type = 'TOOL_PROPS'
    bl_label = ("Animation Bake "+vsn)
    bl_context = "objectmode"
    bl_category = 'Chums'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "animbake_start")
        layout.prop(context.scene, "animbake_end")
        layout.prop(context.scene, "animbake_step")
        layout.operator("animbake.gettime", text=(BUTTON_OT_animbakegettime.bl_label))
        layout.prop(context.scene, "animbake_objects")
        split = layout.split(factor=0.05, align=True)
        col = split.column()
        split.prop(context.scene, "animbake_xforms")
        split = layout.split(factor=0.15, align=True)
        col = split.column()
        split.prop(context.scene, "animbake_toempty")
        split = layout.split(factor=0.15, align=True)
        col = split.column()
        split.prop(context.scene, "animbake_tgtrotation")
        split = layout.split(factor=0.2, align=True)
        col = split.column()
        split.prop(context.scene, "animbake_topath")
        split = layout.split(factor=0.15, align=True)
        col = split.column()
        split.prop(context.scene, "animbake_follow")
        split = layout.split(factor=0.05, align=False)
        col = split.column()
        split.prop(context.scene, "animbake_particles")
        split = layout.split(factor=0.15, align=True)
        col = split.column()
        split.prop(context.scene, "animbake_psysfilter")
        split = layout.split(factor=0.15, align=True)
        col = split.column()
        split.prop(context.scene, "animbake_particles_mesh")
        layout.operator("animbake.bake", text=(BUTTON_OT_animbakebake.bl_label))
        

####    REGISTRATION    ####

classes = ( BUTTON_OT_animbakebake, BUTTON_OT_animbakegettime, VIEW3D_PT_animbake )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.animbake_start = bpy.props.IntProperty \
        (
          name = "Start Frame",
          description = "",
          default = 1
        )
    bpy.types.Scene.animbake_end = bpy.props.IntProperty \
        (
          name = "End Frame",
          description = "",
          default = 250
        )
    bpy.types.Scene.animbake_step = bpy.props.FloatProperty \
        (
          name = "Step",
          description = "Set the step size in frames.",
          min = 0.05,
          max = 100.0,
          step = 5,
          default = 1.0
        )
    bpy.types.Scene.animbake_objects = bpy.props.BoolProperty \
        (
          name = "Selected",
          description = "KEEP THIS TURNED ON;\nJust some good advice for you there.",
          default = True
        )
    bpy.types.Scene.animbake_xforms = bpy.props.BoolProperty \
        (
          name = "Object Transforms",
          description = "",
          default = True
        )
    bpy.types.Scene.animbake_vkey = bpy.props.BoolProperty \
        (
          name = "Visual Keying",
          description = "",
          default = True
        )
    bpy.types.Scene.animbake_clearconstraints = bpy.props.BoolProperty \
        (
          name = "Clear Constraints",
          description = "",
          default = True
        )
    bpy.types.Scene.animbake_clearparents = bpy.props.BoolProperty \
        (
          name = "Clear Parents",
          description = "",
          default = True
        )
    bpy.types.Scene.animbake_toempty = bpy.props.BoolProperty \
        (
          name = "Bake to New Empty",
          description = "Create and Empty that matches the objects animation",
          default = True,
          update = update_objempty_ui
        )
    bpy.types.Scene.animbake_tgtrotation = bpy.props.EnumProperty \
        (
          name = "Rotation",
          description = "Set the rotation mode for the new empty (can help debug euler flips)",
          items=[('QUATERNION','Quaternion',''),
               ('XYZ','XYZ Euler',''),
               ],
          default=('XYZ')
        )
    bpy.types.Scene.animbake_topath = bpy.props.BoolProperty \
        (
          name = "Create Path for Empty",
          description = "Create a motion path curve and animate the Empty along it",
          default = False,
          update = update_topath_ui
        )
    bpy.types.Scene.animbake_follow = bpy.props.BoolProperty \
        (
          name = "Follow Path",
          description = "Caution: This will force the empty to follow the path and ignore the objects rotation",
          default = False,
          update = update_follow_ui
        )
    bpy.types.Scene.animbake_particles = bpy.props.BoolProperty \
        (
          name = "Particle Systems on Selected Objects",
          description = "Bake particle animation from ALL systems on SELECTED.",
          default = True
        )
    bpy.types.Scene.animbake_particles_mesh = bpy.props.BoolProperty \
        (
          name = "to Objects",
          description = "Attempt to bake (or simulate if using a group) particle MESH DATA if available, else bake to EMPTIES.",
          default = True,
          update = update_particle_mesh_ui
        )
    bpy.types.Scene.animbake_psysfilter = bpy.props.EnumProperty \
        (
          name = "Filter",
          description = "Choose to process only visible systems, renderable, or both.",
          items=[('visible','Only Visible',''),
                 ('render','Only Renderable',''),
                 ('both','Only Both View and Render',''),
                 ('all','All Systems',''),
                 ],
          default=('all')
        )

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.animbake_start
    del bpy.types.Scene.animbake_end
    del bpy.types.Scene.animbake_step
    del bpy.types.Scene.animbake_vkey
    del bpy.types.Scene.animbake_clearconstraints
    del bpy.types.Scene.animbake_clearparents
    del bpy.types.Scene.animbake_toempty
    del bpy.types.Scene.animbake_topath
    del bpy.types.Scene.animbake_follow
    del bpy.types.Scene.animbake_particles
    del bpy.types.Scene.animbake_particles_mesh
    del bpy.types.Scene.animbake_psysfilter
    del bpy.types.Scene.animbake_tgtrotation
    del bpy.types.Scene.animbake_xforms
    
    
if __name__ == "__main__":
    register()
