"""Create a separate scene; never delete objects from the user's scene."""
import bpy
from mathutils import Vector
from shaders.divine_glow import setup_glow

def collection(name,scene):
    col=bpy.data.collections.new(name)
    scene.collection.children.link(col)
    return col

def aim(obj,target=(0,0,0)):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def sphere(name,location,radius,material,col,segments=16,rings=8):
    # Operators use the active scene; relink only the newly-created object.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=radius,location=location)
    obj=bpy.context.object; obj.name=name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(material)
    for p in obj.data.polygons: p.use_smooth=True
    return obj

def setup(settings):
    if bpy.app.version < (4,2,0) or bpy.app.version >= (5,0,0):
        raise RuntimeError(f'Blender 4.2-4.5 required; found {bpy.app.version_string}')
    scene=bpy.data.scenes.new('Brahmand - Divine Ganesha')
    bpy.context.window.scene=scene
    scene.render.engine='BLENDER_EEVEE_NEXT'
    scene.eevee.taa_render_samples=settings.samples
    scene.eevee.taa_samples=max(8,settings.samples//2)
    scene.eevee.use_raytracing=False
    scene.render.resolution_x=settings.render_width
    scene.render.resolution_y=settings.render_height
    scene.render.resolution_percentage=100
    scene.render.fps=settings.fps
    scene.render.image_settings.file_format='PNG'
    if hasattr(scene.render,'compositor_device'): scene.render.compositor_device='GPU'
    scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.world=bpy.data.worlds.new('Infinite midnight')
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value=(.0003,.0005,.0014,1)
    bg.inputs['Strength'].default_value=.12
    camera_data=bpy.data.cameras.new('Cinematic 50mm')
    camera=bpy.data.objects.new('Cinematic Camera',camera_data)
    scene.collection.objects.link(camera)
    camera.location=(0,.45,30); aim(camera,(0,.45,0))
    camera_data.lens=50
    camera_data.clip_end=250
    scene.camera=camera
    scene.render.fps_base=1
    scene.frame_start=1
    from animation.timeline import frame
    scene.frame_end=round(frame(65+settings.final_hold_seconds,settings))
    setup_glow(scene,settings)
    return scene
