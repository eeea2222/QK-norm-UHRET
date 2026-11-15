"""Original metre-unit cutaway combustion chamber; illustrative flame, not CFD."""
import bpy, math, random
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.unit_settings.system='METRIC'
s.render.engine='CYCLES';s.cycles.samples=24
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Space laboratory');s.world.color=(.015,.022,.03)
def mat(name,c,metal=0,rough=.4,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
 return m
steel=mat('Brushed titanium',(.26,.32,.36),.85,.26)
dark=mat('Graphite panels',(.025,.042,.05),.6,.32)
gold=mat('Copper fittings',(.53,.28,.09),.8,.25)
blue=mat('Status light',(.12,.6,.7),.2,.3,3)
def cube(name,loc,scale,m,bevel=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(m)
 if bevel:mod=o.modifiers.new('Machined edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,r,depth,m,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name;o.data.materials.append(m);mod=o.modifiers.new('Bevel','BEVEL');mod.width=.008;mod.segments=2
 return o
# Open front and right cutaway expose the experimental volume.
cube('Floor',(0,0,-.08),(2.8,2.1,.16),dark)
cube('Back wall',(0,.99,.85),(2.8,.1,1.8),dark)
cube('Left wall',(-1.35,0,.85),(.1,2.1,1.8),steel)
for x in [-1.25,1.25]:
 for y in [-.92,.9]:
  cube('Structural rail',(x,y,.83),(.075,.075,1.85),steel)
for z in [.02,1.7]:
 for y in [-.92,.9]:cube('Horizontal rail',(0,y,z),(2.6,.075,.075),steel)
for x in [-1.25,1.25]:
 for z in [.02,1.7]:cube('Depth rail',(x,0,z),(.075,1.9,.075),steel)
# Fasteners and vent slats.
for x in [-1.18,-.6,0,.6,1.18]:
 for z in [.18,1.5]:cyl('Panel bolt',(x,.925,z),.026,.035,steel,(math.pi/2,0,0))
for j in range(16):cube('Return vent slat',(.62+j*.033,.915,.8),(.012,.045,.6),steel,.002)
for j in range(10):cube('Wall seam',(-.9+j*.16,.92,1.35),(.002,.015,.22),steel,.001)
cube('Sample cradle',(0,0,.28),(.75,.5,.1),steel)
for x in [-.25,.25]:cyl('Ceramic holder',(x,0,.44),.035,.3,gold)
sample=cube('Polymer specimen',(0,0,.61),(.55,.24,.045),mat('Polymer',(.17,.12,.08),.05,.6))
# Irregular rounded flame shell, volume noise and blue emission.
volume=bpy.data.materials.new('Blue flame volume');volume.use_nodes=True
n=volume.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');v=n.new('ShaderNodeVolumePrincipled')
v.inputs['Color'].default_value=(.08,.22,.5,1);v.inputs['Emission Color'].default_value=(.055,.27,1,1);v.inputs['Emission Strength'].default_value=1.8
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=4
mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';mult.inputs[1].default_value=2
volume.node_tree.links.new(noise.outputs['Fac'],mult.inputs[0]);volume.node_tree.links.new(mult.outputs[0],v.inputs['Density']);volume.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,location=(0,0,.86))
flame=bpy.context.object;flame.name='Illustrative low-momentum flame';flame.scale=(.39,.3,.29);flame.data.materials.append(volume)
core=mat('Amber flame filaments',(1,.22,.025),0,.5,5)
random.seed(4)
for j in range(11):
 curve=bpy.data.curves.new('Flame filament','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=3
 spline=curve.splines.new('BEZIER');spline.bezier_points.add(10)
 a=j*math.tau/11
 for k,p in enumerate(spline.bezier_points):
  q=k/10;radius=.12+.08*math.sin(q*math.pi)
  p.co=(radius*math.cos(a+q),radius*math.sin(a+q),.64+q*.29);p.handle_left_type=p.handle_right_type='AUTO'
 o=bpy.data.objects.new('Illustrative glowing filament',curve);s.collection.objects.link(o);curve.materials.append(core)
# Camera instrument, cables and control unit.
cyl('Optical lens housing',(.97,-.25,.87),.15,.32,dark,(0,math.pi/2,0))
cyl('Optical glass',(.79,-.25,.87),.12,.025,mat('Lens',(.025,.12,.19),.9,.1),(0,math.pi/2,0))
cube('Electronics',(.75,.42,.31),(.66,.4,.38),steel)
for j in range(4):cube('Indicator',(.51+j*.1,.205,.38),(.045,.015,.025),blue,.005)
for j in range(5):
 curve=bpy.data.curves.new('Cable','CURVE');curve.dimensions='3D';curve.bevel_depth=.012;curve.bevel_resolution=3
 sp=curve.splines.new('BEZIER');sp.bezier_points.add(3)
 for p,co in zip(sp.bezier_points,[(.85,.3,.2),(.65,.6,.15),(-.3,.5,.1),(-1.1,.65,.25+j*.045)]):p.co=co;p.handle_left_type=p.handle_right_type='AUTO'
 o=bpy.data.objects.new('Instrument cable',curve);s.collection.objects.link(o);curve.materials.append(gold if j%2 else dark)
def area(loc,power,color,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
area((1,-2,4),650,(.62,.81,1),4);area((-2,1,3),900,(.2,.6,1),3);area((2,2,2),1000,(1,.56,.25),2)
bpy.ops.object.light_add(type='POINT',location=(0,0,.9));bpy.context.object.data.energy=12;bpy.context.object.data.color=(.1,.35,1)
bpy.ops.object.camera_add(location=(3.35,-4.8,2.9));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;s.camera=cam
s.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/microgravity_chamber.blend'))
s.render.filepath=str(root/'assets/flame_3d.png')
bpy.ops.render.render(write_still=True)
print('3D_RENDER_COMPLETE')
