"""Editable second-density workcells. Run staged functions inside Blender.

Only DENS_ owned objects are managed. The approved scene is never replaced.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix

CELLS = [
    ('Crusher', 'Guarded crusher/feed module', (-12.6,18.2,0), (4.6,4,5.2)),
    ('FilterPress', 'Plate filter press', (14,-19.2,0), (6.2,3,2.9)),
    ('Gearbox', 'Gearbox rebuild stands', (-6.9,-17.8,0), (3.3,4,2.6)),
    ('Lubrication', 'Lubrication and test skid', (-5.3,-10.5,0), (3.4,4.5,2.9)),
    ('Welding', 'Welding fixture bench', (4.7,0,0), (2.6,3,2.8)),
    ('MotorRack', 'Motor and parts racking', (-5.4,1.8,0), (3.6,3,3)),
    ('TestCart', 'Hose/filter test cart', (4.2,7.6,0), (1.8,2,2.2)),
    ('Press', 'Hydraulic service press', (14,-13,0), (6,6,4.6)),
    ('Extraction', 'Dust extraction/filter skid', (15.2,16.4,0), (3.8,3.2,4.7)),
    ('Rotor', 'Spare rotor retaining stand', (-12.6,-3.3,0), (3,3,2.4)),
    ('BulkStore', 'Bulk spares shelving', (-18.4,7,0), (1.4,5,2.8)),
    ('Instruments', 'Instrument and electrical cabinets', (18.8,-.8,0), (1.2,3.2,3.2)),
    ('Receivers', 'Twin air receiver skid', (12,20.1,0), (2.4,1.5,3.3)),
    ('Manifold', 'Service valve manifold', (-7.5,21,0), (2,.8,3.3)),
    ('Consumables', 'Welding consumables rack', (-18.8,12.5,0), (.8,4,2.8)),
    ('Reels', 'Hose reel service bank', (-18.8,-7,0), (.8,4,2.8)),
    ('Conditioner', 'Conditioning separator skid', (11.2,-.8,0), (3,3,3.6)),
    ('Trolley', 'Belt service trolley', (4.1,-16.4,0), (1,3,1.4)),
]

# Coherent second processing train, kept entirely outside the central route.
# Existing main hopper/stockpile conveyor stays as its own accepted train.
BELTS = [
    ('C1', 'Yard receiving hopper to crusher', (-21,34,.8), (-12.6,19.4,5.85), 1.0),
    ('C2', 'Crusher discharge to distribution', (-12.6,16.0,2.9), (-14.1,14.9,3.6), .9),
    ('C3', 'Raised screen distribution conveyor', (-15,13.8,6.0), (-15,5.6,6.0), .85),
    ('C4', 'Screen B cross-feed', (-15,12.8,5.15), (-12,13.8,5.15), .8),
    ('C5', 'Screen A cross-feed', (-15,5.8,5.15), (-12,5.8,5.15), .8),
    ('C6', 'Recessed fines collection', (-12,12.6,-.25), (-12,1.8,-.25), .8),
    ('C7', 'Screened product to western stockpile', (-12,1,-.6), (-30,1,4), 1.0),
    ('C8', 'Full-length elevated coal trunk', (-11.2,-19.6,7.1), (-11.2,14.7,7.1), 1.4),
    ('C9', 'Coal receiving feed into elevator', (-9.3,-20.2,1.1), (-11.2,-20.2,1.1), .9),
    ('C10', 'Trunk powered cross-transfer to distributor', (-11.2,14.7,6.25), (-15,12.7,6.7), .9),
]

def collection(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        c['density_managed']=True
    elif not c.get('density_managed'):
        raise RuntimeError('Refusing to manage an unrelated collection: '+name)
    return c

def material(name, color, metallic=.4, roughness=.55):
    m=bpy.data.materials.get(name)
    if m is None:
        m=bpy.data.materials.new(name);m.use_nodes=True
        m.diffuse_color=(*color,1)
        p=m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*color,1)
        p.inputs['Metallic'].default_value=metallic
        p.inputs['Roughness'].default_value=roughness
    return m

def mesh_object(name, vertices, faces, c, m, location=(0,0,0), parent=None):
    if bpy.data.objects.get(name): raise RuntimeError('Duplicate managed name: '+name)
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(vertices,[],faces);me.update()
    me.materials.append(m)
    o=bpy.data.objects.new(name,me);c.objects.link(o);o.location=location
    if parent:o.parent=parent
    o['density_managed']=True
    return o

def octagon(w,d,r):
    r=min(r,w*.2,d*.2);x=w/2;y=d/2
    return [(-x+r,-y),(x-r,-y),(x,-y+r),(x,y-r),(x-r,y),(-x+r,y),(-x,y-r),(-x,-y+r)]

def body(name, p, size, c, m, parent=None, chamfer=.04):
    w,d,h=size
    profile=octagon(w,d,chamfer) if chamfer>0 else [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
    n=len(profile)
    vertices=[(x,y,z) for z in [-h/2,h/2] for x,y in profile]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_object(name,vertices,faces,c,m,p,parent)

def blockout():
    assert bpy.context.scene.name=='VERTO_Higgsfield_Mining_Concept'
    c=collection('DENS_Layout_Proxies')
    if len(c.objects):
        return {'already_present':True,'objects':len(c.objects)}
    m=material('DENS_LayoutPreview',(.13,.3,.34),.2)
    for key,label,position,size in CELLS:
        x,y,z=position
        o=body('DENS_'+key+'_Proxy',(x,y,z+size[2]/2),size,c,m,chamfer=.08)
        o['density_cell']=key;o['purpose']=label;o['stage']='blockout'
    return {'created':[o.name for o in c.objects],'workcells':len(CELLS)}

def checkpoint(label):
    import datetime
    folder=Path('/Users/rpriest/VERTOconnect-Scene-Work/density-performance')
    path=folder/(label+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.blend')
    assert not path.exists()
    before=bpy.data.filepath
    bpy.ops.wm.save_as_mainfile(filepath=str(path),copy=True)
    assert bpy.data.filepath==before
    return str(path)

def bounds_report():
    cells=[]
    for key,label,position,size in CELLS:
        cells.append({'cell':key,'purpose':label,'location':position,'dimensions':size})
    p=Path('/Users/rpriest/VERTOconnect-Scene-Work/density-performance/layout-cells.json')
    p.write_text(json.dumps(cells,indent=2))
    return str(p)

def refine_process_layout():
    c=collection('DENS_Layout_Proxies')
    changed=[]
    for key in ['Crusher','Press']:
        _,label,p,size=next(row for row in CELLS if row[0]==key)
        o=bpy.data.objects['DENS_'+key+'_Proxy']
        old=o.dimensions.copy()
        for axis in range(3):o.scale[axis]*=size[axis]/old[axis]
        o.location=(p[0],p[1],p[2]+size[2]/2)
        o['purpose']=label;changed.append(o.name)
    m=material('DENS_BeltPreview',(.025,.035,.038),.1)
    for key,label,a,b,width in BELTS:
        name='DENS_Belt_'+key+'_Proxy'
        start,end=Vector(a),Vector(b)
        o=bpy.data.objects.get(name) or body(name,(start+end)/2,(width,.2,(end-start).length),c,m,chamfer=.015)
        direction=(end-start).normalized()
        side=Vector((0,0,1)).cross(direction).normalized()
        up=direction.cross(side).normalized()
        o.rotation_euler=Matrix((side,up,direction)).transposed().to_euler()
        o['purpose']=label;o['density_cell']='Belt_'+key;o['stage']='blockout'
        changed.append(name)
    report={'cells':[{'name':x[0],'purpose':x[1],'location':x[2],'dimensions':x[3]} for x in CELLS],
            'belts':[{'name':x[0],'purpose':x[1],'start':x[2],'end':x[3],'width':x[4],
                      'grade_degrees':math.degrees(math.atan2(abs(x[3][2]-x[2][2]),math.hypot(x[3][0]-x[2][0],x[3][1]-x[2][1])))} for x in BELTS]}
    Path('/Users/rpriest/VERTOconnect-Scene-Work/density-performance/process-layout.json').write_text(json.dumps(report,indent=2))
    return {'changed':changed,'conveyors':len(BELTS),'max_grade_degrees':max(x['grade_degrees'] for x in report['belts'])}

# All components below remain native, editable meshes. Repeated cylinders share
# mesh data by profile/material, and have no subdivision modifiers.
def cylinder(name, a, b, radius, c, m, sides=16):
    a,b=Vector(a),Vector(b)
    key='DENS_shared_cylinder_%s_%d' % (m.name,sides)
    me=bpy.data.meshes.get(key)
    if me is None:
        vs=[(math.cos(i*math.tau/sides),math.sin(i*math.tau/sides),z)
            for z in [-.5,.5] for i in range(sides)]
        fs=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]
        fs += [(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
        me=bpy.data.meshes.new(key);me.from_pydata(vs,[],fs);me.materials.append(m)
        for face in list(me.polygons)[2:]:face.use_smooth=True
    o=bpy.data.objects.new(name,me);c.objects.link(o)
    o.location=(a+b)/2;o.scale=(radius,radius,(b-a).length)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    o['density_managed']=True
    return o

def detail_service_cells():
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    made=[]
    for key in ['MotorRack','BulkStore','Consumables','Reels','Receivers','FilterPress','Rotor']:
        c=collection('DENS_'+key)
        if len(c.objects):continue
        _,label,p,sz=next(row for row in CELLS if row[0]==key)
        x,y,z=p;w,d,h=sz
        def box(tag,off,size,mat=steel):
            return body('DENS_'+key+'_'+tag,(x+off[0],y+off[1],z+off[2]),size,c,mat)
        def rod(tag,a,b,r,mat=zinc):
            return cylinder('DENS_'+key+'_'+tag,Vector(p)+Vector(a),Vector(p)+Vector(b),r,c,mat)
        if key in ['MotorRack','BulkStore','Consumables']:
            for ix in [-1,1]:
                for iy in [-1,1]:
                    box('Foot_%s_%s'%(ix,iy),(ix*(w/2-.12),iy*(d/2-.12),.04),(.3,.3,.08))
                    box('Upright_%s_%s'%(ix,iy),(ix*(w/2-.12),iy*(d/2-.12),h/2),(.1,.1,h),zinc)
            for level in range(3):
                zz=.25+level*(h-.55)/2
                box('Shelf_%d'%level,(0,0,zz),(w,d,.1),steel)
                box('Edge_%d'%level,(0,-d/2,zz+.04),(w,.06,.18),yellow)
                for j in range(3):
                    if key=='MotorRack':
                        xx=(j-1)*w/3
                        rod('Motor_%d_%d'%(level,j),(xx,-.45,zz+.35),(xx,.45,zz+.35),.26,teal)
                        rod('Shaft_%d_%d'%(level,j),(xx,-.68,zz+.35),(xx,-.45,zz+.35),.07)
                        for f in range(5):rod('Fin_%d_%d_%d'%(level,j,f),(xx,-.32+f*.14,zz+.35),(xx,-.29+f*.14,zz+.35),.28,teal)
                        box('MotorFoot_%d_%d'%(level,j),(xx,0,zz+.12),(.48,.6,.14),teal)
                    else:
                        yy=(j-1)*d/3
                        box('Bin_%d_%d'%(level,j),(0,yy,zz+.24),(w*.65,d/3-.12,.38),teal)
                        box('Label_%d_%d'%(level,j),(w*.326,yy,zz+.25),(.012,.25,.1),zinc)
            rod('RearBrace',(-w/2,d/2,.25),(w/2,d/2,h-.1),.035)
        elif key=='Receivers':
            box('Skid',(0,0,.1),(w,d,.2))
            for i in [-1,1]:
                xx=i*.58
                rod('Vessel_'+str(i),(xx,0,.35),(xx,0,2.8),.44,teal)
                rod('Base_'+str(i),(xx,0,.2),(xx,0,.35),.48)
                rod('Top_'+str(i),(xx,0,2.8),(xx,0,2.88),.38,teal)
                rod('Valve_'+str(i),(xx,0,2.88),(xx,0,3.15),.06)
                rod('Gauge_'+str(i),(xx,-.43,2.35),(xx,-.52,2.35),.13)
                rod('GaugeFace_'+str(i),(xx,-.52,2.35),(xx,-.53,2.35),.1,rubber)
            rod('CommonHeader',(-.58,0,3.1),(.58,0,3.1),.06)
        elif key=='FilterPress':
            for xx in [-w*.4,w*.4]:
                for yy in [-.8,.8]:box('Leg_%s_%s'%(xx,yy),(xx,yy,.65),(.22,.22,1.3))
            box('DripTray',(0,0,.55),(w*.9,2,.12),zinc)
            for yy in [-.85,.85]:box('Rail_'+str(yy),(0,yy,1.55),(w,.14,.24),zinc)
            for i in range(18):box('FilterPlate_%02d'%i,(-1.6+i*.19,0,1.7),(.13,1.55,1.5),teal)
            for xx in [-2.1,2.1]:box('EndFrame_'+str(xx),(xx,0,1.65),(.3,1.9,1.9),yellow)
            rod('HydraulicBarrel',(2.15,0,1.65),(2.8,0,1.65),.24,teal)
            rod('Ram',(1.65,0,1.65),(2.3,0,1.65),.12)
        elif key=='Rotor':
            for yy in [-1,1]:
                box('Stand_'+str(yy),(0,yy,.5),(1.8,.35,1))
                box('Foot_'+str(yy),(0,yy,.08),(2.2,.7,.16))
            rod('Shaft',(0,-1.4,1.3),(0,1.4,1.3),.16)
            rod('Drum',(0,-.9,1.3),(0,.9,1.3),.65,teal)
            for i in range(8):rod('Flange_%d'%i,(0,-.85+i*.24,1.3),(0,-.8+i*.24,1.3),.73,zinc)
        elif key=='Reels':
            for i in range(3):
                yy=(i-1)*1.2
                box('Mount_%d'%i,(-.3,yy,1.7),(.12,.8,1.1))
                rod('Axle_%d'%i,(-.3,yy,1.7),(.3,yy,1.7),.08)
                rod('Hose_%d'%i,(-.15,yy,1.7),(.18,yy,1.7),.36,rubber)
                for xx in [-.2,.23]:rod('Cheek_%d_%s'%(i,xx),(xx,yy,1.7),(xx+.04,yy,1.7),.43,yellow)
                rod('HangingHose_%d'%i,(.2,yy+.25,1.65),(.2,yy+.25,.45),.035,rubber)
        for o in c.objects:o['density_cell']=key;o['purpose']=label
        proxy=bpy.data.objects.get('DENS_'+key+'_Proxy')
        if proxy:proxy.hide_render=True;proxy.hide_set(True)
        made.append({'cell':key,'components':len(c.objects)})
    return made

def detail_conveyors():
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    made=[]
    for key,label,a,b,width in BELTS:
        c=collection('DENS_Belt_'+key)
        if len(c.objects):continue
        a,b=Vector(a),Vector(b);delta=b-a;length=delta.length
        direction=delta.normalized();side=Vector((0,0,1)).cross(direction).normalized();up=direction.cross(side).normalized()
        basis=Matrix((side,up,direction)).transposed()
        def point(t,s=0,h=0):return a+direction*t+side*s+up*h
        def beam(tag,t,s,h,size,mat=steel):
            o=body('DENS_'+key+'_'+tag,point(t,s,h),size,c,mat,chamfer=.012)
            o.rotation_euler=basis.to_euler();return o
        def pipe(tag,aa,bb,r,mat=zinc):return cylinder('DENS_'+key+'_'+tag,aa,bb,r,c,mat)
        beam('CarryBelt',length/2,0,0,(width,.045,length),rubber)
        beam('ReturnBelt',length/2,0,-.33,(width,.035,length),rubber)
        for sign in [-1,1]:
            beam('Stringer_'+str(sign),length/2,sign*(width/2+.09),-.18,(.12,.28,length),yellow)
            beam('Skirt_'+str(sign),length/2,sign*(width/2-.025),.09,(.045,.18,length),steel)
        count=max(2,math.ceil(length/1.2))
        for i in range(count+1):
            t=length*i/count
            pipe('Idler_%02d'%i,point(t,-width*.55,-.075),point(t,width*.55,-.075),.065)
        for i,t in enumerate([0,length]):
            pipe('Pulley_'+str(i),point(t,-width*.58,-.16),point(t,width*.58,-.16),.18,steel)
            pipe('Shaft_'+str(i),point(t,-width*.72,-.16),point(t,width*.72,-.16),.05)
            for sign in [-1,1]:beam('Bearing_%s_%s'%(i,sign),t,sign*width*.65,-.16,(.2,.22,.25),teal)
        pipe('HeadDrive',point(length,width*.7,-.16),point(length,width*.7+.55,-.16),.2,teal)
        beam('DriveGuard',length,width*.7+.3,-.16,(.68,.52,.55),yellow)
        supports=max(1,math.ceil(length/3))
        for i in range(supports+1):
            if key in {'C4','C5','C8','C10','C11','C12'}:continue  # Long trussed spans use audited service-bay trestles below.
            t=length*i/supports
            if key=='C1' and i==supports:continue
            # The recessed belt is supported from its future concrete trench lining.
            floor=-.78 if key=='C6' else (-1.0 if point(t).z<.1 else 0.0)
            top=point(t,0,-.32)
            if top.z-floor<.12:continue
            for sign in [-1,1]:
                p=point(t,sign*(width/2+.09),-.32)
                foot=Vector((p.x,p.y,floor))
                body('DENS_'+key+'_Foot_%s_%s'%(i,sign),foot+Vector((0,0,.04)),(.38,.38,.08),c,steel)
                body('DENS_'+key+'_Leg_%s_%s'%(i,sign),(p+foot)/2,(.12,.12,p.z-floor),c,steel)
            pipe('Crossbrace_%d'%i,Vector((top.x,top.y,floor+.12))-side*width*.5,top+side*width*.5,.035,steel)
        # Accessible emergency pull-wire follows the exposed belt edge.
        if key!='C6':
            pipe('PullWire',point(.15,width/2+.21,.12),point(length-.15,width/2+.21,.12),.014,yellow)
            for stop_index,t in enumerate([.2,length-.2]):beam('StopSwitch_%02d'%stop_index,t,width/2+.21,.12,(.13,.15,.18),yellow)
        for o in c.objects:o['density_cell']='Belt_'+key;o['purpose']=label
        proxy=bpy.data.objects.get('DENS_Belt_'+key+'_Proxy')
        if proxy:proxy.hide_render=True;proxy.hide_set(True)
        made.append({'belt':key,'components':len(c.objects),'length_m':length})
    return made

def connect_building_openings():
    c=collection('DENS_BuildingConnections');cutters=collection('DENS_Cutters')
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    concrete=material('DENS_TrenchConcrete',(.23,.25,.24),0,.95)
    def cut(key,p,size,targets):
        name='DENS_Cut_'+key
        obj=bpy.data.objects.get(name) or body(name,p,size,cutters,steel,chamfer=0)
        obj.hide_render=True;obj.display_type='WIRE';obj.hide_set(True)
        for name in targets:
            target=bpy.data.objects[name]
            mod=target.modifiers.get('DENS_Opening_'+key) or target.modifiers.new('DENS_Opening_'+key,'BOOLEAN')
            mod.operation='DIFFERENCE';mod.solver='MANIFOLD';mod.object=obj
        return obj
    cut('RearInfeed',(-14.2,22.18,4.45),(1.9,1.3,1.9),['ENV_wall_rear_clad'])
    cut('WestOutfeed',(-20.18,1,1.5),(1.3,2,2.2),['ENV_wall_left_concrete'])
    cut('FinesTrench',(-12,6.7,-.35),(1.55,13,1.2),['ENV_floor_slab','ENV_floor_joints'])
    cut('OutfeedTail',(-13.8,1,-.4),(4.6,1.7,1.3),['ENV_floor_slab','ENV_floor_joints'])
    if len(c.objects):return {'openings':'updated','details':'already present'}
    for sign in [-1,1]:
        body('DENS_RearOpeningJamb_'+str(sign),(-14.2+sign*1.01,22.15,4.45),(.16,.65,2.12),c,steel)
        body('DENS_WestOpeningJamb_'+str(sign),(-20.15,1+sign*1.06,1.5),(.65,.16,2.4),c,steel)
    for sign in [-1,1]:
        body('DENS_RearOpeningSill_'+str(sign),(-14.2,22.15,4.45+sign*1.01),(2.18,.65,.16),c,steel)
        body('DENS_WestOpeningSill_'+str(sign),(-20.15,1,1.5+sign*1.16),(.65,2.28,.16),c,steel)
    body('DENS_TrenchInvert',(-12,6.7,-.86),(1.8,13.2,.16),c,concrete)
    for sign in [-1,1]:
        body('DENS_TrenchWall_'+str(sign),(-12+sign*.84,6.7,-.42),(.14,13.2,.88),c,concrete)
        # Low curb keeps spilled fines from the walking surface; end sections
        # have rail barriers, while screen hoppers enclose the middle run.
        body('DENS_TrenchCurb_'+str(sign),(-12+sign*.88,6.7,.08),(.12,13.2,.16),c,yellow)
        for yy in [.3,7,13.1]:
            cylinder('DENS_TrenchPost_%s_%s'%(sign,yy),(-12+sign*.94,yy,0),(-12+sign*.94,yy,1.1),.035,c,yellow)
        for zz in [.55,1.1]:
            cylinder('DENS_TrenchRail_%s_%s'%(sign,zz),(-12+sign*.94,.3,zz),(-12+sign*.94,13.1,zz),.03,c,yellow)
    body('DENS_TailTrenchInvert',(-13.8,1,-1.08),(4.8,1.9,.16),c,concrete)
    return {'wall_openings':2,'floor_cuts':2,'details':len(c.objects)}

def detail_machine_cells():
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    white=material('DENS_EnamelIvory',(.65,.68,.63),.25,.5)
    made=[]
    for key in ['Welding','TestCart','Trolley','Instruments','Manifold','Lubrication','Gearbox','Press','Extraction','Conditioner','Crusher']:
        c=collection('DENS_'+key)
        if len(c.objects):continue
        _,label,p,sz=next(row for row in CELLS if row[0]==key)
        x,y,z=p;w,d,h=sz
        def box(tag,off,size,mat=steel):return body('DENS_'+key+'_'+tag,Vector(p)+Vector(off),size,c,mat)
        def rod(tag,a,b,r,mat=zinc):return cylinder('DENS_'+key+'_'+tag,Vector(p)+Vector(a),Vector(p)+Vector(b),r,c,mat)
        def legs(zz,ww,dd):
            for i,xx in enumerate([-ww/2,ww/2]):
                for j,yy in enumerate([-dd/2,dd/2]):
                    box('Leg_%d_%d'%(i,j),(xx,yy,zz/2),(.14,.14,zz))
                    box('Pad_%d_%d'%(i,j),(xx,yy,.045),(.35,.35,.09))
        def motor(tag,xx,yy,zz,length=.7,r=.25):
            rod(tag+'Case',(xx,yy-length/2,zz),(xx,yy+length/2,zz),r,teal)
            for f in range(6):rod(tag+'Fin_%d'%f,(xx,yy-length*.4+f*length*.14,zz),(xx,yy-length*.4+f*length*.14+.025,zz),r*1.1,teal)
            rod(tag+'Shaft',(xx,yy-length*.7,zz),(xx,yy-length/2,zz),r*.28)
            box(tag+'Foot',(xx,yy,zz-r),(.6,length*.75,.12),teal)
        if key in ['Welding','TestCart','Trolley']:
            deck=.95 if key=='Welding' else .65
            legs(deck,w*.8,d*.8)
            box('Worktop',(0,0,deck),(w,d,.12),zinc)
            box('LowerShelf',(0,0,.25),(w*.9,d*.9,.08))
            if key=='Welding':
                box('Backscreen',(0,d/2,1.7),(w,.08,1.45),teal)
                box('WeldSet',(-.6,.5,.52),(.55,.65,.5),teal)
                for i in range(5):box('Workpiece_%d'%i,(-.7+i*.35,0,1.06),(.1,1.2,.1))
                box('ViceBase',(.65,-.7,1.13),(.4,.35,.25),teal)
                rod('ViceSpindle',(.65,-.9,1.23),(.65,-1.2,1.23),.025)
            elif key=='TestCart':
                box('InstrumentBack',(0,.6,1.25),(w*.8,.15,1),teal)
                for i in range(3):
                    rod('Filter_%d'%i,(-.5+i*.5,0,.75),(-.5+i*.5,0,1.25),.13,white)
                    rod('Gauge_%d'%i,(-.5+i*.5,.5,1.4),(-.5+i*.5,.41,1.4),.1,zinc)
            else:
                for i in range(4):rod('SpareIdler_%d'%i,(-.4,-1+i*.65,.85),(.4,-1+i*.65,.85),.13,zinc)
            if key!='Welding':
                for i,xx in enumerate([-w*.4,w*.4]):
                    for j,yy in enumerate([-d*.4,d*.4]):rod('Wheel_%d_%d'%(i,j),(xx-.07,yy,.14),(xx+.07,yy,.14),.14,rubber)
        elif key=='Instruments':
            box('Plinth',(0,0,.12),(w,d,.24))
            for i in range(3):
                yy=(i-1)*.98
                box('Cabinet_%d'%i,(0,yy,1.4),(1,.9,2.5),white)
                box('Door_%d'%i,(-.52,yy,1.4),(.035,.82,2.35),steel)
                box('Display_%d'%i,(-.545,yy,2.05),(.012,.38,.23),teal)
                rod('Handle_%d'%i,(-.57,yy+.25,1.15),(-.57,yy+.25,1.5),.018)
                for j in range(7):box('Louvre_%d_%d'%(i,j),(-.55,yy,.5+j*.08),(.025,.6,.022),zinc)
        elif key=='Manifold':
            legs(2.5,1.7,.45)
            for i in range(3):
                zz=.8+i*.65
                rod('Header_%d'%i,(-.9,0,zz),(.9,0,zz),.09,zinc)
                for j in [-1,1]:
                    rod('ValveBody_%d_%d'%(i,j),(j*.55,-.15,zz),(j*.55,-.34,zz),.12,teal)
                    rod('Handwheel_%d_%d'%(i,j),(j*.55,-.35,zz),(j*.55,-.38,zz),.16,yellow)
            rod('Riser',(-.85,0,.6),(-.85,0,3.15),.09,zinc)
        elif key=='Lubrication':
            box('Skid',(0,0,.12),(w,d,.24))
            box('OilReservoir',(0,.9,.8),(2.8,1.8,1.3),teal)
            box('ServiceLid',(0,.9,1.48),(2.65,1.65,.08),zinc)
            for i in [-1,1]:
                motor('Pump_%d'%i,i*.7,-.8,.65)
                rod('Discharge_%d'%i,(i*.7,-.5,.65),(i*.7,-.5,1.9),.06)
                rod('Filter_%d'%i,(i*.7,-.5,1.3),(i*.7,-.5,1.9),.16,white)
                rod('Return_%d'%i,(i*.7,-.5,1.85),(i*.7,.7,1.85),.06)
                rod('TankDrop_%d'%i,(i*.7,.7,1.85),(i*.7,.7,1.45),.06)
            box('Controls',(1.2,1,2.1),(.45,.6,.75),white)
        elif key=='Gearbox':
            legs(.9,2.7,2.8);box('Stand',(0,0,.9),(3,3.3,.2))
            box('LowerCasting',(0,0,1.35),(2.3,2.1,.7),teal)
            box('UpperCasting',(0,0,1.95),(1.8,1.9,.5),teal)
            box('SplitFlange',(0,0,1.7),(2.4,2.2,.12),zinc)
            for i in [-1,1]:
                rod('Bearing_%d'%i,(0,i*.95,1.65),(0,i*1.25,1.65),.4,teal)
                rod('Shaft_%d'%i,(0,i*1.1,1.65),(0,i*1.8,1.65),.17)
            for i in range(5):box('CastingRib_%d'%i,(-.9+i*.45,0,1.4),(.08,2.16,.65),teal)
        elif key=='Press':
            for i in [-1,1]:
                box('Foundation_%d'%i,(i*2,0,.15),(.9,3.8,.3))
                box('Column_%d'%i,(i*2,0,2.2),(.5,1,4.4),yellow)
            box('Crown',(0,0,4.1),(4.5,1.2,.6),yellow)
            box('WorkBed',(0,0,1.2),(4,1.6,.4),zinc)
            rod('HydraulicCylinder',(0,0,3.1),(0,0,4.3),.4,teal)
            rod('Piston',(0,0,2.4),(0,0,3.3),.22)
            box('ToolPlate',(0,0,2.35),(1.2,1,.18),zinc)
            box('Powerpack',(2.35,1.5,.6),(.9,1.2,1.2),teal)
            rod('HydraulicFeed',(2.35,1.5,1.2),(2.35,1.5,3.8),.045,rubber)
            rod('CrownFeed',(2.35,1.5,3.8),(0,0,3.8),.045,rubber)
        elif key in ['Extraction','Conditioner']:
            box('Skid',(0,0,.12),(w,d,.24));legs(.8,w*.7,d*.65)
            r=.8 if key=='Extraction' else .85
            rod('Vessel',(0,.15,.9),(0,.15,h-.6),r,white)
            rod('TopFlange',(0,.15,h-.7),(0,.15,h-.6),r*1.1,zinc)
            rod('BaseFlange',(0,.15,.85),(0,.15,1),r*1.1,zinc)
            box('InspectionHatch',(0,-r,1.8),(.8,.12,.9),teal)
            motor('Blower',1,-.3,.6,.7,.32)
            rod('BlowerRiser',(1,-.3,.7),(1,-.3,2),.16)
            rod('VesselConnection',(1,-.3,2),(0,-.3,2),.16)
            rod('TopOutlet',(0,.15,h-.6),(0,.15,h-.05),.22)
        elif key=='Crusher':
            # Raised feed and discharge leave room for the transfer beneath.
            legs(3.15,3.6,3.1)
            box('SupportDeck',(0,0,3.15),(4.1,3.5,.2))
            box('CrusherHousing',(0,0,3.9),(3,2.7,1.3),teal)
            for i in [-1,1]:
                rod('Bearing_%d'%i,(i*1.4,0,3.9),(i*1.9,0,3.9),.32,zinc)
                box('DriveGuard_%d'%i,(i*1.85,0,3.9),(.35,1.5,1.1),yellow)
            for i in range(4):box('HousingRib_%d'%i,(-1.1+i*.73,0,3.9),(.08,2.8,1.35),teal)
            # Open, four-sided receiving collar rather than a solid box.
            for sign in [-1,1]:
                box('HopperSide_%d'%sign,(sign*1.35,.4,4.85),(.1,2.4,.7),steel)
                box('HopperEnd_%d'%sign,(0,.4+sign*1.15,4.85),(2.7,.1,.7),steel)
            box('DischargeNeck',(0,-1.65,3.5),(1.2,.7,.6),steel)
        for o in c.objects:o['density_cell']=key;o['purpose']=label
        proxy=bpy.data.objects.get('DENS_'+key+'_Proxy')
        if proxy:proxy.hide_render=True;proxy.hide_set(True)
        made.append({'cell':key,'components':len(c.objects)})
    return made

def detail_transfers_and_coal():
    c=collection('DENS_Transfers')
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    coalmat=material('DENS_Coal',(.018,.022,.025),.05,.85)
    if len(c.objects):return {'already_present':True}
    def chute(key,a,b,width=.9,depth=.65):
        a,b=Vector(a),Vector(b);direction=(b-a).normalized()
        side=direction.cross(Vector((0,1,0)))
        if side.length<.1:side=direction.cross(Vector((1,0,0)))
        side.normalize();up=direction.cross(side).normalized();basis=Matrix((side,up,direction)).transposed()
        for index,offset,size in [(0,side*width/2,(.06,depth,(b-a).length)),(1,-side*width/2,(.06,depth,(b-a).length)),(2,up*depth/2,(width,.06,(b-a).length)),(3,-up*depth/2,(width,.06,(b-a).length))]:
            o=body('DENS_Chute_'+key+'_%d'%index,(a+b)/2+offset,size,c,steel)
            o.rotation_euler=basis.to_euler()
    chute('CrusherToC2',(-12.6,16.55,3.25),(-12.6,16.0,2.98),1.1,.7)
    chute('C2Lift',(-14.1,14.9,3.62),(-14.8,14.6,3.05),.85,.65)
    chute('LiftDistributor',(-15.2,14.2,6.55),(-15,13.8,6.08),.8,.65)
    chute('TrunkCrossfeed',(-11.2,14.7,7.15),(-11.2,14.7,6.32),1.1,.8)
    chute('CrossfeedDistributor',(-15,12.7,6.72),(-15,12.7,6.08),.85,.7)
    chute('DistributorB',(-15,12.8,6.02),(-15,12.8,5.22),.8,.65)
    chute('DistributorA',(-15,5.8,6.02),(-15,5.8,5.22),.8,.65)
    chute('ScreenB',(-12,13.8,5.19),(-12,13.8,4.05),.95,.8)
    chute('ScreenA',(-12,5.8,5.19),(-12,5.8,4.05),.95,.8)
    chute('UndersA',(-12,2.2,.35),(-12,2.2,-.19),.95,.8)
    chute('UndersB',(-12,10.2,.35),(-12,10.2,-.19),.95,.8)
    chute('C6ToC7',(-12,1.8,-.2),(-12,1,-.53),.95,.8)
    # Outdoor receiving bin: open walls, steel floor above belt tail, grizzly.
    for sign in [-1,1]:
        body('DENS_ReceivingSide_'+str(sign),(-21+sign*1.2,34.8,2),( .1,2.4,2),c,steel)
        body('DENS_ReceivingEnd_'+str(sign),(-21,34.8+sign*1.15,2),(2.4,.1,2),c,steel)
        for sy in [-1,1]:body('DENS_ReceivingLeg_%s_%s'%(sign,sy),(-21+sign*1.1,34.8+sy*1.1,.5),(.16,.16,1),c,steel)
    for i in range(8):body('DENS_Grizzly_%02d'%i,(-22+i*.28,34.8,3.03),(.065,2.4,.12),c,yellow)
    chute('Receiving',(-21,34.5,1.1),(-21,34,.86),1.1,.9)
    # A low-poly irregular coal heap, with radial tiers rather than a cone.
    vs=[(-30,1,2.6)];rings=24
    for radius,zz in [(1.5,2.1),(3.2,1.2),(4.8,0)]:
        for i in range(rings):
            angle=i*math.tau/rings;r=radius*(1+.07*math.sin(i*2.3))
            vs.append((-30+math.cos(angle)*r,1+math.sin(angle)*r*.8,zz))
    fs=[(0,1+i,1+(i+1)%rings) for i in range(rings)]
    for band in range(2):
        a=1+band*rings;b=a+rings
        fs += [(a+i,b+i,b+(i+1)%rings,a+(i+1)%rings) for i in range(rings)]
    mesh_object('DENS_WestCoalStockpile',vs,fs,c,coalmat)
    # Seed one small, shared irregular mesh. Every belt keeps its own batch zone.
    me=bpy.data.meshes.get('DENS_shared_coal')
    if me is None:
        me=bpy.data.meshes.new('DENS_shared_coal')
        me.from_pydata([(-.18,-.12,0),(.17,-.13,0),(.21,.13,.03),(-.13,.16,0),(-.1,-.07,.2),(.12,.06,.24)],[],[(0,1,4),(1,5,4),(1,2,5),(2,3,5),(3,4,5),(3,0,4),(0,3,2,1)])
        me.materials.append(coalmat)
    ores=collection('DENS_MovingCoal')
    for key,label,a,b,width in BELTS:
        a,b=Vector(a),Vector(b);direction=(b-a).normalized();side=Vector((0,0,1)).cross(direction).normalized();up=direction.cross(side).normalized()
        for i in range(10):
            o=bpy.data.objects.new('DENS_ORE_'+key+'_%02d'%i,me);ores.objects.link(o);o['density_managed']=True
            offset=side*((i%3)-1)*width*.2+up*.045
            phase=i*24
            for frame,t,scale in [(1,0,.001),(13,.05,1),(229,.95,1),(241,1,.001)]:
                o.location=a.lerp(b,t)+offset;o.scale=(scale,)*3
                o.keyframe_insert('location',frame=frame-phase);o.keyframe_insert('scale',frame=frame-phase)
            action=o.animation_data.action;action.name='DENS_CoalLoop_'+key+'_%02d'%i
            for layer in action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            for kp in fc.keyframe_points:kp.interpolation='LINEAR'
                            fc.modifiers.new('CYCLES')
    bpy.context.scene.frame_set(1)
    return {'transfer_components':len(c.objects),'animated_coal':len(ores.objects)}

def bake_coal_phases():
    # glTF slides each action to zero. Bake every lump onto the SAME positive
    # frame interval so its stagger cannot be lost during that normalization.
    scene=bpy.context.scene
    objects=[o for o in scene.objects if o.name.startswith('DENS_ORE_')]
    samples={o.name:[] for o in objects}
    for frame in range(1,242,3):
        scene.frame_set(frame)
        for o in objects:samples[o.name].append((frame,tuple(o.location),tuple(o.scale)))
    for o in objects:
        o.animation_data_clear()
        for frame,location,scale in samples[o.name]:
            o.location=location;o.scale=scale
            o.keyframe_insert('location',frame=frame);o.keyframe_insert('scale',frame=frame)
        o.animation_data.action.name='DENS_StaggeredLoop_'+o.name
        for layer in o.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for kp in fc.keyframe_points:kp.interpolation='LINEAR'
                        fc.modifiers.new('CYCLES')
    scene.frame_set(1)
    return {'baked_objects':len(objects),'common_interval':[1,241]}

def refine_yard_connections():
    # Replace only this pass's owned objects, never accepted source machinery.
    for name in ['DENS_Belt_C1','DENS_Transfers','DENS_MovingCoal','DENS_BuildingConnections']:
        c=bpy.data.collections.get(name)
        if c:
            assert c.get('density_managed')
            for o in list(c.objects):
                assert o.get('density_managed')
                bpy.data.objects.remove(o,do_unlink=True)
    cutter=bpy.data.objects.get('DENS_Cut_RearInfeed')
    if cutter:cutter.location.x=-14.2
    detail_conveyors();connect_building_openings();detail_transfers_and_coal();bake_coal_phases()
    c=collection('DENS_YardServices')
    if not len(c.objects):
        m=bpy.data.materials.get('DENS_TrenchConcrete')
        body('DENS_WestYardGround',(-30,0,-.13),(20,44,.26),c,m)
    # Cladding rails pass through the new rear aperture unless cut too.
    for name in ['YARD_rear_trim_3.55_-19.5','YARD_rear_trim_4.75_-19.5']:
        o=bpy.data.objects.get(name)
        if o:
            mod=o.modifiers.get('DENS_Opening_RearInfeed') or o.modifiers.new('DENS_Opening_RearInfeed','BOOLEAN')
            mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    return {'receiving_tail':[-21,34,.8],'rear_aperture_x':-14.2,'west_yard_ground':True}

def add_connected_services():
    c=collection('DENS_ConnectedServices')
    if len(c.objects):return {'already_present':True}
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    # Dust extraction above crane travel, dropping at the two actual machines.
    path=[(-12.6,18.2,5.2),(-12.6,18.2,9.5),(-12.6,20.7,9.5),(15.2,20.7,9.5),(15.2,16.55,9.5),(15.2,16.55,4.65)]
    for i,(a,b) in enumerate(zip(path,path[1:])):
        cylinder('DENS_DustDuct_%02d'%i,a,b,.29,c,zinc,24)
        direction=(Vector(b)-Vector(a)).normalized();length=(Vector(b)-Vector(a)).length
        for j in range(math.ceil(length/2)+1):
            pos=Vector(a).lerp(Vector(b),j/math.ceil(length/2))
            cylinder('DENS_DuctFlange_%02d_%02d'%(i,j),pos-direction*.035,pos+direction*.035,.34,c,steel,24)
    # Real hangers supported by rear wall girts, not floating duct sections.
    for i,xx in enumerate([-12,-6,0,6,12]):
        body('DENS_DuctWallBracket_%d'%i,(xx,21.35,9.15),(.12,1.3,.12),c,steel)
        body('DENS_DuctWallPlate_%d'%i,(xx,21.97,9.35),(.32,.08,.65),c,steel)
    # Paired longitudinal service mains sit outside the crane's +/-9.18m sweep.
    for side in [-1,1]:
        xx=side*10.4
        for k,zz in enumerate([5.7,6.1]):
            cylinder('DENS_ServiceMain_%s_%d'%(side,k),(xx,-18,zz),(xx,18,zz),.09,c,zinc)
            for i,yy in enumerate([-16,-8,0,8,14]):
                cylinder('DENS_MainFlange_%s_%d_%d'%(side,k,i),(xx,yy-.035,zz),(xx,yy+.035,zz),.135,c,steel)
        for i,yy in enumerate([-16,-8,0,8,14]):
            # Cantilever from nearby column line, with a diagonal brace.
            outer=side*16.6
            for post_index,post_x in enumerate([xx,outer]):
                body('DENS_ServicePost_%s_%d_%d'%(side,i,post_index),(post_x,yy,2.725),(.12,.12,5.45),c,steel)
                body('DENS_ServiceFoot_%s_%d_%d'%(side,i,post_index),(post_x,yy,.045),(.35,.35,.09),c,steel)
            body('DENS_PipeRackBeam_%s_%d'%(side,i),((xx+outer)/2,yy,5.45),(abs(outer-xx),.12,.16),c,steel)
            cylinder('DENS_PipeRackBrace_%s_%d'%(side,i),(outer,yy,4.6),(xx,yy,5.45),.035,c,steel)
    # Services visibly terminate on the new lubrication skid and receiver bank.
    for name,a,b in [('LubeFeed',(-10.4,-10.5,5.7),(-5.3,-10.5,5.7)),('LubeDrop',(-5.3,-10.5,5.7),(-5.3,-10.5,2.2)),('AirDrop',(10.4,18,6.1),(12,20.1,3.1))]:
        cylinder('DENS_'+name,a,b,.055,c,zinc)
    # Visible shutoffs on the low accessible service drops.
    cylinder('DENS_LubeValve',(-5.3,-10.5,2.7),(-5.3,-10.8,2.7),.12,c,teal)
    cylinder('DENS_LubeHandwheel',(-5.3,-10.8,2.7),(-5.3,-10.84,2.7),.18,c,yellow)
    return {'service_components':len(c.objects),'minimum_cross_crane_duct_bottom':9.16,'crane_trolley_top':8.72}

def add_main_coal_trunk():
    detail_conveyors()
    c=collection('DENS_MainCoalTrunk')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    x=-11.2
    for side in [-1,1]:
        xx=x+side*.86
        body('DENS_TrunkLowerChord_'+str(side),(xx,-2.45,6.2),(.18,34.3,.18),c,yellow)
        body('DENS_TrunkUpperChord_'+str(side),(xx,-2.45,6.85),(.18,34.3,.18),c,yellow)
        for i in range(23):
            ya=-19.6+i*34.3/23;yb=-19.6+(i+1)*34.3/23
            cylinder('DENS_TrunkDiagonal_%s_%02d'%(side,i),(xx,ya,6.2 if i%2==0 else 6.85),(xx,yb,6.85 if i%2==0 else 6.2),.055,c,steel)
        for i,yy in enumerate([-19,-10,-6,7,15]):
            body('DENS_TrunkPier_%s_%02d'%(side,i),(xx,yy,3.1),(.2,.2,6.2),c,steel)
            body('DENS_TrunkFoot_%s_%02d'%(side,i),(xx,yy,.075),(.5,.5,.15),c,steel)
    # Enclosed bucket elevator provides a credible low-to-high feed without
    # an impossibly steep ordinary belt; guards cover its internal chain.
    body('DENS_BucketElevatorCasing',(x,-20.2,3.75),(1.15,1.15,7.5),c,teal)
    body('DENS_BucketElevatorBase',(x,-20.2,.12),(1.6,1.6,.24),c,steel)
    body('DENS_ElevatorTopDrive',(x,-20.2,7.6),(1.5,1.4,.55),c,yellow)
    for i in range(6):
        body('DENS_ElevatorInspection_%02d'%i,(x+.59,-20.2,.7+i*1.1),(.06,.65,.65),c,steel)
    # Hooded transfer at trunk discharge, descending into the screen distribution transfer.
    a=Vector((x,14.7,7.15));b=Vector((-15,12.8,4.95));direction=(b-a).normalized()
    side=Vector((0,0,1)).cross(direction).normalized();up=direction.cross(side).normalized();basis=Matrix((side,up,direction)).transposed()
    for i,offset,size in [(0,side*.58,(.08,1.0,(b-a).length)),(1,-side*.58,(.08,1.0,(b-a).length)),(2,up*.5,(1.2,.08,(b-a).length)),(3,-up*.5,(1.2,.08,(b-a).length))]:
        o=body('DENS_TrunkDischargeChute_%d'%i,(a+b)/2+offset,size,c,steel);o.rotation_euler=basis.to_euler()
    # Recreate this pass's coal so the additional lines receive phased loops.
    for name in ['DENS_Transfers','DENS_MovingCoal']:
        coll=collection(name)
        for o in list(coll.objects):
            assert o.get('density_managed');bpy.data.objects.remove(o,do_unlink=True)
    detail_transfers_and_coal();bake_coal_phases()
    return {'main_belt_length_m':34.3,'width_m':1.4,'height_m':7.1,'new_conveyors':2,'components':len(c.objects)}

def repair_audit_findings():
    # Boolean operands must be closed manifold cubes. Zero-chamfer octagons
    # contain duplicate vertices and can remove an entire wall in Exact mode.
    for o in collection('DENS_Cutters').objects:
        size=tuple(o.dimensions);w,d,h=[v/2 for v in size]
        vs=[(-w,-d,-h),(w,-d,-h),(w,d,-h),(-w,d,-h),(-w,-d,h),(w,-d,h),(w,d,h),(-w,d,h)]
        fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        me=bpy.data.meshes.new(o.name+'_Manifold');me.from_pydata(vs,[],fs);me.update();o.data=me;o.scale=(1,1,1)
    for o in bpy.context.scene.objects:
        for modifier in o.modifiers:
            if modifier.type=='BOOLEAN' and modifier.name.startswith('DENS_Opening_'):
                modifier.solver='MANIFOLD'
    for name in ['DENS_Extraction','DENS_ConnectedServices']:
        coll=collection(name)
        for o in list(coll.objects):
            assert o.get('density_managed');bpy.data.objects.remove(o,do_unlink=True)
    detail_machine_cells();add_connected_services()
    return {'manifold_cutters':len(collection('DENS_Cutters').objects),'extractor_center':[15.2,16.4,0]}



def repair_conveyor_clearances():
    for name in ['DENS_Belt_C1','DENS_Belt_C2','DENS_Belt_C3','DENS_Belt_C4','DENS_Belt_C5','DENS_Belt_C6','DENS_Belt_C10','DENS_TransferSupports','DENS_Transfers','DENS_MovingCoal']:
        for obj in list(collection(name).objects):
            assert obj.get('density_managed');bpy.data.objects.remove(obj,do_unlink=True)
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith('DENS_TrunkDischargeChute_'):bpy.data.objects.remove(obj,do_unlink=True)
    detail_conveyors();detail_transfers_and_coal();bake_coal_phases()
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    c=collection('DENS_TransferSupports')
    body('DENS_DistributionElevator',(-15.2,14.6,3.35),(1.0,1.0,6.7),c,teal)
    body('DENS_DistributionElevatorBase',(-15.2,14.6,.1),(1.3,1.3,.2),c,steel)
    body('DENS_DistributionElevatorDrive',(-15.2,14.6,6.85),(1.3,1.3,.35),c,yellow)
    for i in range(5):body('DENS_DistributionElevatorInspection_%d'%i,(-15.72,14.6,.7+i*1.1),(.05,.6,.65),c,steel)
    # Each cross-feed hangs from a supported overhead beam. Cross saddles
    # follow the belt in plan and sit below the return strand.
    for key in ['C4','C5','C10']:
        _,_,aa,bb,width=next(row for row in BELTS if row[0]==key)
        a,b=Vector(aa),Vector(bb);side=Vector((0,0,1)).cross(b-a).normalized()
        yy=(a.y+b.y)/2
        overhead=5.95 if key=='C4' else 8.6
        body('DENS_'+key+'_OverheadBeam',(-13.4,yy,overhead),(6.8,.22,.28),c,steel)
        for xx in [-16.8,-10]:
            body('DENS_'+key+'_SupportColumn_'+str(xx),(xx,yy,overhead/2),(.18,.18,overhead),c,steel)
            body('DENS_'+key+'_SupportPad_'+str(xx),(xx,yy,.07),(.5,.5,.14),c,steel)
        for i,t in enumerate([.2,.8]):
            at=a.lerp(b,t);at.z-=.55
            for sign in [-1,1]:
                foot=at+side*sign*(width/2+.18)
                elbow=Vector((foot.x,foot.y,min(overhead,at.z+1.1)))
                cylinder('DENS_'+key+'_Hanger_%s_%s'%(i,sign),foot,elbow,.035,c,steel)
                if overhead>elbow.z+.01:cylinder('DENS_'+key+'_HangerTop_%s_%s'%(i,sign),elbow,(foot.x,yy,overhead),.035,c,steel)
            cylinder('DENS_'+key+'_Saddle_%d'%i,at-side*(width/2+.22),at+side*(width/2+.22),.05,c,yellow)
    a=Vector(BELTS[0][2]);b=Vector(BELTS[0][3]);direction=(b-a).normalized()
    side=Vector((0,0,1)).cross(direction).normalized();up=direction.cross(side).normalized()
    mid=b-direction*.3-up*.58
    cylinder('DENS_C1_HeadSaddle',mid-side*.75,mid+side*.75,.055,c,yellow)
    for sign in [-1,1]:
        foot=mid+side*sign*.64
        cylinder('DENS_C1_HeadRiser_'+str(sign),foot,foot+up*.4,.05,c,steel)
        # Offset posts stand on the existing crusher support deck, outside
        # its housing; a bracket carries the end saddle inward.
        base=Vector((-12.6+sign*1.8,19.7,3.2));top=Vector((base.x,base.y,mid.z))
        cylinder('DENS_C1_HeadPedestal_'+str(sign),base,top,.085,c,steel)
        cylinder('DENS_C1_HeadBracket_'+str(sign),top,foot,.07,c,steel)
    for obj in c.objects:obj['density_cell']='TransferSupports'
    moved=[]
    for obj in bpy.context.scene.objects:
        if obj.name.startswith('WKS_bench_L2_') and not obj.get('density_outfeed_clearance'):
            obj.location.y+=.8;obj['density_outfeed_clearance']=True;moved.append(obj.name)
    return {'underpass':'C2 at 3.6m; enclosed elevator south of gallery to 6m distributor','moved_bench_parts':moved,'conveyors':len(BELTS)}


def add_upper_service_bays():
    """Continuous ventilation trunks and cable ladders, below roof trusses.
    Upper-bay density uses purposeful services, without entering crane travel
    or the central approach. Rear connections step above the gallery headroom.
    """
    c=collection('DENS_UpperServiceBays')
    if len(c.objects):return {'already_present':True}
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    blue=material('DENS_VentIdentification',(.08,.24,.32),.2,.6)
    for sign in [-1,1]:
        xx=sign*17.8
        path=[(xx,-17,7.35),(xx,15.3,7.35),(xx,15.3,9.5)]
        path+=([(xx,18.2,9.5),(-12.6,18.2,9.5)] if sign<0 else [(xx,16.55,9.5),(15.2,16.55,9.5)])
        for leg,(aa,bb) in enumerate(zip(path,path[1:])):
            a,b=Vector(aa),Vector(bb);d=(b-a).normalized();count=max(1,math.ceil((b-a).length/2.75))
            cylinder('DENS_VentMain_%s_%s'%(sign,leg),a,b,.55,c,zinc,24)
            for i in range(count+1):
                at=a.lerp(b,i/count)
                cylinder('DENS_VentJoint_%s_%s_%s'%(sign,leg,i),at-d*.025,at+d*.025,.59,c,steel,24)
        # Tapered branch boxes and louvres distribute air into workshop bays.
        for i,yy in enumerate([-15,-9.5,-4,1.5,7,12.5]):
            body('DENS_VentRegister_%s_%s'%(sign,i),(xx,yy,6.81),(.9,1.15,.2),c,steel)
            for j in range(6):body('DENS_VentLouvre_%s_%s_%s'%(sign,i,j),(xx,yy-.45+j*.18,6.69),(.83,.075,.08),c,zinc)
            cylinder('DENS_VentBand_%s_%s'%(sign,i),(xx,yy-.06,7.35),(xx,yy+.06,7.35),.558,c,blue,24)
        # Roof-bottom chords at these authored truss lines carry the hangers.
        for i,yy in enumerate([-13.75,-8.25,-2.75,2.75,8.25,13.75]):
            for side in [-1,1]:
                px=xx+side*.64
                cylinder('DENS_VentHanger_%s_%s_%s'%(sign,i,side),(px,yy,6.27),(px,yy,8.88),.027,c,steel)
                body('DENS_VentHangerPlate_%s_%s_%s'%(sign,i,side),(px,yy,8.86),(.18,.23,.045),c,steel)
            body('DENS_VentSaddle_%s_%s'%(sign,i),(xx,yy,6.72),(1.4,.10,.10),c,steel)
        # Side-by-side cable trays follow the same structural support rhythm.
        tx=sign*16.65
        for side in [-1,1]:
            body('DENS_CableLadderRail_%s_%s'%(sign,side),(tx+side*.32,-.85,6.40),(.055,32.3,.15),c,zinc)
        for i in range(65):
            yy=-17+i*32.3/64
            body('DENS_CableLadderRung_%s_%s'%(sign,i),(tx,yy,6.35),(.64,.04,.04),c,zinc)
        for i in range(4):
            px=tx-.22+i*.145
            cylinder('DENS_CableBundle_%s_%s'%(sign,i),(px,-17,6.45),(px,15.3,6.45),.045,c,rubber,8)
        for i,yy in enumerate([-13.75,-8.25,-2.75,2.75,8.25,13.75]):
            body('DENS_CableTraySupport_%s_%s'%(sign,i),((xx+tx)/2,yy,6.27),(abs(xx-tx)+.7,.08,.08),c,steel)
            cylinder('DENS_CableTrayHanger_%s_%s'%(sign,i),(tx-sign*.4,yy,6.27),(tx-sign*.4,yy,8.88),.027,c,steel)
    for obj in c.objects:obj['density_cell']='UpperServiceBays';obj['purpose']='Supported ventilation and cable distribution outside crane envelope'
    return {'components':len(c.objects),'ventilation_runs':2,'cable_ladders':2,'main_run_length_m':32.3}


def add_workshop_air_distribution():
    """Receiver-fed perimeter air main with supported, valved service drops."""
    c=collection('DENS_AirDistribution')
    if len(c.objects):return {'already_present':True}
    blue=material('DENS_AirMainBlue',(.045,.19,.29),.45,.38)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    def pipe(tag,points,r=.085):
        # Continuous swept elbow rings avoid disconnected cylinders at bends.
        pts=[Vector(p) for p in points];rounded=[pts[0]]
        for a,b,d in zip(pts,pts[1:],pts[2:]):
            incoming=(b-a).normalized();outgoing=(d-b).normalized()
            radius=min(.28,(b-a).length*.25,(d-b).length*.25)
            assert abs(incoming.dot(outgoing))<.001,'Air fittings use square elbows'
            center=b-incoming*radius+outgoing*radius
            for j in range(7):
                angle=math.pi*j/12
                rounded.append(center-outgoing*radius*math.cos(angle)+incoming*radius*math.sin(angle))
        rounded.append(pts[-1]);vertices=[];faces=[];sides=12;previous_u=None
        for i,p in enumerate(rounded):
            tangent=(rounded[min(i+1,len(rounded)-1)]-rounded[max(0,i-1)]).normalized()
            axis=Vector((0,0,1)) if abs(tangent.z)<.9 else Vector((1,0,0))
            u=(previous_u-tangent*previous_u.dot(tangent)).normalized() if previous_u is not None else tangent.cross(axis).normalized()
            v=tangent.cross(u).normalized();previous_u=u
            vertices.extend([tuple(p+r*(u*math.cos(j*math.tau/sides)+v*math.sin(j*math.tau/sides))) for j in range(sides)])
        for i in range(len(rounded)-1):
            for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
        faces.extend([tuple(reversed(range(sides))),tuple((len(rounded)-1)*sides+j for j in range(sides))])
        obj=mesh_object('DENS_Air_'+tag,vertices,faces,c,blue)
        for polygon in obj.data.polygons[:-2]:polygon.use_smooth=True
        return obj
    # The feed meets the existing receiver common header at (12,20.1,3.1).
    pipe('ReceiverFeed',[(12,20.1,3.1),(12,20.1,6.55),(12,21.4,6.55),(12,21.4,5.9)],.06)
    pipe('RearHeader',[(-18.9,21.4,5.9),(18.9,21.4,5.9)])
    for sign in [-1,1]:
        xx=sign*18.9
        pipe('SideMain_'+str(sign),[(xx,21.4,5.9),(xx,-17.2,5.9)])
        for i,yy in enumerate([-13.75,-10.5,-5,.5,6,11.5,17]):
            if sign<0 and i==0:
                cylinder('DENS_Air_PlenumHanger',(xx,yy,5.74),(xx,yy,8.88),.027,c,steel)
                continue
            body('DENS_Air_WallPlate_%s_%s'%(sign,i),(sign*19.75,yy,5.75),(.08,.28,.42),c,steel)
            body('DENS_Air_Cantilever_%s_%s'%(sign,i),(sign*19.3,yy,5.74),(.9,.08,.08),c,steel)
            cylinder('DENS_Air_Clamp_%s_%s'%(sign,i),(xx,yy-.035,5.9),(xx,yy+.035,5.9),.105,c,zinc)
        for i,yy in enumerate([-4.5,9.7,15.3] if sign<0 else [-14,-8.7,8.7]):
            # Riser hugs the wall; an inward outlet remains outside walkways.
            pipe('Drop_%s_%s'%(sign,i),[(xx,yy,5.9),(xx,yy,1.45),(xx-sign*.25,yy,1.45)],.028)
            for z in [1.8,3.7,5.5]:
                cylinder('DENS_Air_DropBracket_%s_%s_%s'%(sign,i,z),(xx,yy,z),(sign*19.75,yy,z),.018,c,zinc,8)
            cylinder('DENS_Air_Valve_%s_%s'%(sign,i),(xx,yy,1.6),(xx,yy,1.78),.065,c,zinc)
            body('DENS_Air_ValveHandle_%s_%s'%(sign,i),(xx-sign*.1,yy,1.72),(.27,.045,.045),c,yellow)
            cylinder('DENS_Air_QuickCoupler_%s_%s'%(sign,i),(xx-sign*.25,yy,1.45),(xx-sign*.32,yy,1.45),.047,c,zinc)
    for i,xx in enumerate([-16,-11,-6,0,6,11,16]):
        body('DENS_Air_RearPlate_'+str(i),(xx,21.85,5.75),(.28,.08,.42),c,steel)
        body('DENS_Air_RearBracket_'+str(i),(xx,21.6,5.74),(.08,.5,.08),c,steel)
        cylinder('DENS_Air_RearClamp_'+str(i),(xx-.035,21.4,5.9),(xx+.035,21.4,5.9),.105,c,zinc)
    for o in c.objects:o['density_cell']='AirDistribution';o['purpose']='Receiver-fed compressed air service main and isolated workshop outlets'
    return {'components':len(c.objects),'service_outlets':6,'receiver_feed':[12,20.1,3.1],'main_length_m':115.0}


def add_rear_compressor():
    """Packaged workshop compressor in the verified clear rear-door side bay."""
    c=collection('DENS_RearCompressor')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    x,y=4.4,20.0
    body('DENS_Compressor_Plinth',(x,y,.10),(1.8,2.5,.2),c,steel)
    for xx in [-.62,.62]:
        for yy in [-.9,.9]:body('DENS_Compressor_Isolator_%s_%s'%(xx,yy),(x+xx,y+yy,.24),(.25,.25,.12),c,rubber)
    body('DENS_Compressor_Cabinet',(x,y,1.42),(1.6,2.3,2.26),c,teal,chamfer=.07)
    body('DENS_Compressor_Roof',(x,y,2.59),(1.7,2.4,.08),c,steel)
    # Facing the workshop, recessed access panels and simple functional controls.
    body('DENS_Compressor_ServiceDoor',(x,y-1.17,.75),(1.4,.04,.75),c,steel)
    body('DENS_Compressor_ControlPlate',(x+.48,y-1.18,2.14),(.4,.04,.58),c,zinc)
    body('DENS_Compressor_Display',(x+.48,y-1.205,2.25),(.27,.015,.17),c,rubber)
    cylinder('DENS_Compressor_Stop',(x+.48,y-1.21,2.02),(x+.48,y-1.25,2.02),.055,c,yellow)
    for yy in [-.75,.75]:
        body('DENS_Compressor_SidePanel_'+str(yy),(x+.815,y+yy,1.45),(.025,.6,1.75),c,steel)
        for i in range(9):body('DENS_Compressor_Louvre_%s_%s'%(yy,i),(x+.835,y+yy,1.05+i*.10),(.02,.49,.035),c,zinc)
    for xx in [-.66,.66]:
        for zz in [.45,.95,2.4]:cylinder('DENS_Compressor_Fastener_%s_%s'%(xx,zz),(x+xx,y-1.205,zz),(x+xx,y-1.22,zz),.022,c,zinc,6)
    # A low-speed guarded cooling fan gives this operational unit readable motion.
    center=Vector((x-.2,y-1.29,1.67))
    cylinder('DENS_Compressor_FanBack',center+Vector((0,.08,0)),center+Vector((0,.12,0)),.40,c,rubber,24)
    rotor=bpy.data.objects.new('DENS_Compressor_FanMotion',None);c.objects.link(rotor);rotor.location=center
    rotor['density_managed']=True
    for i in range(4):
        angle=i*math.pi/2
        blade=body('DENS_Compressor_FanBlade_'+str(i),(.2*math.cos(angle),0,.2*math.sin(angle)),(.33,.035,.12),c,zinc,parent=rotor,chamfer=.025)
        blade.rotation_euler.y=-angle
    cylinder('DENS_Compressor_FanHub',center-Vector((0,.015,0)),center+Vector((0,.035,0)),.075,c,zinc)
    # Guard bars stay fixed and cannot rotate through the surrounding case.
    for i in range(-3,4):
        offset=i*.105;half=math.sqrt(.39*.39-offset*offset)
        cylinder('DENS_Compressor_GrilleV_'+str(i),center+Vector((offset,-.08,-half)),center+Vector((offset,-.08,half)),.012,c,steel,8)
        cylinder('DENS_Compressor_GrilleH_'+str(i),center+Vector((-half,-.095,offset)),center+Vector((half,-.095,offset)),.012,c,steel,8)
    for frame in range(1,242,6):
        rotor.rotation_euler.y=(frame-1)/24*math.tau
        rotor.keyframe_insert('rotation_euler',frame=frame)
    rotor.animation_data.action.name='DENS_Compressor_CoolingFanLoop'
    for layer in rotor.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points:kp.interpolation='LINEAR'
                    fc.modifiers.new('CYCLES')
    # Rear discharge rises within the skid footprint, then meets the air header.
    cylinder('DENS_Compressor_DischargeRiser',(x,y+.9,2.5),(x,y+.9,5.9),.045,c,zinc)
    cylinder('DENS_Compressor_HeaderConnection',(x,y+.9,5.9),(x,21.4,5.9),.045,c,zinc)
    for z in [2.75,4.2,5.6]:
        cylinder('DENS_Compressor_RiserBracket_'+str(z),(x,y+.9,z),(x,21.85,z),.025,c,steel)
    for o in c.objects:o['density_cell']='RearCompressor';o['purpose']='Workshop compressed air supply with guarded cooling fan'
    bpy.context.scene.frame_set(1)
    return {'components':len(c.objects),'footprint':[3.5,18.75,5.3,21.25],'cooling_fan_rpm':60,'header_connection':[4.4,21.4,5.9]}


def repair_east_workbenches():
    """Consolidate overlapping legacy workbenches without narrowing gallery access."""
    scene=bpy.context.scene
    if scene.get('density_east_benches_repaired'):return {'already_present':True}
    hidden=[]
    for suffix in ['top','frame','drawers']:
        o=bpy.data.objects['WKS_bench_S1_'+suffix]
        o.hide_render=True;o.hide_set(True)
        o['density_replacement']='Overlapping table consolidated into EXP service benches'
        hidden.append(o.name)
    def move_bounds(name,minimum):
        o=bpy.data.objects[name]
        corners=[o.matrix_world@Vector(v)for v in o.bound_box]
        low=Vector([min(v[i]for v in corners)for i in range(3)])
        matrix=o.matrix_world.copy();matrix.translation+=Vector(minimum)-low;o.matrix_world=matrix
    move_bounds('WKS_bench_S1_vice',(18.0,4.50,1.06))
    move_bounds('WKS_bench_S1_bins',(18.0,6.10,1.06))
    scene['density_east_benches_repaired']=True
    return {'hidden_redundant_parts':hidden,'vice_on':'EXP_Bench_Top_4','bins_on':'EXP_Bench_Top_7','wall_pegboard_retained':True}


def add_dust_recovery_skid():
    """Twin cyclone vacuum receiver in the clear inner rear process bay."""
    c=collection('DENS_DustRecovery')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    x,y=9.8,10.8
    body('DENS_DustRecovery_Skid',(x,y,.10),(2.8,3.2,.2),c,steel)
    for xx in [x-1.15,x+1.15]:
        for yy in [y-1.35,y+1.35]:
            body('DENS_DustRecovery_Foot_%.2f_%.2f'%(xx,yy),(xx,yy,.08),(.32,.32,.16),c,zinc)
            body('DENS_DustRecovery_Leg_%.2f_%.2f'%(xx,yy),(xx,yy,1.60),(.12,.12,2.8),c,steel)
    for side in [-1,1]:
        body('DENS_DustRecovery_FrameRail_'+str(side),(x+side*1.15,y,2.95),(.14,2.82,.14),c,steel)
    for i,yy in enumerate([y-1.35,y-.20,y+.20,y+1.35]):
        body('DENS_DustRecovery_SaddleBeam_'+str(i),(x,yy,2.95),(2.30,.14,.14),c,steel)
    for side,yy in enumerate([y-.78,y+.78]):
        tag='DENS_DustRecovery_%s_'%side
        # Sealed removable bin below a tapered cyclone and accessible slide gate.
        cylinder(tag+'Bin',(x,yy,.24),(x,yy,1.0),.48,c,teal,24)
        cylinder(tag+'Lid',(x,yy,1.0),(x,yy,1.07),.53,c,steel,24)
        cylinder(tag+'Discharge',(x,yy,1.07),(x,yy,1.65),.16,c,zinc)
        body(tag+'SlideGate',(x,yy,1.30),(.46,.42,.09),c,steel)
        cylinder(tag+'GateHandle',(x-.2,yy,1.3),(x-.62,yy,1.3),.025,c,yellow,8)
        vs=[(x+r*math.cos(i*math.tau/24),yy+r*math.sin(i*math.tau/24),z)for z,r in [(1.65,.16),(3.0,.62)]for i in range(24)]
        fs=[tuple(reversed(range(24))),tuple(range(24,48))]+[(i,(i+1)%24,(i+1)%24+24,i+24)for i in range(24)]
        mesh_object(tag+'Cone',vs,fs,c,zinc)
        cylinder(tag+'Body',(x,yy,3.0),(x,yy,4.45),.62,c,zinc,24)
        for z in [3.0,4.40]:cylinder(tag+'Flange_'+str(z),(x,yy,z-.035),(x,yy,z+.035),.67,c,steel,24)
        cylinder(tag+'Outlet',(x,yy,4.45),(x,yy,4.95),.22,c,zinc,24)
        body(tag+'InspectionPlate',(x-.63,yy,3.6),(.06,.40,.48),c,teal)
        for zz in [3.43,3.77]:
            for yo in [-.14,.14]:cylinder(tag+'Bolt_%s_%s'%(zz,yo),(x-.68,yy+yo,zz),(x-.70,yy+yo,zz),.025,c,zinc,6)
        cylinder(tag+'Inlet',(x+.55,yy+.40,4.0),(x+1.03,yy+.40,4.0),.16,c,zinc)
    # Common inlet and capped vacuum connection; no hose across pedestrian access.
    cylinder('DENS_DustRecovery_InletManifold',(x+1.03,y-.38,4.0),(x+1.03,y+1.18,4.0),.16,c,zinc)
    cylinder('DENS_DustRecovery_InletDrop',(x+1.03,y+1.18,1.6),(x+1.03,y+1.18,4.0),.16,c,zinc)
    cylinder('DENS_DustRecovery_VacuumPort',(x+1.03,y+1.18,1.6),(x+1.03,y+1.43,1.6),.16,c,rubber)
    cylinder('DENS_DustRecovery_OutletManifold',(x,y-.78,4.95),(x,y+1.4,4.95),.22,c,zinc,24)
    path=[(x,y+1.4,4.95),(x,y+1.4,6.8),(15.2,y+1.4,6.8),(15.2,16.55,6.8)]
    for i,(a,b) in enumerate(zip(path,path[1:])):
        cylinder('DENS_DustRecovery_FilterBranch_'+str(i),a,b,.22,c,zinc,24)
    # Branch hangers meet the authored roof chord at y=13.75.
    for xx in [9.8,15.2]:
        cylinder('DENS_DustRecovery_Hanger_'+str(xx),(xx,13.75,6.55),(xx,13.75,8.88),.027,c,steel,8)
    body('DENS_DustRecovery_OutletSupport',(9.8,12.975,6.55),(.10,1.75,.10),c,steel)
    body('DENS_DustRecovery_FilterSupport',(15.2,13.75,6.55),(.65,.10,.10),c,steel)
    for o in c.objects:o['density_cell']='DustRecovery';o['purpose']='Twin cyclone vacuum recovery with sealed collection bins and filter branch'
    return {'components':len(c.objects),'footprint':[8.4,9.2,11.2,12.4],'filter_connection':[15.2,16.55,6.8]}


def repair_clean_bench_clearance():
    """Restore clearance between the clean bench, receiver and first MCC cabinet."""
    scene=bpy.context.scene
    if scene.get('density_clean_bench_repaired'):return {'already_present':True}
    moved=[]
    for obj in list(scene.objects):
        if obj.name.startswith('WKS_bench_Clean_'):
            matrix=obj.matrix_world.copy();matrix.translation+=Vector((.6,-.6,0));obj.matrix_world=matrix;moved.append(obj.name)
    assert moved
    scene['density_clean_bench_repaired']=True
    return {'moved':moved,'translation':[.6,-.6,0],'purpose':'Clear MCC end and open receiver-side approach'}


def add_filter_process_headers():
    """Supported pump-to-filter feed and filtrate return outside the crane sweep."""
    c=collection('DENS_FilterHeaders')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    def sweep(tag,points,r,mat):
        pts=[Vector(p)for p in points];rounded=[pts[0]]
        for a,b,d in zip(pts,pts[1:],pts[2:]):
            incoming=(b-a).normalized();outgoing=(d-b).normalized()
            assert abs(incoming.dot(outgoing))<.001
            radius=min(.45,(b-a).length*.45,(d-b).length*.45)
            assert radius>r,'Elbow bend radius must exceed tube radius'
            center=b-incoming*radius+outgoing*radius
            for j in range(9):
                angle=math.pi*j/16;rounded.append(center-outgoing*radius*math.cos(angle)+incoming*radius*math.sin(angle))
        rounded.append(pts[-1]);vs=[];fs=[];previous=None;sides=16
        for i,p in enumerate(rounded):
            tangent=(rounded[min(i+1,len(rounded)-1)]-rounded[max(0,i-1)]).normalized()
            axis=Vector((0,0,1))if abs(tangent.z)<.9 else Vector((1,0,0))
            u=(previous-tangent*previous.dot(tangent)).normalized()if previous is not None else tangent.cross(axis).normalized()
            v=tangent.cross(u).normalized();previous=u
            vs.extend(tuple(p+r*(u*math.cos(j*math.tau/sides)+v*math.sin(j*math.tau/sides)))for j in range(sides))
        for i in range(len(rounded)-1):
            for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
        fs.extend([tuple(reversed(range(sides))),tuple((len(rounded)-1)*sides+j for j in range(sides))])
        o=mesh_object('DENS_FilterHeaders_'+tag,vs,fs,c,mat)
        for face in o.data.polygons[:-2]:face.use_smooth=True
        return o
    feed=[(8.7,4.1,2.4),(8.7,4.1,2.9),(10.7,4.1,2.9),(10.7,4.1,5.9),(12.8,4.1,5.9),(12.8,-20.8,5.9),(10.9,-20.8,5.9),(10.9,-20.8,2.1),(10.9,-19.2,2.1),(11.75,-19.2,2.1)]
    returned=[(11.9,-20.15,1.65),(11.9,-20.65,1.65),(13.6,-20.65,1.65),(13.6,-20.65,5.9),(13.6,7,5.9),(12.2,7,5.9),(12.2,7,5.5)]
    sweep('Feed',feed,.15,teal);sweep('Return',returned,.12,zinc)
    for k,(xx,r)in enumerate([(12.8,.15),(13.6,.12)]):
        for i,yy in enumerate([-18,-14,-10,-6,-2,2]):
            cylinder('DENS_FilterHeaders_Flange_%d_%d'%(k,i),(xx,yy-.035,5.9),(xx,yy+.035,5.9),r+.045,c,steel,16)
            cylinder('DENS_FilterHeaders_Band_%d_%d'%(k,i),(xx,yy+.09,5.9),(xx,yy+.16,5.9),r+.005,c,yellow,16)
    for i,yy in enumerate([-19.25,-13.75,-8.25,-2.75,2.75]):
        body('DENS_FilterHeaders_Cradle_'+str(i),(13.2,yy,5.67),(1.6,.12,.12),c,steel)
        for j,xx in enumerate([12.4,14.0]):
            cylinder('DENS_FilterHeaders_Hanger_%d_%d'%(i,j),(xx,yy,5.67),(xx,yy,8.88),.025,c,steel,8)
            body('DENS_FilterHeaders_Anchor_%d_%d'%(i,j),(xx,yy,8.86),(.20,.24,.04),c,steel)
        for j,(xx,r)in enumerate([(12.8,.15),(13.6,.12)]):
            body('DENS_FilterHeaders_Saddle_%d_%d'%(i,j),(xx,yy,5.9-r-.05),(.23,.16,.10),c,zinc)
    for name,xx,yy in [('Feed',10.9,-20.8),('Return',13.6,-20.65)]:
        cylinder('DENS_FilterHeaders_Valve_'+name,(xx,yy,2.45),(xx,yy,2.75),.22,c,steel)
        cylinder('DENS_FilterHeaders_Stem_'+name,(xx,yy,2.60),(xx,yy+.35,2.60),.035,c,zinc,8)
        cylinder('DENS_FilterHeaders_Handle_'+name,(xx,yy+.35,2.60),(xx,yy+.40,2.60),.16,c,yellow,16)
    for o in c.objects:o['density_cell']='FilterHeaders';o['purpose']='Supported filter feed and filtrate return with accessible isolation valves'
    return {'components':len(c.objects),'feed_path':feed,'return_path':returned,'roof_anchor_z':8.88}


def add_trunk_service_catwalk():
    """Guarded mid-run C8 access, with a dogleg around C5 suspension rods."""
    c=collection('DENS_TrunkCatwalk')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    deck=6.4
    segments=[(-12.2,-6.5,-13.0),(-5.5,4.8,-13.0),(4.8,6.8,-13.3),(6.8,11.8,-13.0)]
    for i,(a,b,x)in enumerate(segments):
        body('DENS_Catwalk_Deck_%d'%i,(x,(a+b)/2,deck-.04),(1.1,b-a,.08),c,zinc,chamfer=0)
        for side in [-1,1]:
            body('DENS_Catwalk_Stringer_%d_%d'%(i,side),(x+side*.48,(a+b)/2,6.23),(.10,b-a,.18),c,steel,chamfer=0)
        # Subtle tread strips provide scale without an alpha-overdraw grating.
        for j in range(math.ceil((b-a)/.45)):
            yy=a+.18+j*.45
            if yy<b-.06:body('DENS_Catwalk_Tread_%d_%d'%(i,j),(x,yy,6.403),(.88,.035,.006),c,steel,chamfer=0)
    outer=[(-13.55,-12.2),(-13.55,4.8),(-13.85,4.8),(-13.85,6.8),(-13.55,6.8),(-13.55,11.8)]
    inner=[(-12.45,-12.2),(-12.45,4.8),(-12.75,4.8),(-12.75,6.8),(-12.45,6.8),(-12.45,11.8)]
    for side,path in enumerate([outer,inner]):
        for i,(a,b)in enumerate(zip(path,path[1:])):
            for level,z in enumerate([6.95,7.5]):cylinder('DENS_Catwalk_Rail_%d_%d_%d'%(side,i,level),(*a,z),(*b,z),.025,c,yellow,8)
            va,vb=Vector((*a,0)),Vector((*b,0));length=(vb-va).length;count=max(1,math.ceil(length/1.8))
            for j in range(count+1):
                pt=va.lerp(vb,j/count)
                cylinder('DENS_Catwalk_Post_%d_%d_%d'%(side,i,j),(pt.x,pt.y,6.35),(pt.x,pt.y,7.5),.027,c,steel,8)
            mid=(va+vb)/2
            o=body('DENS_Catwalk_Toeboard_%d_%d'%(side,i),(mid.x,mid.y,6.48),(.035,length,.16),c,yellow,chamfer=0)
            o.rotation_euler.z=math.atan2(-(vb-va).x,(vb-va).y)
    for i,y in enumerate([-12.2,11.8,-6.5,-5.5]):
        for j,z in enumerate([6.95,7.5]):cylinder('DENS_Catwalk_EndGuard_%d_%d'%(i,j),(-13.55,y,z),(-12.45,y,z),.025,c,yellow,8)
    # Hatch gate has visible hinge and spring housing; opens onto the deck.
    cylinder('DENS_Catwalk_GateSpring',(-13.5,-5.5,7.10),(-13.5,-5.5,7.40),.055,c,steel)
    for i,y in enumerate([-10,-8.25,-6,-2.75,2.75,7,8.25,11.4]):
        body('DENS_Catwalk_CrossBearer_%d'%i,(-12.79,y,6.23),(1.62,.14,.20),c,steel,chamfer=0)
    for i,y in enumerate([-8.25,-2.75,2.75,8.25]):
        cylinder('DENS_Catwalk_RoofHanger_%d'%i,(-13.57,y,6.23),(-13.57,y,8.88),.03,c,steel,8)
        body('DENS_Catwalk_Anchor_%d'%i,(-13.57,y,8.86),(.24,.3,.04),c,steel)
    # Caged top-out ladder stays inside the guarded deck opening.
    for i,x in enumerate([-13.3,-12.7]):
        body('DENS_Catwalk_LadderStile_%d'%i,(x,-6.3,3.8),(.06,.08,7.6),c,zinc,chamfer=0)
        body('DENS_Catwalk_LadderFoot_%d'%i,(x,-6.3,.035),(.20,.25,.07),c,steel)
    for i in range(23):
        z=.18+i*.28
        cylinder('DENS_Catwalk_Rung_%02d'%i,(-13.3,-6.3,z),(-12.7,-6.3,z),.022,c,zinc,8)
    for k,z in enumerate([2.4,3.3,4.2,5.1,6.0,7.1]):
        for j in range(24):
            # Upper hoop leaves an opening toward the top-out gate.
            if k==5 and 3<=j<9:continue
            a=j*math.tau/24;b=(j+1)*math.tau/24
            cylinder('DENS_Catwalk_Cage_%d_%02d'%(k,j),(-13+.42*math.cos(a),-6.05+.42*math.sin(a),z),(-13+.42*math.cos(b),-6.05+.42*math.sin(b),z),.018,c,steel,6)
    for i,deg in enumerate([0,45,135,180,225,270,315]):
        a=math.radians(deg);x=-13+.42*math.cos(a);y=-6.05+.42*math.sin(a)
        cylinder('DENS_Catwalk_CageUpright_%d'%i,(x,y,2.4),(x,y,7.1),.018,c,steel,6)
    for o in c.objects:o['density_cell']='TrunkCatwalk';o['purpose']='Guarded conveyor inspection walkway with caged access and structural supports'
    return {'components':len(c.objects),'run_length_m':24,'deck_z':deck,'hatch_y':[-6.5,-5.5],'dogleg_y':[4.8,6.8]}


def add_motor_test_instruments():
    """Rear-mounted instruments and tool storage for the existing motor test bench."""
    c=collection('DENS_TestInstrumentation')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    blue=material('DENS_InstrumentBlue',(.025,.12,.18),.35,.5)
    white=material('DENS_GaugeWhite',(.72,.75,.70),.1,.58)
    black=material('DENS_Rubber',(.015,.021,.022),0,.8)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    x=-10.08;cy=-5.2
    body('DENS_TestPanel_Back',(x,cy,2.53),(.10,1.9,2.0),c,blue)
    for i,y in enumerate([cy-.4,cy+.4]):
        body('DENS_TestPanel_Post_%d'%i,(x-.035,y,1.77),(.10,.10,3.54),c,steel)
        body('DENS_TestPanel_Foot_%d'%i,(x-.035,y,.035),(.26,.24,.07),c,steel)
        body('DENS_TestPanel_BenchBracket_%d'%i,(x+.22,y,1.28),(.52,.12,.10),c,zinc)
    body('DENS_TestPanel_TopFrame',(x,cy,3.51),(.14,2.02,.10),c,steel)
    body('DENS_TestPanel_LightHousing',(x+.15,cy,3.45),(.30,1.65,.09),c,steel)
    body('DENS_TestPanel_LightLens',(x+.17,cy,3.40),(.24,1.48,.025),c,white)
    # Analogue panel meters, seated flush on the front rather than floating.
    for i,y in enumerate([cy-.55,cy,cy+.55]):
        body('DENS_TestPanel_Meter_%d'%i,(x+.12,y,3.0),(.18,.43,.40),c,steel)
        cylinder('DENS_TestPanel_Dial_%d'%i,(x+.215,y,3.0),(x+.23,y,3.0),.145,c,white,16)
        cylinder('DENS_TestPanel_Needle_%d'%i,(x+.235,y,3.0),(x+.235,y+.08,3.08),.008,c,black,6)
        for j in range(5):
            a=math.radians(35+j*27.5)
            cylinder('DENS_TestPanel_Tick_%d_%d'%(i,j),(x+.235,y+.115*math.cos(a),3.0+.115*math.sin(a)),(x+.235,y+.135*math.cos(a),3.0+.135*math.sin(a)),.005,c,black,6)
    body('DENS_TestPanel_TerminalRail',(x+.1,cy,2.47),(.13,1.65,.10),c,zinc)
    for i in range(10):
        y=cy-.67+i*.15
        body('DENS_TestPanel_Terminal_%02d'%i,(x+.19,y,2.47),(.13,.095,.18),c,black)
        cylinder('DENS_TestPanel_TerminalCap_%02d'%i,(x+.26,y,2.47),(x+.275,y,2.47),.022,c,zinc,8)
    body('DENS_TestPanel_LowerShelf',(x+.25,cy,1.65),(.60,1.8,.06),c,zinc)
    for i,y in enumerate([cy-.60,cy,cy+.60]):
        body('DENS_TestPanel_BinBase_%d'%i,(x+.26,y,1.72),(.42,.48,.06),c,blue)
        for j,yy in enumerate([y-.23,y+.23]):body('DENS_TestPanel_BinSide_%d_%d'%(i,j),(x+.26,yy,1.83),(.42,.03,.24),c,blue)
        body('DENS_TestPanel_BinFront_%d'%i,(x+.46,y,1.79),(.03,.48,.16),c,blue)
        body('DENS_TestPanel_BinBack_%d'%i,(x+.06,y,1.83),(.03,.48,.24),c,blue)
        body('DENS_TestPanel_BinLabel_%d'%i,(x+.48,y,1.80),(.005,.25,.07),c,white,chamfer=0)
    # Short, retained test leads loop on panel hooks above the parts bins.
    for i,y in enumerate([cy-.5,cy+.45]):
        cylinder('DENS_TestPanel_Hook_%d'%i,(x+.05,y,2.20),(x+.27,y,2.20),.02,c,zinc,8)
        for j in range(16):
            a=j*math.tau/16;b=(j+1)*math.tau/16
            cylinder('DENS_TestPanel_Lead_%d_%02d'%(i,j),(x+.22,y+.14*math.cos(a),2.04+.16*math.sin(a)),(x+.22,y+.14*math.cos(b),2.04+.16*math.sin(b)),.012,c,black,6)
    body('DENS_TestPanel_IsolatorBox',(x+.15,cy+.64,2.13),(.20,.27,.28),c,yellow)
    cylinder('DENS_TestPanel_IsolatorHandle',(x+.26,cy+.64,2.13),(x+.31,cy+.64,2.13),.07,c,steel,8)
    for o in c.objects:o['density_cell']='TestInstrumentation';o['purpose']='Bench-mounted motor-test instruments, lead hooks and parts bins'
    return {'components':len(c.objects),'support':'rear bench edge and floor-mounted uprights'}


def add_east_product_conveyors():
    """East elevated trunk and rising side-wall discharge; transfer/feed pass follows."""
    global BELTS
    c=collection('DENS_EastProductStructure')
    if len(c.objects):return {'already_present':True}
    routes=[('C11','East product trunk',(11.3,-22.3,7.8),(11.3,12.0,7.8),1.2),('C12','Rising east stockpile discharge',(11.3,12.0,7.4),(30,12.0,10.2),1.2)]
    prior=BELTS
    try:
        BELTS=routes;detail_conveyors()
    finally:BELTS=prior
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    for side in [-1,1]:
        xx=11.3+side*.78
        for i,z in enumerate([6.9,7.45]):body('DENS_EastTrunkChord_%d_%d'%(side,i),(xx,-5.45,z),(.14,33.7,.14),c,yellow)
        for i in range(24):
            a=-22.3+i*33.7/24;b=-22.3+(i+1)*33.7/24
            cylinder('DENS_EastTrunkDiagonal_%d_%02d'%(side,i),(xx,a,6.9 if i%2==0 else 7.45),(xx,b,7.45 if i%2==0 else 6.9),.035,c,steel,8)
        for i,y in enumerate([-19.25,-13.75,-8.25,-2.75,2.75,8.25]):
            cylinder('DENS_EastTrunkHanger_%d_%d'%(side,i),(11.3+side*.95,y,6.86),(11.3+side*.95,y+.3,8.88),.035,c,steel,8)
            body('DENS_EastTrunkAnchor_%d_%d'%(side,i),(11.3+side*.95,y+.3,8.86),(.22,.26,.04),c,steel)
    for i,y in enumerate([-19.25,-13.75,-8.25,-2.75,2.75,8.25]):body('DENS_EastTrunkBearer_%d'%i,(11.3,y,6.86),(2.1,.16,.14),c,steel)
    # Outdoor trestles carry the rising discharge; no new legs in workshop aisles.
    for i,x in enumerate([20.8,24.2,27.5]):
        z=7.4+(x-11.3)*2.8/18.7-.55
        for side in [-1,1]:
            y=12+side*.78
            body('DENS_EastDischargePier_%d_%d'%(i,side),(x,y,z/2),(.20,.20,z),c,steel)
            body('DENS_EastDischargeFoot_%d_%d'%(i,side),(x,y,.10),(.60,.60,.20),c,steel)
            body('DENS_EastDischargeSaddle_%d_%d'%(i,side),(x,12+side*.70,z+.14),(.18,.13,.28),c,steel)
        cylinder('DENS_EastDischargeBrace_%d'%i,(x,11.22,.3),(x,12.78,z-.2),.055,c,steel,8)
        body('DENS_EastDischargeBearer_%d'%i,(x,12,z),( .22,1.8,.18),c,steel)
    # Keep one named editable opening for the weatherproof conveyor penetration.
    cutter=body('DENS_EastDischargeWallCut',(20.2,12,8.75),(1.4,2.05,1.1),c,steel,chamfer=0)
    cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE'
    for name in ['ENV_wall_right_clad','ENV_window_frames','ENV_window_mullions','ENV_window_glass_day']:
        o=bpy.data.objects[name];mod=o.modifiers.new('EastProductConveyorOpening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='MANIFOLD';mod.object=cutter
    for side in [-1,1]:
        body('DENS_EastDischargeJamb_%d'%side,(20.23,12+side*1.08,8.75),(.16,.11,1.25),c,steel)
        body('DENS_EastDischargeLintel_%d'%side,(20.23,12,8.75+side*.61),(.16,2.27,.12),c,steel)
    for o in c.objects:o['density_cell']='EastProductConveyors';o['purpose']='Supported east product route through framed wall penetration'
    return {'components':len(c.objects),'routes':routes,'pending':['feed elevator','corner transfer','outdoor stockpile','coal animation','support and opening audit']}


def connect_east_product_feed():
    """Outdoor enclosed bucket lift, coal receiving hopper and discharge loading chute."""
    global BELTS
    c=collection('DENS_EastProductFeed')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    coal=material('DENS_Coal',(.018,.022,.025),.05,.85)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    prior=BELTS
    try:
        BELTS=[('C13','Receiving hopper into enclosed elevator',(11.3,-25.8,.75),(11.3,-23.2,.75),.8)];detail_conveyors()
    finally:BELTS=prior
    # Enclosed elevator has a broad foundation, inspection hatches and top drive.
    body('DENS_EastLift_Casing',(11.3,-23.2,4.1),(1.2,1.3,8.0),c,teal)
    body('DENS_EastLift_Base',(11.3,-23.25,.10),(1.6,1.6,.20),c,steel)
    body('DENS_EastLift_Head',(11.3,-23.2,8.2),(1.45,1.5,.45),c,yellow)
    cylinder('DENS_EastLift_Motor',(12.03,-23.2,8.2),(12.6,-23.2,8.2),.22,c,teal)
    for i in range(7):
        z=.7+i*1.05
        body('DENS_EastLift_Hatch_%d'%i,(11.92,-23.2,z),(.06,.7,.65),c,steel)
        body('DENS_EastLift_Handle_%d'%i,(11.97,-23.2,z),(.05,.25,.04),c,zinc)
    # Thin-walled rectangular chutes remain visibly open at both ends.
    def chute(key,a,b,width,depth):
        a,b=Vector(a),Vector(b);d=(b-a).normalized();side=d.cross(Vector((1,0,0)))
        if side.length<.1:side=d.cross(Vector((0,1,0)))
        side.normalize();up=d.cross(side).normalized();basis=Matrix((side,up,d)).transposed()
        for i,offset,size in [(0,side*width/2,(.05,depth,(b-a).length)),(1,-side*width/2,(.05,depth,(b-a).length)),(2,up*depth/2,(width,.05,(b-a).length)),(3,-up*depth/2,(width,.05,(b-a).length))]:
            o=body('DENS_EastChute_'+key+'_%d'%i,(a+b)/2+offset,size,c,steel,chamfer=0);o.rotation_euler=basis.to_euler()
    chute('LiftOutlet',(11.3,-22.65,8.02),(11.3,-22.0,7.85),.9,.5)
    chute('CornerTransfer',(11.3,12.0,7.90),(11.7,12.0,7.53),.95,.65)
    chute('StockpileLoading',(30,12,10.23),(32.2,12,3.85),.7,.7)
    # Hopper tapers onto the short receiving belt; grizzly bars and retained coal.
    top=[(10.3,-26.8,2.2),(12.3,-26.8,2.2),(12.3,-24.8,2.2),(10.3,-24.8,2.2)]
    bottom=[(10.94,-26.16,.82),(11.66,-26.16,.82),(11.66,-25.44,.82),(10.94,-25.44,.82)]
    mesh_object('DENS_EastReceivingHopper',top+bottom,[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)],c,steel)
    for i in range(7):body('DENS_EastReceivingGrizzly_%d'%i,(10.4+i*.3,-25.8,2.22),(.06,2,.09),c,yellow)
    for i,x in enumerate([10.38,12.22]):
        for j,y in enumerate([-26.72,-24.88]):body('DENS_EastReceivingLeg_%d_%d'%(i,j),(x,y,1.07),(.12,.12,2.14),c,steel)
    # A dedicated front-wall penetration, framed around all carried/return geometry.
    cut=body('DENS_EastFeedWallCut',(11.3,-22.18,7.65),(2.15,1.4,1.75),c,steel,chamfer=0)
    cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE'
    for name in ['ENV_wall_far_clad','ENV_window_frames','ENV_window_mullions','ENV_window_glass_day','ENV_window_sills','TUN_POLISH_split_wall_trim.007']:
        o=bpy.data.objects[name];m=o.modifiers.new('EastFeedOpening','BOOLEAN');m.operation='DIFFERENCE';m.solver='MANIFOLD';m.object=cut
    for side in [-1,1]:
        body('DENS_EastFeedJamb_%d'%side,(11.3+side*1.13,-22.22,7.65),(.11,.16,1.9),c,steel)
        body('DENS_EastFeedLintel_%d'%side,(11.3,-22.22,7.65+side*.93),(2.37,.16,.11),c,steel)
    # Fresh coal heap is set beyond the final trestle, not around its feet.
    rings=32;verts=[(32.2,12,3.4)]
    for radius,z in [(1,2.9),(2.5,1.7),(4.2,.02)]:
        for i in range(rings):
            a=i*math.tau/rings;r=radius*(1+.035*math.sin(i*2.3));verts.append((32.2+r*math.cos(a),12+r*math.sin(a),z+(.12*math.sin(i*1.7) if z>.1 else 0)))
    faces=[(0,1+i,1+(i+1)%rings)for i in range(rings)]
    for k in range(2):
        a=1+k*rings;b=a+rings
        faces +=[(a+i,b+i,b+(i+1)%rings,a+(i+1)%rings)for i in range(rings)]
    pile=mesh_object('DENS_EastCoalStockpile',verts,faces,c,bpy.data.materials['YARD_Coal'])
    uv=pile.data.uv_layers.new(name='UVMap')
    for loop in pile.data.loops:
        v=pile.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x/2,v.y/2)
    for polygon in pile.data.polygons:polygon.use_smooth=True
    from mathutils.bvhtree import BVHTree
    surface=BVHTree.FromPolygons([Vector(v)for v in verts],faces)
    import random
    rng=random.Random(2718)
    chip=bpy.data.meshes['DENS_shared_coal'].copy();chip.name='DENS_EastPileChip';chip.materials.clear();chip.materials.append(material('DENS_PileCoalDark',(.004,.006,.008),.05,.9))
    for i in range(150):
        r=4*math.sqrt(rng.random());angle=rng.random()*math.tau
        hit=surface.ray_cast(Vector((32.2+r*math.cos(angle),12+r*math.sin(angle),6)),Vector((0,0,-1)),7)[0]
        if hit is None:continue
        rock=bpy.data.objects.new('DENS_EastPileCoal_%03d'%i,chip);c.objects.link(rock);rock['density_managed']=True;rock.location=hit-Vector((0,0,.035))
        rock.rotation_euler=(rng.uniform(-.6,.6),rng.uniform(-.6,.6),angle);rock.scale=(rng.uniform(.4,1.3),rng.uniform(.4,1.3),rng.uniform(.3,.8))
    concrete=bpy.data.objects['ENV_floor_slab'].data.materials[0]
    for key,center,size in [('Receiving',(11.3,-25.6,-.06),(3.6,6.4,.20)),('Stockpile',(30.2,12,-.06),(19.5,16.0,.20))]:
        pad=body('DENS_EastApron_'+key,center,size,c,concrete,chamfer=0)
        uv=pad.data.uv_layers.new(name='UVMap')
        for loop in pad.data.loops:
            v=pad.matrix_world@pad.data.vertices[loop.vertex_index].co
            uv.data[loop.index].uv=(v.x/4,v.y/4)
    for o in c.objects:o['density_cell']='EastProductFeed';o['purpose']='Connected receiving, enclosed lift, transfer and coal stockpile discharge'
    return {'components':len(c.objects),'pending':['connection and opening audit','animated coal','seated and exterior visual audit']}


def animate_east_product_coal():
    c=collection('DENS_EastProductCoal')
    if len(c.objects):return {'already_present':True}
    routes=[('C11',(11.3,-22.3,7.8),(11.3,12,7.8),1.2,900),('C12',(11.3,12,7.4),(30,12,10.2),1.2,480),('C13',(11.3,-25.8,.75),(11.3,-23.2,.75),.8,240)]
    mesh=bpy.data.meshes['DENS_shared_coal']
    for key,start,end,width,period in routes:
        a,b=Vector(start),Vector(end);d=(b-a).normalized();side=Vector((0,0,1)).cross(d).normalized();up=d.cross(side).normalized()
        for i in range(10):
            o=bpy.data.objects.new('DENS_ORE_'+key+'_%02d'%i,mesh);c.objects.link(o);o['density_managed']=True
            for frame in range(1,period+2,3):
                t=((frame-1)/period+i/10)%1;scale=max(.001,min(1,(t-.025)/.05,(.975-t)/.05))
                o.location=a.lerp(b,t)+side*((i%3)-1)*width*.2+up*.045;o.scale=(scale,)*3
                o.keyframe_insert('location',frame=frame);o.keyframe_insert('scale',frame=frame)
            o.animation_data.action.name='DENS_StaggeredLoop_'+o.name
            for layer in o.animation_data.action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            for index,kp in enumerate(fc.keyframe_points):
                                kp.interpolation='LINEAR'
                                if fc.data_path=='location' and index+1<len(fc.keyframe_points):
                                    next_frame=fc.keyframe_points[index+1].co.x
                                    wrap=1+period*(1-i/10)
                                    if abs(next_frame-wrap)<.01:kp.interpolation='CONSTANT'
                            fc.modifiers.new('CYCLES')
    bpy.context.scene.frame_set(1)
    return {'coal_objects':len(c.objects),'period_frames':{r[0]:r[4]for r in routes}}


def add_east_inspection_walkway():
    """Suspended conveyor inspection deck with stairs from the existing east gallery."""
    c=collection('DENS_EastInspection')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    body('DENS_EastWalk_Deck',(13,-3.25,6.46),(1.1,27.5,.08),c,zinc,chamfer=0)
    for side in [-1,1]:
        body('DENS_EastWalk_Stringer_%d'%side,(13+side*.48,-3.25,6.3),(.1,27.5,.18),c,steel,chamfer=0)
    # Long outside rail opens only at the stair landing.
    for side,ranges in [(-1,[(-17,10.5)]),(1,[(-17,6.7),(7.9,10.5)])]:
        x=13+side*.55
        for k,(a,b)in enumerate(ranges):
            for j,z in enumerate([7.05,7.6]):cylinder('DENS_EastWalk_Rail_%d_%d_%d'%(side,k,j),(x,a,z),(x,b,z),.025,c,yellow,8)
            body('DENS_EastWalk_Toeboard_%d_%d'%(side,k),(x,(a+b)/2,6.58),(.035,b-a,.16),c,yellow,chamfer=0)
            count=math.ceil((b-a)/1.8)
            for j in range(count+1):
                y=a+(b-a)*j/count;cylinder('DENS_EastWalk_Post_%d_%d_%d'%(side,k,j),(x,y,6.45),(x,y,7.6),.027,c,steel,8)
    for i,y in enumerate([-17,10.5]):
        for j,z in enumerate([7.05,7.6]):cylinder('DENS_EastWalk_EndRail_%d_%d'%(i,j),(12.45,y,z),(13.55,y,z),.025,c,yellow,8)
    for i in range(61):body('DENS_EastWalk_Tread_%02d'%i,(13,-16.8+i*.45,6.503),(.88,.035,.006),c,steel,chamfer=0)
    for i,y in enumerate([-13.75,-8.25,-2.75,2.75,8.25]):
        body('DENS_EastWalk_Bearer_%d'%i,(13,y-.35,6.25),(1.4,.14,.14),c,steel)
        for side in [-1,1]:
            x=13+side*.62
            cylinder('DENS_EastWalk_Hanger_%d_%d'%(i,side),(x,y-.35,6.25),(x,y-.3,8.88),.03,c,steel,8)
            body('DENS_EastWalk_Anchor_%d_%d'%(i,side),(x,y-.3,8.86),(.22,.26,.04),c,steel)
    a=Vector((16.4,3.0,4.12));b=Vector((14.2,7.3,6.5));d=(b-a).normalized();side=Vector((0,0,1)).cross(d).normalized();up=d.cross(side).normalized();basis=Matrix((side,up,d)).transposed()
    # Landing terminates on the stair's upper riser plane instead of covering treads.
    left=b+side*.52;right=b-side*.52
    outline=[(12.45,6.7),(13.55,6.7),(left.x,left.y),(right.x,right.y),(14.8,7.9),(12.45,7.9)]
    vertices=[(x,y,z) for z in [6.42,6.5] for x,y in outline];n=len(outline)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh_object('DENS_EastWalk_Landing',vertices,faces,c,zinc)
    body('DENS_EastWalk_LandingBeam',(13.6,7.8,6.3),(2.3,.12,.18),c,steel)
    for k,(start,end) in enumerate([((13.55,7.9),(14.8,7.9)),((14.8,7.9),(right.x,right.y)),((13.55,6.7),(left.x,left.y))]):
        for j,z in enumerate([7.05,7.6]):cylinder('DENS_EastWalk_LandingRail_%d_%d'%(k,j),(*start,z),(*end,z),.025,c,yellow,8)
        for j,pt in enumerate([start,end]):cylinder('DENS_EastWalk_LandingPost_%d_%d'%(k,j),(*pt,6.46),(*pt,7.6),.027,c,steel,8)
    for sign in [-1,1]:
        o=body('DENS_EastWalk_StairStringer_%d'%sign,(a+b)/2+side*sign*.47-Vector((0,0,.12)),(.12,.18,(b-a).length),c,steel,chamfer=0);o.rotation_euler=basis.to_euler()
        for j,z in enumerate([.55,1.05]):cylinder('DENS_EastWalk_StairRail_%d_%d'%(sign,j),a+side*sign*.52+Vector((0,0,z)),b+side*sign*.52+Vector((0,0,z)),.025,c,yellow,8)
        for j,t in enumerate([0,.33,.66,1]):
            pt=a.lerp(b,t)+side*sign*.52;cylinder('DENS_EastWalk_StairPost_%d_%d'%(sign,j),pt,pt+Vector((0,0,1.05)),.027,c,steel,8)
    run=Vector((b.x-a.x,b.y-a.y,0)).length
    for i in range(15):
        pt=a.lerp(b,(i+.5)/15);pt.z=a.z+(b.z-a.z)*(i+1)/15-.03
        o=body('DENS_EastWalk_StairTread_%02d'%i,pt,(1,run/15,.06),c,zinc,chamfer=0);o.rotation_euler.z=math.atan2(side.y,side.x)
    cut=body('DENS_EastWalk_GalleryRailCut',(16.02,4.1,4.7),(1.4,3.0,2.0),c,steel,chamfer=0);cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE'
    for o in list(bpy.context.scene.objects):
        if o.name.startswith(('FIT_GalleryRail_16p02_','FIT_GalleryPost_16p02_')) or o.name=='FIT_GalleryToe_16p02':
            m=o.modifiers.new('EastInspectionStairAccess','BOOLEAN');m.operation='DIFFERENCE';m.solver='MANIFOLD';m.object=cut
    for i,y in enumerate([2.6,5.6]):cylinder('DENS_EastWalk_GalleryEntryPost_%d'%i,(16.02,y,4.12),(16.02,y,5.22),.03,c,steel,8)
    # Relocate the existing under-gallery luminaire clear of the new stair stringer.
    for name in ['FIT_TaskHousing_16p6_3','FIT_TaskLens_16p6_3']:
        lamp=bpy.data.objects.get(name)
        if lamp:lamp.location.y=2.2
    for o in c.objects:o['density_cell']='EastInspection';o['purpose']='Guarded east conveyor inspection deck connected to existing gallery'
    return {'components':len(c.objects),'walkway_length_m':27.5,'deck_z':6.5,'stair_risers':15,'stair_rise_m':(b.z-a.z)/15,'pending':['collision audit','headroom and entry audit','visual review']}


def add_bench_rebuild_stations():
    """Bench-supported pump/roller rebuild fixtures within existing worktop footprints."""
    c=collection('DENS_BenchRebuild')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    plans=[('East','EXP_Bench_Top_1',(18.6,1.75)),('Mid','EXP_Bench_Top_4',(18.6,3.25)),('InspectionTray','FIT_Rear_DeskWorktop',(-5.7,6.375))]
    reports=[]
    for key,name,xy in plans:
        top=bpy.data.objects[name];bounds=[top.matrix_world@Vector(v) for v in top.bound_box]
        low=Vector([min(v[i]for v in bounds)for i in range(3)]);high=Vector([max(v[i]for v in bounds)for i in range(3)])
        # u follows the long bench edge; v remains within its depth.
        along_y=False;u=Vector((1,0,0));v=Vector((0,1,0))
        center=Vector((*xy,high.z));length=1.0;depth=.64
        def point(x,y,z):return center+u*x+v*y+Vector((0,0,z))
        def box(tag,x,y,z,size,mat):
            o=body('DENS_Rebuild_'+key+'_'+tag,point(x,y,z),size,c,mat,chamfer=.008);o.rotation_euler.z=math.atan2(u.y,u.x);return o
        def rod(tag,a,b,r,mat):return cylinder('DENS_Rebuild_'+key+'_'+tag,point(*a),point(*b),r,c,mat,12)
        # Retained pump rotor on twin bolted bearing blocks; neither shaft nor casing floats.
        x=0
        if key!='InspectionTray':
            box('FixturePlate',x,0,.025,(.94,depth*.72,.05),steel)
            for i,dx in enumerate([-.31,.31]):
                box('BearingFoot_%d'%i,x+dx,0,.09,(.18,.36,.08),teal)
                box('BearingBlock_%d'%i,x+dx,0,.19,(.14,.28,.18),teal)
                for j,dy in enumerate([-.13,.13]):rod('FootBolt_%d_%d'%(i,j),(x+dx,dy,.125),(x+dx,dy,.145),.025,zinc)
            rod('RotorShaft',(x-.44,0,.25),(x+.44,0,.25),.045,zinc)
            rod('RotorCore',(x-.22,0,.25),(x+.22,0,.25),.145,teal)
            for i in range(8):
                angle=i*math.tau/8
                o=box('RotorRib_%d'%i,x,.15*math.sin(angle),.25+.15*math.cos(angle),(.42,.022,.04),zinc)
                # Rotate radial ribs around the actual shaft axis.
                o.rotation_euler=(__import__('mathutils').Quaternion(u,angle)@o.rotation_euler.to_quaternion()).to_euler()
        # Small open parts tray with bearing races and bolts, clear of the rotor fixture.
        if key=='InspectionTray':
            tx=0;tw=.62;td=.48
            box('TrayBase',tx,0,.015,(tw,td,.03),zinc)
            for j,dy in enumerate([-td/2,td/2]):box('TrayLongEdge_%d'%j,tx,dy,.06,(tw,.025,.09),steel)
            for j,dx in enumerate([-tw/2,tw/2]):box('TrayEnd_%d'%j,tx+dx,0,.06,(.025,td,.09),steel)
            for i in range(2):
                cx=tx+(i-.5)*tw*.46;verts=[];faces=[];segments=16
                for z,r in [(.03,.075),(.03,.045),(.075,.075),(.075,.045)]:
                    verts.extend(tuple(point(cx+r*math.cos(j*math.tau/segments),r*math.sin(j*math.tau/segments),z)) for j in range(segments))
                for j in range(segments):
                    k=(j+1)%segments
                    faces.extend([(j,k,32+k,32+j),(16+j,48+j,48+k,16+k),(32+j,32+k,48+k,48+j),(j,16+j,16+k,k)])
                mesh_object('DENS_Rebuild_'+key+'_BearingRace_%d'%i,verts,faces,c,zinc)
            for i in range(5):rod('TrayBolt_%d'%i,(tx-.20+i*.09,-td*.3,.05),(tx-.20+i*.09,-td*.3,.09),.018,steel)
        reports.append({'bench':name,'top_z':high.z,'purpose':('Bearing inspection tray' if key=='InspectionTray' else 'Supported rotor rebuild fixture'),'long_axis':'Y'if along_y else'X'})
    for o in c.objects:o['density_cell']='BenchRebuild';o['purpose']='Bench-supported maintenance fixtures and organised disassembled parts'
    return {'components':len(c.objects),'stations':reports,'pending':['existing equipment collision audit','visual review']}


def add_spare_belting_reel():
    """Static spare belting on a retained spindle stand, clear of the floor drain."""
    c=collection('DENS_BeltingStore')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    rubber=material('DENS_BeltRubber',(.022,.027,.030),.02,.87)
    edge=material('DENS_BeltFabricEdge',(.029,.033,.034),.02,.93)
    x,y,z=-4.1,-4.4,1.38
    # Two A-frame spindle supports; cross ties stay raised so the slab can be cleaned.
    for side in [-1,1]:
        xx=x+side*.59
        for j,yy in enumerate([y-1.15,y+1.15]):
            body('DENS_Belting_Foot_%d_%d'%(side,j),(xx,yy,.06),(.24,.30,.12),c,steel,chamfer=.015)
            a=Vector((xx,yy,.14));b=Vector((xx,y,z));d=b-a
            o=body('DENS_Belting_Brace_%d_%d'%(side,j),(a+b)/2,(.10,.12,d.length),c,yellow,chamfer=0);o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
            cylinder('DENS_Belting_FootBolt_%d_%d'%(side,j),(xx,yy,.12),(xx,yy,.15),.03,c,zinc,8)
        body('DENS_Belting_Bearing_%d'%side,(xx,y,z),(.17,.28,.25),c,steel)
        cylinder('DENS_Belting_Collar_%d'%side,(xx-side*.13,y,z),(xx-side*.08,y,z),.14,c,zinc,16)
    for j,yy in enumerate([y-1.15,y+1.15]):body('DENS_Belting_CrossTie_%d'%j,(x,yy,.20),(1.3,.10,.12),c,steel,chamfer=0)
    cylinder('DENS_Belting_Spindle',(x-.73,y,z),(x+.73,y,z),.085,c,zinc,16)
    cylinder('DENS_Belting_Core',(x-.44,y,z),(x+.44,y,z),.19,c,steel,24)
    # Concentric fabric/rubber end layers model the rolled belt, without transparent planes.
    vs=[];faces=[];indices=[];segments=40;rings=13
    for xx in [x-.43,x+.43]:
        for ring in range(rings):
            radius=.19+(1.05-.19)*ring/(rings-1)
            vs.extend((xx,y+radius*math.sin(j*math.tau/segments),z+radius*math.cos(j*math.tau/segments))for j in range(segments))
    offset=rings*segments
    for side in range(2):
        for ring in range(rings-1):
            for j in range(segments):
                a=side*offset+ring*segments+j;b=side*offset+ring*segments+(j+1)%segments
                f=(a,b,b+segments,a+segments);faces.append(tuple(reversed(f))if side==0 else f);indices.append(ring%2)
    for j in range(segments):
        a=(rings-1)*segments+j;b=(rings-1)*segments+(j+1)%segments
        faces.append((a,a+offset,b+offset,b));indices.append(0)
    roll=mesh_object('DENS_Belting_Roll',vs,faces,c,rubber);roll.data.materials.append(edge)
    for face,idx in zip(roll.data.polygons,indices):face.material_index=idx
    for face in list(roll.data.polygons)[-segments:]:face.use_smooth=True
    # Retaining pin and parked winding handle make the stand read as service equipment.
    cylinder('DENS_Belting_LockPin',(x+.69,y-.16,z),(x+.69,y+.16,z),.018,c,yellow,8)
    cylinder('DENS_Belting_CrankArm',(x-.73,y,z),(x-.73,y,z-.30),.025,c,steel,8)
    cylinder('DENS_Belting_CrankGrip',(x-.73,y,z-.30),(x-.59,y,z-.30),.04,c,rubber,12)
    for o in c.objects:o['density_cell']='BeltingStore';o['purpose']='Spare conveyor belting on retained maintenance spindle stand'
    return {'components':len(c.objects),'roll_diameter_m':2.1,'belt_width_m':.86,'center':[x,y,z],'pending':['geometry audit','seated camera review']}


def add_hose_repair_station():
    """Compact hose cutting/crimping bench with reel rack and hydraulic powerpack."""
    c=collection('DENS_HoseRepair')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    def box(tag,p,size,mat=steel):return body('DENS_HoseRepair_'+tag,p,size,c,mat,chamfer=.015)
    def rod(tag,a,b,r,mat=steel,n=12):return cylinder('DENS_HoseRepair_'+tag,a,b,r,c,mat,n)
    for i,x in enumerate([3.65,5.25]):
        for j,y in enumerate([2.85,5.15]):
            box('Foot_%d_%d'%(i,j),(x,y,.06),(.3,.3,.12))
            box('Leg_%d_%d'%(i,j),(x,y,.51),(.12,.12,.9))
    box('LowerShelf',(4.45,4,.25),(1.7,2.45,.08))
    box('Worktop',(4.45,4,1.02),(1.9,2.6,.10),zinc)
    for i,y in enumerate([2.8,5.2]):box('ReelRackPost_%d'%i,(5.3,y,1.67),(.10,.10,1.30))
    box('ReelRackHeader',(5.3,4,2.34),(.12,2.5,.12),teal)
    box('ReelRackTie',(5.3,4,1.53),(.12,2.5,.10))
    for i,y in enumerate([3.15,4,4.85]):
        rod('ReelAxle_%d'%i,(4.92,y,1.95),(5.35,y,1.95),.045,zinc)
        rod('ReelCore_%d'%i,(5.03,y,1.95),(5.24,y,1.95),.13,teal)
        rod('WoundHose_%d'%i,(5.06,y,1.95),(5.21,y,1.95),.28,rubber,24)
        for side,x in enumerate([5.025,5.245]):
            # Open six-spoke flange: avoids solid disc hiding the hose winding.
            for j in range(24):
                a=j*math.tau/24;b=(j+1)*math.tau/24
                rod('ReelRim_%d_%d_%02d'%(i,side,j),(x,y+.32*math.cos(a),1.95+.32*math.sin(a)),(x,y+.32*math.cos(b),1.95+.32*math.sin(b)),.018,teal,6)
            for j in range(6):
                a=j*math.tau/6
                rod('ReelSpoke_%d_%d_%d'%(i,side,j),(x,y,1.95),(x,y+.32*math.cos(a),1.95+.32*math.sin(a)),.018,zinc,6)
        rod('HoseTail_%d'%i,(5.0,y,1.74),(4.84,y,1.30),.026,rubber,8)
        rod('TailCoupling_%d'%i,(4.84,y,1.30),(4.81,y,1.23),.04,zinc,8)
    # Bench crimper: retained radial jaws leave the hose opening visible.
    box('CrimperBase',(4.1,3.25,1.14),(.7,.72,.14),teal)
    box('CrimperHousing',(4.28,3.25,1.40),(.43,.57,.46),teal)
    for i in range(8):
        a=i*math.tau/8;yy=3.25+.145*math.sin(a);zz=1.40+.145*math.cos(a)
        die=box('CrimperDie_%d'%i,(3.99,yy,zz),(.15,.08,.13),zinc);die.rotation_euler.x=-a
    box('CrimperControls',(4.45,3.25,1.72),(.15,.48,.20),steel)
    for i,(y,mat)in enumerate([(3.12,teal),(3.35,yellow)]):rod('CrimperButton_%d'%i,(4.36,y,1.72),(4.33,y,1.72),.035,mat,12)
    # Guarded cutting station, with a visible feed throat and material support.
    box('CutterBase',(4.1,4.65,1.14),(.74,.76,.14),teal)
    box('CutterGuard',(4.32,4.65,1.39),(.30,.55,.40),yellow)
    box('CutterFeedBed',(3.95,4.65,1.24),(.45,.54,.06),zinc)
    for j,y in enumerate([4.47,4.83]):rod('CutterGuide_%d'%j,(3.78,y,1.29),(4.10,y,1.29),.045,zinc)
    rod('CutHose',(3.9,4.25,1.30),(3.9,5.02,1.30),.028,rubber)
    box('Powerpack',(4.85,3.35,.52),(.60,.70,.45),teal)
    rod('PumpMotor',(4.85,3.35,.745),(4.85,3.35,.94),.12,steel)
    for i,x in enumerate([4.78,4.92]):
        points=[(x,3.1,.89),(x,2.62,.89),(x,2.62,1.18),(4.45+i*.06,2.62,1.34),(4.35+i*.06,3.02,1.40)]
        for j,(a,b)in enumerate(zip(points,points[1:])):rod('HydraulicHose_%d_%d'%(i,j),a,b,.022,rubber,8)
    box('FittingsCabinet',(4.65,4.65,.65),(.9,.8,.7),teal)
    for i in range(3):
        box('Drawer_%d'%i,(4.18,4.65,.43+i*.21),(.035,.72,.17),steel)
        rod('DrawerHandle_%d'%i,(4.14,4.42,.43+i*.21),(4.14,4.88,.43+i*.21),.018,zinc,8)
    for o in c.objects:o['density_cell']='HoseRepair';o['purpose']='Reel-fed hose cutting and crimping station with supported powerpack and storage'
    return {'components':len(c.objects),'footprint':[1.9,2.6],'max_height_m':2.40,'pending':['geometry audit','seated visual review','export']}


def add_shaft_repair_lathe():
    """Parked shaft-repair lathe, controls toward the central maintenance aisle."""
    c=collection('DENS_ShaftLathe')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    def box(tag,p,size,mat=teal):return body('DENS_Lathe_'+tag,p,size,c,mat,chamfer=.025)
    def rod(tag,a,b,r,mat=zinc,n=16):return cylinder('DENS_Lathe_'+tag,a,b,r,c,mat,n)
    x=3.95
    for i,y in enumerate([-13.15,-10.45]):
        box('Pedestal_%d'%i,(x,y,.43),(1.1,.78,.78))
        for j,xx in enumerate([3.5,4.4]):
            box('Foot_%d_%d'%(i,j),(xx,y,.06),(.25,.9,.12),steel)
            rod('Anchor_%d_%d'%(i,j),(xx,y,.12),(xx,y,.15),.03,zinc,8)
    box('Bed',(x,-11.8,.88),(1.10,3.85,.22))
    box('ChipTray',(x,-11.6,.78),(1.2,3.1,.06),steel)
    for i,xx in enumerate([3.68,4.20]):box('PrecisionWay_%d'%i,(xx,-11.65,1.025),(.14,3.3,.07),zinc)
    box('Headstock',(x,-13.16,1.27),(1.05,.88,.70))
    box('HeadstockCover',(x,-13.16,1.65),(1.08,.90,.07),steel)
    for i in range(5):box('MotorVent_%d'%i,(4.486,-13.4+i*.11,1.28),(.015,.055,.30),steel)
    rod('ChuckBody',(x,-12.72,1.38),(x,-12.43,1.38),.255,steel,24)
    rod('ChuckFace',(x,-12.43,1.38),(x,-12.40,1.38),.26,zinc,24)
    for i in range(3):
        a=i*math.tau/3
        o=box('ChuckJaw_%d'%i,(x+.145*math.cos(a),-12.37,1.38+.145*math.sin(a)),(.16,.10,.09),zinc);o.rotation_euler.y=-a
    # Solid rear half-guard leaves the stopped workpiece readable from the aisle.
    vs=[];fs=[]
    for y in [-12.77,-12.30]:
        for i in range(13):
            a=-math.pi/2+i*math.pi/12;vs.append((x+.34*math.cos(a),y,1.38+.34*math.sin(a)))
    for i in range(12):fs.append((i,i+1,i+14,i+13))
    guard=mesh_object('DENS_Lathe_ChuckGuard',vs,fs,c,yellow)
    mod=guard.modifiers.new('GuardThickness','SOLIDIFY');mod.thickness=.018
    rod('Workpiece',(x,-12.38,1.38),(x,-10.60,1.38),.075,zinc,24)
    rod('ShaftFlange',(x,-11.1,1.38),(x,-10.98,1.38),.17,zinc,24)
    box('TailstockBase',(x,-10.42,1.07),(.70,.55,.12),steel)
    box('Tailstock',(x,-10.35,1.25),(.50,.48,.32))
    rod('TailQuill',(x,-10.65,1.38),(x,-10.10,1.38),.09,zinc)
    rod('TailWheel',(x,-10.08,1.38),(x,-10.03,1.38),.16,steel)
    box('Carriage',(x,-11.75,1.08),(1.22,.52,.14),steel)
    box('CrossSlide',(3.78,-11.75,1.19),(.70,.40,.09),zinc)
    box('Toolpost',(3.78,-11.75,1.30),(.20,.20,.14),steel)
    box('Tool',(3.89,-11.75,1.365),(.28,.055,.045),zinc)
    box('Apron',(3.39,-11.75,.92),(.15,.60,.45))
    rod('FeedScrew',(3.42,-12.75,.88),(3.42,-10.1,.88),.035,zinc)
    rod('CarriageWheel',(3.30,-11.75,.96),(3.23,-11.75,.96),.145,steel)
    rod('WheelGrip',(3.23,-11.66,.96),(3.17,-11.66,.96),.024,rubber,8)
    box('ControlPanel',(3.40,-13.16,1.38),(.035,.62,.35),steel)
    for i,(y,mat)in enumerate([(-13.36,teal),(-13.15,yellow),(-12.96,rubber)]):rod('Control_%d'%i,(3.37,y,1.40),(3.34,y,1.40),.042,mat,12)
    # Low rear splashback and power cable remain inside the verified bay.
    box('Splashback',(4.49,-11.55,1.25),(.055,2.9,.55),teal)
    rod('PowerCable',(4.35,-13.4,.70),(4.35,-13.4,.17),.022,rubber,8)
    for o in c.objects:o['density_cell']='ShaftLathe';o['purpose']='Parked shaft-repair lathe with supported workpiece, chip tray and aisle-facing controls'
    return {'components':len(c.objects),'bay':[3.15,4.65,-13.8,-9.8],'operating_state':'stopped','pending':['geometry and access audit','seated visual review','export']}


def animate_service_press():
    """Slow unloaded press cycle with a fixed cylinder anchor and telescoping piston."""
    scene=bpy.context.scene
    if scene.get('density_service_press_animated'):return {'already_present':True}
    piston=bpy.data.objects['DENS_Press_Piston'];plate=bpy.data.objects['DENS_Press_ToolPlate']
    assert piston.parent is None and plate.parent is None
    assert piston.animation_data is None and plate.animation_data is None
    rest_z=plate.location.z;mid=piston.location.z;length=piston.scale.z
    top=mid+length/2;bottom=mid-length/2
    keys=[(1,0),(121,0),(361,.65),(481,.65),(721,0),(1201,0)]
    for frame,travel in keys:
        plate.location.z=rest_z-travel;plate.keyframe_insert('location',index=2,frame=frame)
        piston.location.z=(top+bottom-travel)/2;piston.scale.z=length+travel
        piston.keyframe_insert('location',index=2,frame=frame);piston.keyframe_insert('scale',index=2,frame=frame)
    for obj in [plate,piston]:
        for layer in obj.animation_data.action.layers:
            for strip in layer.strips:
                bag=strip.channelbag(obj.animation_data.action_slot)
                if bag:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
                        curve.modifiers.new('CYCLES')
    scene['density_service_press_animated']=True;scene.frame_set(1)
    return {'stroke_m':.65,'period_s':50,'unloaded':True,'fixed_piston_top_z':top,'keys':keys,'pending':['full-cycle clearance audit','exported motion audit']}


def add_parked_service_crane():
    """Second parked maintenance bridge on the existing runway, outside crane motion."""
    c=collection('DENS_ServiceCrane')
    if len(c.objects):return {'already_present':True}
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    source=bpy.data.collections['WKS_Overhead_Crane']
    made=[]
    for obj in list(source.objects):
        if obj.type!='MESH' or obj.hide_render or obj.name.startswith('CRANE_runway'):continue
        matrix=obj.matrix_world.copy();matrix.translation.y-=19.45
        if obj.name.startswith(('CRANE_trolley','CRANE_hoist_motor','CRANE_wire_rope','CRANE_hook')):matrix.translation.x+=6
        clone=obj.copy();clone.name='DENS_ServiceCrane_'+obj.name;clone.animation_data_clear();clone.parent=None;clone.matrix_parent_inverse=Matrix.Identity(4);c.objects.link(clone);clone.matrix_world=matrix
        clone['density_managed']=True;clone['density_cell']='ServiceCrane';clone['purpose']='Parked unloaded maintenance bridge on existing runway; separate from moving rear crane';made.append(clone.name)
    assert len(made)==9,made
    return {'components':len(made),'bridge_y':-10,'trolley_x':3,'operating_state':'parked and unloaded','shared_source_meshes':True,'pending':['runway contacts','whole crane sweep clearance','portal and seated review']}


def add_hydraulic_test_guard():
    """Visual service-bay enclosure; not a certified pressure-test guard design."""
    c=collection('DENS_HydraulicTestGuard')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    teal=material('DENS_EnamelTeal',(.035,.21,.22),.35,.38)
    yellow=material('DENS_SafetyYellow',(.75,.51,.025),.25,.42)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    def box(tag,p,sz,m=steel):return body('DENS_TestGuard_'+tag,p,sz,c,m)
    # Within existing plinth; open top permits crane loading. Two sliding leaves
    # on the aisle side preserve a service opening without swinging into the aisle.
    for ix,x in enumerate([3.45,6.12]):
        for iy,y in enumerate([9.95,12.8,15.65]):
            box(f'Foot_{ix}_{iy}',(x,y,.34 if iy==1 else .04),(.12,.12,.08),zinc)
            box(f'Post_{ix}_{iy}',(x,y,1.69 if iy==1 else 1.54),(.08,.08,2.7 if iy==1 else 3.0),yellow)
        box(f'TopRail_{ix}',(x,12.8,3.04),(.10,5.78,.12),yellow)
    for i,y in enumerate([9.95,15.65]):
        box(f'EndRail_{i}',(4.785,y,3.04),(2.75,.1,.12),yellow)
        box(f'EndPanel_{i}',(4.785,y,1.08),(2.59,.045,1.4),teal)
        for j in range(14):
            box(f'EndBar_{i}_{j}',(3.56+j*.188,y,2.40),(.018,.025,1.16),zinc)
        box(f'EndMeshRail_{i}',(4.785,y,2.4),(2.59,.025,.025),zinc)
    # Rear panel separated into bays, with deliberate hose slots at both ports.
    for i,(a,b) in enumerate([(10.01,12.88),(13.12,14.48),(14.72,15.59)]):
        box(f'RearPanel_{i}',(6.12,(a+b)/2,1.08),(.045,b-a,1.4),teal)
    for j in range(26):
        box(f'RearBar_{j}',(6.12,10.4+j*.192,2.40),(.025,.018,1.16),zinc)
    box('RearMeshRail',(6.12,12.8,2.4),(.025,4.98,.025),zinc)
    # Closed sliding guards retain the visible cylinder through sparse mesh.
    for i,(a,b) in enumerate([(10.03,12.75),(12.85,15.57)]):
        y=(a+b)/2
        box(f'DoorLower_{i}',(3.40,y,1.08),(.045,b-a,1.4),teal)
        for edge,yy in enumerate([a,b]):box(f'DoorEdge_{i}_{edge}',(3.40,yy,1.7),(.06,.06,2.6),yellow)
        for j in range(13):box(f'DoorMesh_{i}_{j}',(3.40,a+.08+j*.184,2.4),(.025,.018,1.16),zinc)
        box(f'DoorMeshRail_{i}',(3.4,y,2.4),(.025,b-a,.025),zinc)
        box(f'Handle_{i}',(3.31,12.62+i*.36,1.7),(.08,.035,.3),yellow)
        for j,yy in enumerate([a+.18,b-.18]):
            cylinder(f'DENS_TestGuard_DoorRoller_{i}_{j}',(3.31,yy,3.04),(3.43,yy,3.04),.065,c,steel,12)
    box('ControlBox',(3.34,10.47,1.63),(.14,.26,.4),steel)
    cylinder('DENS_TestGuard_Stop',(3.24,10.47,1.68),(3.20,10.47,1.68),.04,c,material('DENS_StopRed',(.65,.025,.012),.1,.4),12)
    for o in c.objects:o['density_cell']='HydraulicTestGuard';o['purpose']='Visual hydraulic service enclosure, sliding access and crane loading'
    return {'components':len(c.objects),'aisle_min_x':3.20,'open_top':True,'hose_slots':[13,14.6],'engineering_certified':False}


def add_inner_bay_ventilation():
    """Connected rectangular air branch above the inner right-hand service bays."""
    c=collection('DENS_InnerBayVentilation')
    if len(c.objects):return {'already_present':True}
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    blue=material('DENS_VentIdentification',(.08,.24,.32),.2,.6)
    def box(tag,p,sz,m=zinc):return body('DENS_InnerVent_'+tag,p,sz,c,m,chamfer=.008)
    # Square duct elbows are enclosed fabricated junctions, not open pipe ends.
    box('LongitudinalTrunk',(6,-.5,6.4),(.86,33,.86))
    box('FrontRiser',(6,-17,7.8),(.86,.86,2.8))
    box('CrossFeed',(11.9,-17,9.2),(11.8,.86,.86))
    box('OuterRiser',(17.8,-17,8.275),(.86,.86,1.85))
    box('RoundMainAdapter',(17.8,-17,7.35),(1.12,.86,.86))
    # Fabricated corner covers and visible bolted flange bands.
    for i,(x,z) in enumerate([(6,6.4),(6,9.2),(17.8,9.2)]):
        box(f'CornerCover_{i}',(x,-17.445,z),(.68,.035,.68),steel)
        for j,(dx,dz) in enumerate([(-.27,-.27),(-.27,.27),(.27,-.27),(.27,.27)]):
            cylinder(f'DENS_InnerVent_CornerBolt_{i}_{j}',(x+dx,-17.46,z+dz),(x+dx,-17.49,z+dz),.022,c,zinc,6)
    for i in range(13):
        y=-17+i*2.75
        for side in [-1,1]:
            box(f'JointSide_{i}_{side}',(6+side*.455,y,6.4),(.05,.055,.96),steel)
            box(f'JointCap_{i}_{side}',(6,y,6.4+side*.455),(.86,.055,.05),steel)
    for i,x in enumerate([8,10.5,13,15.5]):
        for side in [-1,1]:
            box(f'FeedJointSide_{i}_{side}',(x,-17+side*.455,9.2),(.055,.05,.96),steel)
            box(f'FeedJointCap_{i}_{side}',(x,-17,9.2+side*.455),(.055,.86,.05),steel)
    for i,y in enumerate([-14.5,-9,-3.5,2,7.5,13]):
        box(f'OutletBoot_{i}',(6,y,5.91),(.70,1.1,.24),steel)
        for j in range(6):box(f'Louvre_{i}_{j}',(6,y-.45+j*.18,5.77),(.66,.075,.06))
        box(f'IDBand_{i}',(5.56,y,6.4),(.025,.22,.55),blue)
    # Six braced cantilevers join the inner column row. No roof hangers cross
    # either crane's movement envelope. The bottom of the duct rests on saddles.
    for i,y in enumerate([-13.75,-8.25,-2.75,2.75,8.25,13.75]):
        box(f'ColumnPlate_{i}',(9.33,y,5.6),(.10,.32,.9),steel)
        box(f'Cantilever_{i}',(7.45,y,5.90),(3.85,.12,.14),steel)
        cylinder(f'DENS_InnerVent_Brace_{i}',(9.3,y,5.18),(6.5,y,5.85),.045,c,steel,8)
        box(f'Saddle_{i}',(6,y,5.95),(1.05,.20,.08),steel)
    for o in c.objects:o['density_cell']='InnerBayVentilation';o['purpose']='Connected inner service-bay ventilation with column-supported trunk and downward registers'
    return {'components':len(c.objects),'length_m':33,'outlets':6,'main_connection':[17.8,-17,7.35],'support_column_x':9.5}


def add_west_inner_bay_ventilation():
    """Matching west branch offset outward to clear the crane trolley/hook."""
    c=collection('DENS_WestInnerBayVentilation')
    if len(c.objects):return {'already_present':True}
    source=bpy.data.collections['DENS_InnerBayVentilation']
    reflect=Matrix.Diagonal((-1,1,1,1));made=[]
    for obj in source.objects:
        assert obj.type=='MESH' and obj.parent is None and not obj.animation_data
        clone=obj.copy();clone.name=obj.name.replace('DENS_InnerVent_','DENS_WestVent_');c.objects.link(clone);clone.matrix_world=reflect@obj.matrix_world
        tag=obj.name.removeprefix('DENS_InnerVent_')
        # Left branch sits one metre farther from the central crane path.
        if tag.startswith(('LongitudinalTrunk','FrontRiser','JointSide','JointCap','OutletBoot','Louvre','IDBand','Saddle','CornerCover_0','CornerCover_1','CornerBolt_0','CornerBolt_1')):
            clone.location.x-=1
        elif tag=='CrossFeed':
            clone.location.x-=.5;clone.data=clone.data.copy()
            for vertex in clone.data.vertices:vertex.co.x*=10.8/11.8
            clone.data.update()
        elif tag.startswith('Cantilever'):
            clone.location.x-=.5;clone.data=clone.data.copy()
            for vertex in clone.data.vertices:vertex.co.x*=2.85/3.85
            clone.data.update()
        elif tag.startswith('Brace'):
            y=clone.location.y;a,b=Vector((-9.3,y,5.18)),Vector((-7.5,y,5.85))
            clone.location=(a+b)/2;clone.scale=(.045,.045,(b-a).length);clone.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
        clone['density_cell']='WestInnerBayVentilation';clone['purpose']='West inner-bay ventilation with outward offset to clear moving crane';made.append(clone.name)
    return {'components':len(made),'length_m':33,'outlets':6,'main_connection':[-17.8,-17,7.35],'inner_trunk_x':-7,'shared_meshes':True}


def add_welding_bay_screens():
    """Opaque, pleated workshop screens beside the existing welding bench."""
    c=collection('DENS_WeldingScreens')
    if len(c.objects):return {'already_present':True}
    steel=material('DENS_Graphite',(.055,.071,.078),.7,.43)
    zinc=material('DENS_Galvanised',(.42,.46,.47),.8,.48)
    fabric=material('DENS_WeldingScreenBurgundy',(.18,.022,.018),0,.84)
    rubber=material('DENS_Rubber',(.018,.021,.023),.05,.85)
    for i,cy in enumerate([-.37,1.07]):
        x=3.22;y0=cy-.69;y1=cy+.69
        for j,y in enumerate([y0,y1]):
            cylinder(f'DENS_WeldScreen_Post_{i}_{j}',(x,y,.12),(x,y,2.58),.025,c,zinc,12)
            body(f'DENS_WeldScreen_Foot_{i}_{j}',(x,y,.10),(.26,.14,.06),c,steel,chamfer=.01)
            for k,xx in enumerate([x-.085,x+.085]):
                cylinder(f'DENS_WeldScreen_Wheel_{i}_{j}_{k}',(xx,y-.025,.055),(xx,y+.025,.055),.05,c,rubber,12)
        cylinder(f'DENS_WeldScreen_Top_{i}',(x,y0,2.56),(x,y1,2.56),.025,c,zinc,12)
        cylinder(f'DENS_WeldScreen_Bottom_{i}',(x,y0,.28),(x,y1,.28),.018,c,zinc,12)
        # Closed thin slab with shallow pleats: no transparent overdraw in VR.
        n=33;verts=[]
        for dx in [-.006,.006]:
            for z in [.30,2.49]:
                for j in range(n):
                    y=y0+.045+(y1-y0-.09)*j/(n-1)
                    verts.append((x+dx+.022*math.sin(j*math.tau/8),y,z))
        faces=[]
        for j in range(n-1):
            faces.extend([(j,j+1,n+j+1,n+j),(2*n+j,3*n+j,3*n+j+1,2*n+j+1),(j,2*n+j,2*n+j+1,j+1),(n+j,n+j+1,3*n+j+1,3*n+j)])
        faces.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
        mesh_object(f'DENS_WeldScreen_Curtain_{i}',verts,faces,c,fabric)
        for j in range(8):
            y=y0+.10+(y1-y0-.20)*j/7
            cylinder(f'DENS_WeldScreen_Hanger_{i}_{j}',(x,y,2.47),(x,y,2.56),.009,c,zinc,8)
            cylinder(f'DENS_WeldScreen_Eyelet_{i}_{j}',(x-.034,y,2.46),(x+.034,y,2.46),.018,c,zinc,12)
    for o in c.objects:o['density_cell']='WeldingScreens';o['purpose']='Parked welding screens between fabrication bench and central route'
    return {'components':len(c.objects),'aisle_min_x':3.09,'panels':2,'opaque_material':True,'operator_access':'open bench ends, screens parked along aisle side'}


def clear_fan_belting_sightline():
    """Park spare belting farther into its service bay to reveal the wall fans."""
    scene=bpy.context.scene
    if scene.get('density_belting_sightline_repaired'):return {'already_present':True}
    c=bpy.data.collections['DENS_BeltingStore'];moved=[]
    for o in c.objects:
        assert o.parent is None and not o.animation_data
        o.location.y-=1.6;moved.append(o.name)
    scene['density_belting_sightline_repaired']=True
    return {'objects':len(moved),'translation':[0,-1.6,0],'purpose':'Restore seated sightline to wall fan B'}


def clear_fan_test_bench_sightline():
    """Move the complete motor-test station along its bay, retaining rotor rig."""
    scene=bpy.context.scene
    if scene.get('density_test_bench_sightline_repaired'):return {'already_present':True}
    scene.frame_set(1);c=collection('DENS_MotorTestRelocation')
    objects=[o for o in scene.objects if o.name.startswith(('FIT_TestBench','FIT_TestMotor','DENS_TestPanel','FIT_Tag_TestBench'))]
    names={o.name for o in objects};assert len(objects)==163
    for o in objects:
        assert not o.constraints and (o.parent is None or o.parent.name in names)
        if c not in list(o.users_collection):c.objects.link(o)
        if o.parent is None:o.location.y+=4.0
    rotor=bpy.data.objects['FIT_TestBench_Rotor'];expected=rotor.location.copy()
    for frame in [1,121,241,1201]:
        scene.frame_set(frame);bpy.context.view_layer.update()
        assert (rotor.location-expected).length<1e-6,'Unexpected animated location channel'
    scene.frame_set(1);scene['density_test_bench_sightline_repaired']=True
    return {'objects':len(objects),'translation':[0,4,0],'rotor_location':list(expected),'purpose':'Clear both wall fan faces from seated view'}
