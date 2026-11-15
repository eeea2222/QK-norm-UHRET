"""A narrated illustrative event, not a reconstruction of a recorded BASS run."""
import bpy, math, random
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/microgravity_chamber.blend'))
s=bpy.context.scene;s.render.resolution_x=1280;s.render.resolution_y=720
s.cycles.samples=8;s.cycles.use_denoising=True
s.frame_start=1;s.frame_end=37
flame=bpy.data.objects['Illustrative low-momentum flame']
flame_material=flame.data.materials[0]
volume=flame_material.node_tree.nodes.get('Principled Volume')
noise=next(n for n in flame_material.node_tree.nodes if n.type=='TEX_NOISE')
noise.noise_dimensions='4D'
# Break the perfect spherical surface into a softly irregular envelope.
texture=bpy.data.textures.new('Evolving flame structure',type='CLOUDS');texture.noise_scale=.2
modifier=flame.modifiers.new('Irregular flame envelope','DISPLACE');modifier.texture=texture;modifier.strength=.12;modifier.mid_level=.5
filaments=[o for o in s.objects if o.name.startswith('Illustrative glowing filament')]
for o in filaments:o.hide_render=True
# Replace decorative filaments with an irregular hot luminous inner volume.
inner=flame.copy();inner.data=flame.data.copy();s.collection.objects.link(inner);inner.name='Hot inner flame'
m=flame_material.copy();inner.data.materials.clear();inner.data.materials.append(m)
inner_volume=m.node_tree.nodes.get('Principled Volume')
inner_volume.inputs['Emission Color'].default_value=(1,.12,.008,1)
emission_controls=[]
for material,v in [(flame_material,volume),(m,inner_volume)]:
 nodes=material.node_tree.nodes;links=material.node_tree.links
 coord=nodes.new('ShaderNodeTexCoord')
 distance=nodes.new('ShaderNodeVectorMath');distance.operation='DISTANCE';distance.inputs[1].default_value=(.5,.5,.5)
 links.new(coord.outputs['Generated'],distance.inputs[0])
 subtract=nodes.new('ShaderNodeMath');subtract.operation='SUBTRACT';subtract.inputs[1].default_value=.40;links.new(distance.outputs['Value'],subtract.inputs[0])
 absolute=nodes.new('ShaderNodeMath');absolute.operation='ABSOLUTE';links.new(subtract.outputs[0],absolute.inputs[0])
 shell=nodes.new('ShaderNodeMath');shell.operation='LESS_THAN';shell.inputs[1].default_value=.045;links.new(absolute.outputs[0],shell.inputs[0])
 turbulence=next(n for n in nodes if n.type=='TEX_NOISE')
 product=nodes.new('ShaderNodeMath');product.operation='MULTIPLY';links.new(shell.outputs[0],product.inputs[0]);links.new(turbulence.outputs['Fac'],product.inputs[1])
 density=nodes.new('ShaderNodeMath');density.operation='MULTIPLY';density.inputs[1].default_value=.4;links.new(product.outputs[0],density.inputs[0]);links.new(density.outputs[0],v.inputs['Density'])
 emission=nodes.new('ShaderNodeMath');emission.operation='MULTIPLY';emission.inputs[1].default_value=4;links.new(product.outputs[0],emission.inputs[0]);links.new(emission.outputs[0],v.inputs['Emission Strength'])
 emission_controls.append(emission)
# Small glowing heating ring below the sample; this is a conceptual heat source.
heat_mat=bpy.data.materials.new('Heating ring glow');heat_mat.use_nodes=True
bsdf=heat_mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.1,.02,.005,1);bsdf.inputs['Emission Color'].default_value=(1,.08,.005,1)
bpy.ops.mesh.primitive_torus_add(major_radius=.19,minor_radius=.009,location=(0,0,.59))
heater=bpy.context.object;heater.name='Conceptual heat source';heater.data.materials.append(heat_mat)
smoke_mat=bpy.data.materials.new('Aerosol illustration');smoke_mat.use_nodes=True
nodes=smoke_mat.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');sv=nodes.new('ShaderNodeVolumePrincipled');sv.inputs['Color'].default_value=(.3,.36,.42,1);sv.inputs['Density'].default_value=.6
smoke_mat.node_tree.links.new(sv.outputs['Volume'],output.inputs['Volume'])
smoke=[]
for j in range(14):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1)
 o=bpy.context.object;o.name=f'Illustrative aerosol puff {j}';o.data.materials.append(smoke_mat);smoke.append(o)
def smooth(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
sample=bpy.data.objects['Polymer specimen'];samplemat=sample.data.materials[0].node_tree.nodes.get('Principled BSDF')
cam=s.camera
for frame in range(1,38):
 p=(frame-1)/36
 s.frame_set(frame)
 growth=smooth((p-.08)/.2)
 decay=1-smooth((p-.72)/.23)
 size=growth*decay
 fluctuation=1+.045*math.sin(p*math.tau*5)
 flame.scale=(.39*size*fluctuation+.001,.30*size+.001,.29*size+.001)
 flame.location=(.035*math.sin(p*9)*size,0,.632+.23*size)
 flame.keyframe_insert(data_path='scale');flame.keyframe_insert(data_path='location')
 inner.location=flame.location;inner.scale=(.24*size+.001,.18*size+.001,.17*size+.001)
 inner.keyframe_insert(data_path='scale');inner.keyframe_insert(data_path='location')
 for e,strength in zip(emission_controls,[5,9]):
  e.inputs[1].default_value=strength*size
  e.inputs[1].keyframe_insert(data_path='default_value')
 noise.inputs['W'].default_value=p*2;noise.inputs['W'].keyframe_insert(data_path='default_value')
 heat=1-smooth((p-.65)/.05)
 bsdf.inputs['Emission Strength'].default_value=4*heat
 bsdf.inputs['Emission Strength'].keyframe_insert(data_path='default_value')
 c=.15-.1*smooth(p/.7);samplemat.inputs['Base Color'].default_value=(c,c*.7,c*.4,1)
 samplemat.inputs['Base Color'].keyframe_insert(data_path='default_value')
 for j,o in enumerate(smoke):
  q=(p*1.8+j/14)%1
  active=smooth((p-.25)/.15)*(1-smooth((p-.92)/.08))
  r=.065*active*math.sin(q*math.pi)
  o.scale=(r*1.4+.0001,r+.0001,r*.65+.0001)
  o.location=(q*.85, q*.78,.86+.065*math.sin(q*math.pi)+.035*math.sin(j*3))
  o.keyframe_insert(data_path='scale');o.keyframe_insert(data_path='location')
 degrees=-59+20*smooth(p)
 radius=6.2-1.1*math.sin(p*math.pi)
 cam.location=(radius*math.cos(math.radians(degrees)),radius*math.sin(math.radians(degrees)),2.8-.45*math.sin(p*math.pi))
 cam.rotation_euler=(Vector((0,0,.82))-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.keyframe_insert(data_path='location');cam.keyframe_insert(data_path='rotation_euler')
folder=root/'assets/event_frames';folder.mkdir(exist_ok=True)
s.render.image_settings.file_format='PNG';s.render.filepath=str(folder/'event_')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/microgravity_event.blend'))
bpy.ops.render.render(animation=True)
print('EVENT_RENDER_COMPLETE')
