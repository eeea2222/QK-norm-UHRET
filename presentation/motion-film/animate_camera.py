"""Render a restrained 3D camera arc, with an explanation-timed dolly."""
import bpy, math
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/microgravity_chamber.blend'))
s=bpy.context.scene
s.render.resolution_x=1280;s.render.resolution_y=720
s.cycles.samples=8;s.cycles.use_denoising=True
cam=s.camera
s.frame_start=1;s.frame_end=37
# Keep the open front and right cutaway facing the viewer throughout the arc.
for frame,degrees,radius,height,target_height in [(1,-59,6.25,2.9,.8),(13,-52,5.6,2.65,.82),(25,-43,4.65,2.2,.86),(37,-36,5.65,2.7,.8)]:
    angle=math.radians(degrees)
    cam.location=(radius*math.cos(angle),radius*math.sin(angle),height)
    cam.rotation_euler=(Vector((0,0,target_height))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.keyframe_insert(data_path='location',frame=frame)
    cam.keyframe_insert(data_path='rotation_euler',frame=frame)
folder=root/'assets/camera_frames';folder.mkdir(exist_ok=True)
s.render.image_settings.file_format='PNG'
s.render.filepath=str(folder/'camera_')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/microgravity_camera_animation.blend'))
bpy.ops.render.render(animation=True)
print('CAMERA_SEQUENCE_COMPLETE')
