"""Run in Blender via MCP. All geometry is conceptual and not to scale."""
import bpy, math, json, os
from mathutils import Vector
OUT='/home/efeai/Desktop/NasaSpaceApps/dashboard/assets/3d'
os.makedirs(OUT,exist_ok=True)
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.5
 return m
navy=mat('Cabin panels',(.13,.22,.33)); silver=mat('Equipment',(.48,.61,.69)); orange=mat('Overheating source',(.98,.34,.10)); cyan=mat('Ventilation / light',(.05,.77,.84)); smoke=mat('Illustrative smoke particles',(.85,.72,.51)); green=mat('Sensing surface',(.35,.85,.48))
def box(name,pos,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o

def sphere(name,pos,r,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=r,location=pos);o=bpy.context.object;o.name=name;o.data.materials.append(m);return o

def line(name,a,b,r,m):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o

def arrow(a,b):
 line('Ventilation guide — conceptual',a,b,.025,cyan);d=Vector(b)-Vector(a)
 bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=.10,radius2=0,depth=.25,location=b);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(cyan)

def new(name):
 s=bpy.data.scenes.new(name);bpy.context.window.scene=s
 s.world=bpy.data.worlds.new(name+' world');s.world.color=(.16,.16,.16)
 return s

def finish(s,key):
 objects=[o for o in s.objects if o.type=='MESH']; points=[]; faces=[]
 for o in objects:
  mesh=o.data; mesh.calc_loop_triangles();base=len(points);points.extend([list(o.matrix_world@v.co) for v in mesh.vertices]);c=list(o.data.materials[0].diffuse_color[:3])
  faces.extend([[base+i for i in t.vertices]+[c] for t in mesh.loop_triangles])
 payload={'name':s.name,'conceptual':True,'scale':'arbitrary illustration units','vertices':points,'faces':faces}
 with open(OUT+'/'+key+'.json','w') as f:json.dump(payload,f,separators=(',',':'))
 for o in s.objects:o.select_set(o.type=='MESH')
 bpy.ops.export_scene.gltf(filepath=OUT+'/'+key+'.glb',use_selection=True,use_active_scene=True,export_cameras=False,export_lights=False)
 bpy.ops.object.camera_add(location=(7,-10,8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.2;s.camera=cam
 try:s.render.engine='BLENDER_WORKBENCH'
 except TypeError:pass
 s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD'
 s.render.resolution_x=1100;s.render.resolution_y=740;s.render.resolution_percentage=100;s.render.filepath=OUT+'/'+key+'.png';s.render.image_settings.file_format='PNG'
 bpy.ops.render.render(write_still=True)
 print(key,len(objects),len(points),len(faces))

s=new('01 Cabin transport — conceptual')
box('Cabin floor',(0,0,-.15),(6,3.6,.16),navy);box('Rear cabin wall',(0,1.8,1.05),(6,.13,2.4),navy)
for x in [-2.4,-1.2,0,1.2,2.4]:box('Wall panel',(x,1.70,1.05),(1.1,.05,1.8),silver)
box('Equipment housing',(-2,0,.3),(.9,1,.65),silver);box('Overheated material — no flame',(-2,0,.7),(.5,.5,.12),orange)
box('Return vent',(2.4,1.45,1.2),(1,.20,.8),silver)
for x in range(7):box('Vent grille',(2.0+x*.13,1.29,1.2),(.035,.06,.66),navy)
box('Detector before return',(2.35,.9,1.2),(.55,.35,.36),green)
for i in range(22):
 t=i/21;sphere('Smoke marker',(-1.85+4.2*t,.1+.8*t+.16*math.sin(i*2),.85+.35*t+.16*math.cos(i)),.055,smoke)
for y in [-.9,0,.7]:arrow((-1.4,y,.5),(.9,y+.4,.5))
finish(s,'cabin_transport')
s=new('02 Optical sensing — conceptual cutaway')
box('Detector base',(0,0,0),(4,3,.2),navy);box('Rear housing',(0,1.4,.65),(4,.18,1.4),silver)
box('Emitter',(-1.6,0,.5),(.45,.55,.65),cyan);box('Forward receiver',(1.6,0,.5),(.45,.7,.65),green)
line('Incident light — schematic',(-1.4,0,.65),(0,0,.65),.035,cyan);line('Forward scattered light — schematic',(0,0,.65),(1.4,0,.65),.025,green)
sphere('Illustrative aerosol',(0,0,.65),.18,smoke)
for i in range(9):sphere('Aerosol marker',(-.85+i*.22,.5*math.sin(i*2),.55+.3*math.cos(i)),.055,smoke)
arrow((-1,-1.05,.5),(1,-1.05,.5));finish(s,'optical_detector')
s=new('03 Smoke aging — conceptual experiment chain')
box('Experiment support',(0,0,-.2),(6,2.7,.2),navy)
box('Heated sample chamber',(-2,0,.4),(1,1.2,1),silver);box('Sample',(-2,-.2,.97),(.5,.5,.1),orange)
box('Aging chamber cutaway',(0,.6,.8),(1.8,.1,1.8),silver);box('Aging chamber floor',(0,0,0),(1.8,1.3,.1),silver)
box('Diagnostics block',(2.2,0,.6),(1.1,1.2,1.2),green)
line('Transfer tube',(-1.5,0,.5),(-.9,0,.5),.10,cyan);line('Transfer tube',(.9,0,.5),(1.65,0,.5),.10,cyan)
for i in range(18):sphere('Illustrative aged aerosol',(.65*math.sin(i*2),.42*math.cos(i*3),.25+(i%5)*.26),.06+(i%3)*.025,smoke)
arrow((-2,-1,.25),(2,-1,.25));finish(s,'aging_chamber')
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/qk_norm_concept_models.blend')
print('Saved all conceptual assets')
