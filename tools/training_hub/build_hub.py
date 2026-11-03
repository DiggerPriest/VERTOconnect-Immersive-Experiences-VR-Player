"""Reproducible seated training-hub prototype (Blender 4.5.3).

blender --background --python tools/training_hub/build_hub.py -- --output DIR
Produces actual geometry, not a panorama. See docs/training-hub/design.md.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
parser.add_argument('--bake', action='store_true', help='Bake diffuse lighting to portable unlit texture atlases')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
output = Path(args.output).resolve()
output.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.render.fps = 30
scene.frame_end = 600
static_objects = []


def material(name, color, metallic=0, roughness=.6, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    m.use_backface_culling = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m


M = {
    'steel': material('Powder coated graphite', (.045, .055, .060), .35, .55),
    'concrete': material('Warm concrete', (.43, .44, .42)),
    'wall': material('Warm plaster', (.73, .73, .68)),
    'gold': material('VERTO gold', (1, .62, .025), .3, .32),
    'wood': material('Oak', (.49, .27, .105), 0, .55),
    'navy': material('Workwear navy', (.025, .055, .09)),
    'silver': material('Brushed aluminium', (.47, .53, .56), .65, .3),
    'copper': material('Copper pipe', (.52, .24, .10), .6, .3),
    'black': material('Rubber', (.025, .03, .035)),
    'white': material('Ivory lettering', (.94, .95, .9)),
    'red': material('Red switch', (.7, .055, .025)),
    'blue': material('Blue pipe', (.035, .21, .47)),
    'light': material('Warm strip diffuser', (1, .83, .51), 0, .4, 1.0),
    'sky': material('Skylight', (.55, .72, .86), 0, 1, .15),
    'green': material('Indoor foliage', (.08, .19, .075)),
    'glass': material('Blue smoked glazing', (.16, .25, .29), .2, .25),
    'screen': material('Instrument LCD', (.025, .15, .17), 0, .4, .15),
    'offwhite': material('Enclosure enamel', (.68, .7, .66), .1, .5),
}


def procedural_surface(key, dark, light, scale, grain=False):
    """Author original tile-free surface colour, subsequently baked to a UV atlas."""
    m=M[key]; nodes=m.node_tree.nodes; links=m.node_tree.links
    p=nodes.get('Principled BSDF')
    tex=nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=scale
    tex.inputs['Detail'].default_value=3; tex.inputs['Roughness'].default_value=.7
    coords=nodes.new('ShaderNodeNewGeometry')
    if grain:
        mapping=nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(.5,18,18)
        links.new(coords.outputs['Position'],mapping.inputs[0])
        links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
    else:
        links.new(coords.outputs['Position'],tex.inputs['Vector'])
    ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.2
    ramp.color_ramp.elements[0].color=(*dark,1)
    ramp.color_ramp.elements[1].position=.8
    ramp.color_ramp.elements[1].color=(*light,1)
    links.new(tex.outputs['Fac'],ramp.inputs[0]); links.new(ramp.outputs['Color'],p.inputs['Base Color'])
    bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.13
    bump.inputs['Distance'].default_value=.006 if key=='concrete' else .002
    links.new(tex.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],p.inputs['Normal'])


if args.bake:
    # Broad floor uses clean baked illumination; fine repeated detail is applied
    # by training_hub_surfaces.gd at runtime to avoid a stretched room-size atlas.
    M['concrete'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.34,.35,.33,1)
    procedural_surface('wood',(.24,.10,.035),(.54,.31,.12),4,True)
    procedural_surface('wall',(.62,.63,.60),(.76,.77,.72),14)


def finish(obj, name, mat, parent=None):
    obj.name = name
    obj.data.materials.append(M[mat])
    if parent:
        obj.parent = parent
    static_objects.append(obj)
    return obj


def box(name, loc, size, mat='steel', parent=None, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Small manufactured edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        o.modifiers.new('Normals', 'WEIGHTED_NORMAL')
    return finish(o, name, mat, parent)


def cylinder(name, a, b, radius, mat='silver', parent=None, vertices=12):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return finish(o, name, mat, parent)


def lettering(name, text, loc, size, mat='white', parent=None):
    c = bpy.data.curves.new(name, 'FONT')
    c.body = text
    c.size = size
    c.align_x = 'CENTER'
    c.extrude = .002
    c.resolution_u = 4
    o = bpy.data.objects.new(name, c)
    scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.pi/2, 0, 0)
    o.data.materials.append(M[mat])
    if parent:
        o.parent = parent
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    o.select_set(False)
    static_objects.append(o)
    return o


def bench(parent, x=0, y=0, width=3):
    box('Workbench top', (x,y,.96), (width,.8,.09), 'wood', parent, .018)
    for dx in [-width/2+.12, width/2-.12]:
        for dy in [-.28,.28]:
            box('Bench leg', (x+dx,y+dy,.46), (.055,.055,.92), parent=parent)
    box('Bench low shelf', (x,y,.24), (width-.16,.65,.055), 'steel', parent)


# Solid 24 x 24 metre building; the user's origin is at its centre.
box('Foundation', (0,0,-.14), (24,24,.28), 'concrete')
for n in range(-8, 12, 4):
    box('Floor joint', (n,0,.002), (.007,24,.003), 'steel')
    box('Floor joint', (0,n,.002), (24,.007,.003), 'steel')
for x in [-12,12]:
    box('Side wall', (x,0,3.5), (.2,24,7), 'wall')
for y in [-12,12]:
    box('End wall', (0,y,3.5), (24,.2,7), 'wall')
for x in [-11.7,11.7]:
    for y in [-11.7,-6,0,6,11.7]:
        box('Steel upright', (x,y,3.5), (.24,.24,7))
        box('Gold base guard', (x,y,.5), (.3,.3,1), 'gold')
for y in [-11.7,-6,0,6,11.7]:
    box('Roof girder', (0,y,6.8), (24,.22,.4))
for x in [-9,-3,3,9]:
    box('Skylight mullion', (x,0,7), (.08,24,.12))
box('Skylight ceiling', (0,0,7.12), (24,24,.08), 'sky')
for x in [-10,10]:
    box('Timber ceiling raft', (x,0,6.4), (3,24,.12), 'wood')
    for offset in [-.8,.8]:
        box('Continuous ceiling light', (x+offset,0,6.31), (.035,23,.025), 'light')

# Quiet foreground seating frames the user's position without obstructing hands.
for x in [-3.8,3.8]:
    box('Seating base', (x,1.6,.22), (1.5,.65,.44), 'steel', bevel=.05)
    box('Seat cushion', (x,1.6,.49), (1.5,.65,.12), 'wood', bevel=.045)
    box('Planter', (x,-2.5,.45), (.75,.75,.9), 'steel', bevel=.04)
    for i in range(12):
        angle = i*2.4
        cylinder('Plant stem', (x,-2.5,.9), (x+.28*math.sin(angle),-2.5+.28*math.cos(angle),1.3+i*.035), .012, 'green')
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=1,
            location=(x+.28*math.sin(angle),-2.5+.28*math.cos(angle),1.3+i*.035))
        o=bpy.context.object; o.scale=(.12,.23,.055)
        o.rotation_euler=(.4,angle,.3)
        finish(o,'Broad leaf','green')

stations=[]
for i, (title, loc, yaw) in enumerate([
    ('ELECTRICAL', (0,8,0),0), ('PLUMBING', (8,0,0),-math.pi/2),
    ('CARPENTRY', (0,-8,0),math.pi), ('MINING & MECHANICAL', (-8,0,0),math.pi/2)]):
    root=bpy.data.objects.new('Bay_'+title, None)
    scene.collection.objects.link(root)
    root.location=loc; root.rotation_euler.z=yaw
    stations.append(root)
    box('Bay back panel',(0,2.2,1.8),(6,.12,3.6),'steel',root)
    box('Bay header',(0,2.08,3.45),(6,.10,.4),'navy',root)
    lettering('Bay name', title,(0,2,3.35),.22,'white',root)
    lettering('Bay number', f'0{i+1}',(-2.6,2,3.35),.22,'gold',root)
    box('Safety threshold',(0,-1.15,.009),(6,.055,.012),'gold',root)
    for x in [-3,3]:
        box('Safety edge',(x,.5,.009),(.055,3.3,.012),'gold',root)
        box('Station upright',(x,2.2,1.8),(.08,.18,3.6),'silver',root)

# Electrical bay: a training installation assembled from recognisable components.
r=stations[0]
bench(r, 0,.5,4)
for x in [-1.45,0,1.45]:
    box('Board enclosure',(x,2.01,2),(1.2,.22,1.65),'offwhite',r,.025)
    box('Recessed interior',(x,1.885,2),(.99,.015,1.41),'steel',r)
    for row in range(3):
        z=1.57+row*.37
        box('DIN rail',(x,1.86,z),(.96,.025,.035),'silver',r)
        for col in range(6):
            xx=x-.42+col*.165
            box('Circuit breaker',(xx,1.81,z),(.12,.10,.23),'white',r,.008)
            box('Breaker operating lever',(xx,1.75,z+.02),(.056,.03,.05),'black',r,.003)
            box('Breaker label',(xx,1.751,z+.075),(.075,.006,.025),'blue',r)
            for zz in [z-.085,z+.085]:
                cylinder('Terminal screw',(xx,1.745,zz),(xx,1.738,zz),.009,'silver',r,8)
    # Four corner fasteners and a framed schedule label.
    for dx in [-.55,.55]:
        for z in [1.25,2.75]:
            cylinder('Enclosure fixing',(x+dx,1.882,z),(x+dx,1.87,z),.013,'silver',r,8)
    box('Circuit schedule',(x,1.871,2.63),(.7,.006,.12),'white',r)
    lettering('Circuit schedule label','TRAINING BOARD',(x,1.86,2.61),.055,'navy',r)
    for dx in [-.3,0,.3]:
        cylinder('Galvanised conduit',(x+dx,1.96,.45),(x+dx,1.96,1.15),.018,'silver',r)
        for z in [.6,.95]:
            box('Conduit clamp',(x+dx,1.936,z),(.055,.028,.025),'steel',r)
    box('Conduit trunk',(x,1.97,1.12),(.85,.085,.08),'silver',r)
# Larger lockable switchgear and an isolation panel make the bay look functional.
for x in [-2.55,2.55]:
    box('Isolation cabinet',(x,1.96,1.75),(.62,.3,1.2),'offwhite',r,.025)
    box('Door perimeter',(x,1.798,1.75),(.54,.015,1.1),'steel',r)
    box('Cabinet door',(x,1.781,1.75),(.5,.02,1.06),'offwhite',r,.012)
    box('Main isolator surround',(x,1.755,1.87),(.24,.022,.24),'gold',r,.012)
    cylinder('Rotary isolator',(x,1.73,1.87),(x,1.685,1.87),.065,'red',r,20)
    box('Cabinet latch',(x+.18,1.75,1.58),(.025,.025,.12),'black',r)
    lettering('Isolation label','ISOLATE',(x,1.75,2.15),.055,'navy',r)
# Cable tray and visible supports above the training stations.
box('Cable tray base',(0,1.72,2.95),(5.7,.28,.025),'silver',r)
for y in [1.58,1.86]:
    box('Cable tray side',(0,y,3.015),(5.7,.025,.14),'silver',r)
for x in [-2,-1,0,1,2]:
    cylinder('Tray suspension',(x,1.72,3.1),(x,1.72,3.55),.009,'silver',r)
for x in [-2.4,-1.9,-1.1,-.6,.4,.9,1.7,2.2]:
    cylinder('Cable drop',(x,1.7,2.95),(x,1.7,2.78),.012,'black',r)
# Work surface: meter, probes, screwdriver, wire cutters, parts bins.
box('Test meter',(-.8,.45,1.075),(.18,.28,.10),'gold',r,.025)
box('Meter display',(-.8,.49,1.13),(.12,.11,.004),'screen',r)
cylinder('Meter dial',(-.8,.36,1.128),(-.8,.36,1.143),.034,'black',r,20)
for x,mat in [(-1.1,'red'),(-1.22,'black')]:
    cylinder('Test probe',(x,.35,1.03),(x,.54,1.03),.013,mat,r)
    cylinder('Probe metal tip',(x,.54,1.03),(x,.60,1.03),.005,'silver',r)
for i in range(3):
    x=-1.55+i*.13
    cylinder('Screwdriver handle',(x,.3,1.035),(x,.43,1.035),.022,'blue',r)
    cylinder('Screwdriver shaft',(x,.43,1.035),(x,.62,1.035),.007,'silver',r)
for x in [-1.65,-1.1,-.55]:
    box('Parts bin',(x,.62,.37),(.4,.5,.21),'blue',r,.025)
    box('Bin label',(x,.357,.38),(.21,.008,.055),'white',r)
# Reachable low-voltage practice terminal for the electrical worker's probe.
box('Bench test terminal',(1.34,.40,1.15),(.32,.20,.29),'offwhite',r,.018)
box('Terminal front panel',(1.34,.294,1.15),(.27,.012,.24),'navy',r)
for dx,mat in [(-.065,'black'),(.0,'red'),(.065,'black')]:
    cylinder('Test socket',(1.34+dx,.286,1.20),(1.34+dx,.275,1.20),.014,mat,r,12)
lettering('Low voltage label','24V DC',(1.34,.283,1.08),.035,'white',r)
# Drawer trolley beside bench, including handles and casters.
box('Tool trolley',(-2.4,.35,.52),(.85,.65,.88),'red',r,.035)
for z in [.26,.4,.54,.68,.82]:
    box('Drawer front',(-2.4,.012,z),(.76,.025,.12),'steel',r,.008)
    cylinder('Drawer handle',(-2.67,-.018,z+.025),(-2.13,-.018,z+.025),.012,'silver',r)
for x in [-2.7,-2.1]:
    for y in [.1,.6]:
        cylinder('Trolley caster',(x-.035,y,.09),(x+.035,y,.09),.07,'black',r,16)
box('Trolley top',(-2.4,.35,.99),(.9,.7,.055),'black',r,.012)
# Electrical bay has a rubber standing mat; no training claims implied.
box('Standing mat',(0,-.3,.018),(4.5,.8,.025),'black',r,.025)

# Plumbing: copper circuits, insulated cylinder, sink, drainage and a reachable valve.
r=stations[1]
bench(r,0,.6,3.8)
for i in range(4):
    x=-2.4+i*1.12
    for a,b in [((x,1.94,.4),(x,1.94,2.8)),((x,1.94,2.8),(x+.72,1.94,2.8)),((x+.72,1.94,2.8),(x+.72,1.94,1.5))]:
        cylinder('Copper distribution pipe',a,b,.027,'copper',r,16)
    for z in [.6,1.3,2.4]:
        cylinder('Pipe compression coupling',(x,1.94,z-.04),(x,1.94,z+.04),.041,'copper',r,12)
        box('Pipe saddle',(x,1.97,z),(.11,.08,.025),'silver',r)
    cylinder('Gate valve body',(x,1.94,1.72),(x,1.94,1.92),.06,'silver',r)
    cylinder('Valve stem',(x,1.94,1.82),(x,1.78,1.82),.017,'silver',r)
    for dx in [-.1,.1]:
        cylinder('Valve handwheel spoke',(x,1.76,1.82),(x+dx,1.76,1.82),.012,'red' if i%2 else 'blue',r)
    cylinder('Pressure gauge case',(x+.72,1.94,2.1),(x+.72,1.85,2.1),.105,'silver',r,24)
    cylinder('Pressure gauge face',(x+.72,1.845,2.1),(x+.72,1.84,2.1),.091,'white',r,24)
    cylinder('Gauge needle',(x+.72,1.831,2.1),(x+.76,1.831,2.15),.004,'black',r,8)
# Open basin built with rim and dark inset rather than a solid slab.
box('Sink underside',(-.95,.55,.99),(.9,.57,.16),'silver',r,.04)
box('Sink bowl',(-.95,.55,1.077),(.71,.40,.01),'steel',r,.035)
for x in [-1.38,-.52]: box('Sink rim',(x,.55,1.09),(.07,.57,.03),'silver',r,.012)
for y in [.3,.8]: box('Sink rim',(-.95,y,1.09),(.9,.07,.03),'silver',r,.012)
cylinder('Tap upright',(-.95,.86,1),(-.95,.86,1.42),.022,'silver',r)
cylinder('Tap spout',(-.95,.86,1.42),(-.95,.58,1.42),.022,'silver',r)
cylinder('Tap outlet',(-.95,.58,1.42),(-.95,.58,1.36),.022,'silver',r)
for a,b in [((-.95,.55,.91),(-.95,.55,.6)),((-.95,.55,.6),(-.95,.85,.6)),((-.95,.85,.6),(-.95,.85,.8)),((-.95,.85,.8),(-.95,1.9,.8))]:
    cylinder('Sink waste trap',a,b,.042,'white',r)
cylinder('Insulated hot water cylinder',(2.4,1.25,.12),(2.4,1.25,2.25),.39,'offwhite',r,32)
for z in [.25,2.13]: cylinder('Tank end band',(2.4,1.25,z-.035),(2.4,1.25,z+.035),.403,'silver',r,32)
box('Tank controller',(2.4,.85,1.35),(.27,.10,.35),'steel',r,.015)
box('Tank LCD',(2.4,.792,1.42),(.17,.01,.09),'screen',r)
for x in [2.2,2.6]: cylinder('Tank feed',(x,1.25,2.25),(x,1.25,2.75),.03,'copper',r)
# Worker manipulates this bench-mounted valve at the agreed hand contact.
cylinder('Practice pipe',(1.34,.45,1.01),(1.34,.45,1.45),.03,'copper',r)
cylinder('Practice valve spindle',(1.34,.45,1.2),(1.34,.30,1.2),.024,'silver',r)
box('Practice lever',(1.34,.295,1.2),(.23,.025,.035),'blue',r,.008)
cylinder('Wrench contact branch',(1.34,.45,1.38),(1.26,.40,1.38),.028,'copper',r)
cylinder('Wrench hex fitting',(1.26,.43,1.38),(1.26,.37,1.38),.047,'silver',r,6)
for x in [.45,.7]:
    cylinder('Spare pipe length',(x,.42,1.03),(x,.9,1.03),.025,'copper',r)
box('Pipe fitting bin',(.05,.7,1.08),(.38,.3,.15),'blue',r,.015)

# Carpentry: framed opening, bracing, realistic joiner's bench and hand tools.
r=stations[2]
bench(r,0,.4,4.4)
for x in [-2.5,-1.9,-1.3,-.7,.7,1.3,1.9,2.5]:
    box('Timber wall stud',(x,1.95,1.5),(.09,.14,3),'wood',r)
for z in [.06,3.0]: box('Timber wall plate',(0,1.95,z),(5.1,.14,.09),'wood',r)
box('Door opening header',(0,1.95,2.2),(1.5,.14,.18),'wood',r)
for x in [-2.2,-1.6,-1,1,1.6,2.2]: box('Stud noggin',(x,1.95,1.4),(.5,.14,.09),'wood',r)
cylinder('Steel diagonal bracing',(-2.5,1.86,.2),(-.75,1.86,2.9),.016,'silver',r)
for i in range(4): box('Timber stock',(-.8,.6,1.035+i*.045),(2.3,.12,.04),'wood',r)
# Broad measuring board lies flat under the worker's hands.
box('Measurement workpiece',(1.18,.40,1.035),(1.1,.36,.05),'wood',r,.005)
box('Carpenter square blade',(1.10,.30,1.066),(.48,.025,.006),'silver',r)
box('Carpenter square stock',(.86,.39,1.075),(.035,.20,.025),'black',r)
for i in range(11): box('Ruler graduation',(.88+i*.043,.30,1.071),(.002,.013,.002),'black',r)
# Bench vice has two jaws, screw and sliding handle.
box('Vice fixed jaw',(-1.6,-.04,.93),(.5,.09,.22),'steel',r,.012)
box('Vice moving jaw',(-1.6,-.18,.93),(.5,.09,.22),'blue',r,.012)
cylinder('Vice screw',(-1.6,.1,.89),(-1.6,-.32,.89),.028,'silver',r)
cylinder('Vice cross handle',(-1.8,-.33,.89),(-1.4,-.33,.89),.012,'silver',r)
box('Hand plane body',(-.5,.15,1.06),(.3,.09,.09),'steel',r,.015)
box('Plane wood handle',(-.59,.15,1.14),(.07,.045,.1),'wood',r,.02)
cylinder('Plane front knob',(-.41,.15,1.10),(-.41,.15,1.16),.027,'wood',r)
cylinder('Claw hammer handle',(-.1,.2,1.04),(-.1,.55,1.04),.018,'wood',r)
box('Hammer head',(-.1,.55,1.04),(.15,.055,.05),'silver',r,.012)
for x in [-2.8,2.8]:
    for z in [.5,1.0,1.5]: box('Timber rack arm',(x,1.45,z),(.08,.8,.06),'steel',r)
    box('Stock rack upright',(x,1.8,.9),(.07,.07,1.8),'steel',r)
for i in range(5): box('Racked long timber',(0,1.3+i*.09,.55),(5.7,.075,.07),'wood',r)

# Mechanical: stationary motor/pump skid, flanged pipework, guard and service rig.
r=stations[3]
box('Machine plinth',(-.55,.9,.18),(3.6,1.5,.36),'steel',r,.04)
cylinder('Electric motor barrel',(-1.85,.9,.85),(-.6,.9,.85),.42,'blue',r,32)
for i in range(16):
    a=i*math.tau/16
    o=box('Motor cooling rib',(-1.23,.9+.42*math.cos(a),.85+.42*math.sin(a)),(1.14,.04,.085),'steel',r)
    o.rotation_euler.x=a-math.pi/2
for x in [-1.83,-.65]: cylinder('Motor end cap',(x-.035,.9,.85),(x+.035,.9,.85),.445,'blue',r,32)
box('Motor terminal box',(-1.3,.9,1.36),(.4,.35,.20),'blue',r,.025)
for x in [-1.7,-.8]:
    box('Motor mounting foot',(x,.9,.4),(.3,.95,.12),'blue',r)
    for y in [.5,1.3]: cylinder('Foundation bolt',(x,y,.4),(x,y,.49),.025,'silver',r,6)
cylinder('Coupling shaft',(-.6,.9,.85),(.1,.9,.85),.09,'silver',r,20)
# Slotted safety guard visibly surrounds the coupling.
for x in [-.5,-.4,-.3,-.2,-.1,0]:
    cylinder('Coupling guard bar',(x,.62,.49),(x,.62,1.15),.018,'gold',r)
box('Coupling guard lid',(-.25,.9,1.15),(.65,.62,.04),'gold',r)
cylinder('Centrifugal pump casing',(.3,.9,.7),(.3,.9,1.0),.34,'silver',r,24)
cylinder('Pump outlet',(.3,.9,1),(.3,.9,1.6),.09,'silver',r,20)
cylinder('Discharge pipe',(.3,.9,1.6),(.3,1.8,1.6),.09,'silver',r,20)
for z in [1.2,1.4]:
    cylinder('Pipe flange',(.3,.9,z-.025),(.3,.9,z+.025),.15,'silver',r,20)
    for i in range(6):
        a=i*math.tau/6
        cylinder('Flange bolt',(.3+.12*math.cos(a),.9+.12*math.sin(a),z-.04),(.3+.12*math.cos(a),.9+.12*math.sin(a),z+.04),.014,'steel',r,6)
# Service console placed to one side; worker inspects tablet without machinery contact.
box('Service console',(1.8,1.25,1.0),(.75,.65,1.6),'offwhite',r,.025)
box('Console control face',(1.8,.91,1.35),(.65,.025,.6),'steel',r)
box('Console LCD',(1.8,.89,1.47),(.43,.01,.24),'screen',r)
for x,mat in [(1.62,'green'),(1.8,'red'),(1.98,'gold')]:
    cylinder('Console pushbutton',(x,.87,1.16),(x,.84,1.16),.035,mat,r,16)
for x in [-2.5,2.7]:
    for y in [-.25,1.6]: cylinder('Guard post',(x,y,0),(x,y,1),.035,'gold',r)
    cylinder('Guard rail',(x,-.25,1),(x,1.6,1),.035,'gold',r)
for x in [-1.8,-.6,.6,1.8]:
    box('Service tool board',(x,2.04,2.1),(1.04,.07,1.05),'offwhite',r,.01)
    for j in range(4):
        xx=x-.34+j*.22
        cylinder('Hanging spanner stem',(xx,1.98,1.85),(xx,1.98,2.3),.012,'silver',r)
        cylinder('Spanner ring',(xx,1.99,2.3),(xx,1.96,2.3),.034,'silver',r,12)
lettering('Mechanical lockout label','ISOLATED TRAINING EQUIPMENT',(0,1.99,2.8),.10,'gold',r)

# Upper gallery, glazed classrooms and structural bracing add architectural depth.
for side in [-1,1]:
    x=side*10.5
    box('Upper gallery deck',(x,0,3.85),(2.7,23,.18),'concrete')
    for y in range(-10,11,2):
        box('Gallery balustrade post',(side*9.1,y,4.4),(.045,.045,1.0),'silver')
        box('Gallery rail shadow',(side*9.1,y,3.99),(.1,.1,.02),'black')
    for z in [4.0,4.9]:
        cylinder('Gallery continuous rail',(side*9.1,-11,z),(side*9.1,11,z),.03,'silver')
    for z in [4.25,4.5,4.72]:
        cylinder('Gallery horizontal infill',(side*9.1,-11,z),(side*9.1,11,z),.011,'steel')
    for y in [-9,-5,-1,3,7]:
        box('Classroom glazing',(side*11.85,y,5.1),(.025,3.7,2.1),'glass')
        for yy in [y-1.85,y,y+1.85]:
            box('Classroom mullion',(side*11.82,yy,5.1),(.06,.055,2.2),'silver')
    for y in [-9,-3,3,9]:
        cylinder('Diagonal steel brace',(side*11.7,y-2,3.7),(side*11.7,y+2,6.7),.06,'steel')
# Northern clerestory and lower utility room doors flank the electrical bay.
for x in [-9,-5,0,5,9]:
    box('Clerestory frame',(x,11.79,5.1),(3.6,.08,2.0),'steel')
    box('Clerestory glazing',(x,11.73,5.1),(3.4,.025,1.8),'glass')
    for dx in [-.85,0,.85]:
        box('Window vertical mullion',(x+dx,11.70,5.1),(.04,.025,1.8),'silver')
for x in [-7,7]:
    box('Utility doorway',(x,11.77,1.3),(1.45,.08,2.6),'steel')
    box('Utility door',(x,11.71,1.25),(1.28,.05,2.42),'wood',bevel=.015)
    box('Door vision panel',(x,11.67,1.75),(.45,.025,.75),'glass')
    cylinder('Door pull',(x+.42,11.6,1),(x+.42,11.6,1.3),.014,'silver')
# Far-wall service installation helps avoid an empty hangar impression.
for x in [-10.9,10.9]:
    box('Tall storage cabinet',(x,9.8,1.1),(1.1,.7,2.2),'steel',bevel=.02)
    for dx in [-.27,.27]:
        box('Storage door',(x+dx,9.43,1.1),(.5,.03,2.08),'offwhite',bevel=.01)
        cylinder('Storage handle',(x+dx+.16,9.39,1),(x+dx+.16,9.39,1.2),.012,'black')

# Visible from the default forward-facing menu position.
box('Brand sign',(0,5.5,4.35),(5.5,.14,.85),'navy',bevel=.04)
lettering('Brand wordmark','VERTOconnect',(0,5.39,4.32),.48,'gold')
lettering('Brand descriptor','IMMERSIVE EXPERIENCES',(0,5.39,4.04),.13)
for x in [-2.35,2.35]:
    cylinder('Sign suspension',(x,5.5,4.78),(x,5.5,6.55),.012,'silver')

# Merge static geometry by material so hundreds of fixtures do not mean hundreds
# of draw calls. Separate material batches preserve a modest bounding volume.
bpy.ops.object.select_all(action='DESELECT')
for mat in list(M.values()):
    objects=[o for o in scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==mat]
    if not objects:
        continue
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join()
    o=bpy.context.object
    o.name='Architecture_'+mat.name.replace(' ','_')
    # Keep its world matrix when detaching the station parent.
    matrix=o.matrix_world.copy(); o.parent=None; o.matrix_world=matrix
    bpy.ops.object.select_all(action='DESELECT')

def denoise_atlas(image, destination):
    """Blender compositor OIDN removes bake sampling noise, not surface texture."""
    temp=bpy.data.scenes.new('Atlas denoising')
    temp.render.engine='CYCLES'; temp.cycles.samples=1
    temp.render.resolution_x=image.size[0]; temp.render.resolution_y=image.size[1]
    temp.render.resolution_percentage=100
    temp.render.image_settings.file_format='PNG'
    temp.render.image_settings.color_mode='RGB'
    temp.render.filepath=str(destination)
    temp.view_settings.view_transform='Standard'
    temp.view_settings.look='None'
    camera_data=bpy.data.cameras.new('Atlas camera')
    camera=bpy.data.objects.new('Atlas camera',camera_data)
    temp.collection.objects.link(camera); temp.camera=camera
    if hasattr(temp, 'compositing_node_group'):
        tree=bpy.data.node_groups.new('Atlas denoise compositor','CompositorNodeTree')
        tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
        temp.compositing_node_group=tree
    else:
        temp.use_nodes=True
        tree=temp.node_tree
    nodes=tree.nodes; nodes.clear()
    source=nodes.new('CompositorNodeImage'); source.image=image
    denoise=nodes.new('CompositorNodeDenoise')
    if hasattr(denoise, 'use_hdr'): denoise.use_hdr=True
    target=nodes.new('NodeGroupOutput' if hasattr(temp, 'compositing_node_group') else 'CompositorNodeComposite')
    tree.links.new(source.outputs['Image'],denoise.inputs['Image'])
    tree.links.new(denoise.outputs['Image'],target.inputs['Image'])
    bpy.ops.render.render(write_still=True,scene=temp.name)
    bpy.data.scenes.remove(temp)
    bpy.data.objects.remove(camera,do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    # Use the compositor result rather than the original still-packed noisy bake.
    clean=bpy.data.images.load(str(destination),check_existing=False)
    clean.name=image.name+'_denoised'; clean.pack()
    return clean


# Bake view-independent diffuse illumination into portable textures. The app
# uses these as unlit materials: no realtime GI or multiple room lights on Quest.
# The authoring blend retains the procedural shaders and lights before baking.
if args.bake:
    scene.render.engine='CYCLES'
    scene.cycles.samples=96
    scene.cycles.max_bounces=3
    scene.cycles.diffuse_bounces=2
    scene.cycles.use_denoising=False
    scene.world.use_nodes=True
    scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.72,.8,1,1)
    scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.2
    for x in [-6,6]:
        for y in [-6,6]:
            data=bpy.data.lights.new('Skylight area','AREA')
            data.energy=450; data.shape='DISK'; data.size=8
            lamp=bpy.data.objects.new('Skylight area',data)
            scene.collection.objects.link(lamp); lamp.location=(x,y,6.6)
    # Warm station strips provide local variation and workbench contact shadows.
    for root in stations:
        data=bpy.data.lights.new('Station task light','AREA')
        data.energy=50; data.shape='RECTANGLE'; data.size=4.8; data.size_y=.3
        data.color=(1,.86,.64)
        lamp=bpy.data.objects.new('Station task light',data)
        scene.collection.objects.link(lamp); lamp.parent=root; lamp.location=(0,.9,3.1)
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'training_hub_authoring.blend'))
    scene.render.bake.use_pass_direct=True
    scene.render.bake.use_pass_indirect=True
    scene.render.bake.use_pass_color=True
    scene.render.bake.margin=12
    # Bake every target before replacing any shader; other objects still provide
    # physically diffuse bounce illumination during all bakes.
    baked=[]
    for key,mat in M.items():
        if key in ['light','sky','screen']:
            continue
        objects=[o for o in scene.objects if o.type=='MESH' and len(o.data.materials) and o.data.materials[0]==mat]
        for o in objects:
            bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
            bpy.context.view_layer.objects.active=o
            bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015)
            bpy.ops.object.mode_set(mode='OBJECT')
            size=2048 if key in ['concrete','wall','steel','wood'] else 1024
            image=bpy.data.images.new('Baked_'+key,width=size,height=size,alpha=False)
            image.colorspace_settings.name='sRGB'
            node=mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image=image
            mat.node_tree.nodes.active=node
            # Metallic surfaces have no meaningful diffuse colour at metallic=1.
            # Bake diffuse shading for the scenery's deliberately non-reflective
            # mobile approximation, retaining metallic originals in authoring file.
            mat.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0
            print('BAKING',key,size,flush=True)
            bpy.ops.object.bake(type='DIFFUSE')
            image.filepath_raw=str(output/('baked_'+key+'.png')); image.file_format='PNG'; image.save(); image.pack()
            baked.append((mat,image))
    for mat,image in baked:
        image=denoise_atlas(image,output/(image.name+'_denoised.png'))
        nodes=mat.node_tree.nodes; nodes.clear()
        tex=nodes.new('ShaderNodeTexImage'); tex.image=image
        dest=nodes.new('ShaderNodeOutputMaterial')
        # A colour socket wired directly to Surface is the Blender glTF exporter's
        # explicit KHR_materials_unlit pattern (plain Emission exports lit PBR).
        mat.node_tree.links.new(tex.outputs['Color'],dest.inputs['Surface'])

bpy.ops.wm.save_as_mainfile(filepath=str(output/'training_hub.blend'))
bpy.ops.export_scene.gltf(filepath=str(output/'training_hub.glb'), export_format='GLB',
    export_cameras=False, export_lights=False, export_animations=False)
triangles=sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH')
report={'stage':'four-bay architecture prototype', 'blender':bpy.app.version_string,
        'mesh_objects':sum(o.type=='MESH' for o in scene.objects),
        'polygons_before_triangulation':triangles, 'workers':0,
        'lighting':'Blender Cycles diffuse texture bake, 96 samples, 2 diffuse bounces, OIDN denoised' if args.bake else 'runtime prototype lighting; final light bake pending',
        'asset_sources':'Custom authored geometry and procedural surfaces; Blender bundled Bfont lettering',
        'textured_bake':args.bake}
(output/'architecture-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
