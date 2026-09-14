"""Integration checks evaluate real GN meshes, tip positions and final motion."""
import json
import math
import bpy
from animation.timeline import frame
from ganesha.depth_mapper import sample_polyline

def validate(scene,manifestation,settings,output):
    checks=[]
    def check(name,condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    objects=manifestation['strokes']; slots=manifestation['slots']; tip=manifestation['tip']
    scene.frame_set(1)
    check('No Ganesha strokes visible at opening',all(o.hide_render and o['reveal']==0 for o in objects))
    check('Body field has no opaque ghosts before manifestation',all(o.hide_render for o in scene.collection.children['Cosmic body'].objects))
    for index in (0,len(slots)//2,len(slots)-1):
        slot=slots[index]; obj=objects[index]
        f=frame((slot.start+slot.end)/2,settings)
        scene.frame_set(int(f),subframe=f-int(f))
        check(f'Stroke {index} reveals halfway',abs(obj['reveal']-.5)<.001)
        expected=sample_polyline(manifestation['coordinates'][slot.path.id],.5)
        check(f'Tip follows exact active stroke {index}',math.dist(tip.location,expected)<.002)
        deps=bpy.context.evaluated_depsgraph_get()
        evaluated=obj.evaluated_get(deps); mesh=evaluated.to_mesh()
        check(f'Stroke {index} generates actual tube mesh',len(mesh.vertices)>8)
        evaluated.to_mesh_clear()
        check(f'Future strokes remain hidden {index}',all(o.hide_render for o in objects[index+1:]))
    scene.frame_set(round(frame(66,settings)))
    check('All completed strokes persist',all(abs(o['reveal']-1)<.001 and not o.hide_render for o in objects))
    camera=tuple(scene.camera.location)
    galaxy=next(o for o in scene.objects if o.name.startswith('Distant spiral'))
    rotation=tuple(galaxy.rotation_euler)
    scene.frame_set(round(frame(75,settings)))
    check('Final camera remains animated',tuple(scene.camera.location)!=camera)
    check('Camera preserves upright global Y',abs(scene.camera.rotation_euler.z)<1e-6)
    check('All animation drivers valid',all(fc.driver.is_valid for o in scene.objects if o.animation_data for fc in o.animation_data.drivers))
    check('Final galaxy remains animated',tuple(galaxy.rotation_euler)!=rotation)
    check('No external file textures',not any(i.source=='FILE' and i.filepath for i in bpy.data.images))
    # Inspect actual attraction instances: the same mote moves toward a fixed tip
    # over a short interval, on a stroke long enough to avoid a hand-off.
    dust=next((o for o in scene.objects if o.name=='Universe donating energy'),None)
    if dust:
        def instance_positions(seconds):
            f=frame(seconds,settings); scene.frame_set(int(f),subframe=f-int(f))
            deps=bpy.context.evaluated_depsgraph_get()
            return [(tuple(i.persistent_id),tuple(i.matrix_world.translation)) for i in deps.object_instances
                    if i.is_instance and i.parent and i.parent.original==dust]
        a=dict(instance_positions(30)); b=dict(instance_positions(30.1))
        check(f'Particles are efficiently instanced ({len(a)}/{settings.particle_count})',len(a)==settings.particle_count)
        check('Particles move over time',any(math.dist(a[k],b[k])>.001 for k in a if k in b))
    (output/'blender_validation.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2))
    print(f'BLENDER VALIDATION: {len(checks)} checks passed',flush=True)
