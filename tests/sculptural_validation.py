"""Actual mesh, shader, phase and greeting checks for the new default style."""
import json
import math
import bpy
from animation.timeline import frame
from ganesha.depth_mapper import sample_polyline

def validate(scene,sculpture,settings,output):
    checks=[]
    def check(name,value):
        if not value: raise AssertionError(name)
        checks.append(name)
    bodies=sculpture['anatomy']
    scene.frame_set(1)
    check('All sculptural anatomy hidden in cosmic void',all(o.hide_render for o in bodies))
    text=scene.objects.get('Happy Ganesh Chaturthi 2026')
    if settings.show_greeting:
        check('Greeting exact wording',text.data.body=='Happy Ganesh Chaturthi 2026')
        check('Greeting hidden before manifestation',text.hide_render)
    else:
        check('Reference composition has no greeting text',text is None)
    check('Portrait composition',scene.render.resolution_y>scene.render.resolution_x)
    drawing=sculpture.get('manifestation')
    if settings.enable_particles:
        strokes=drawing['strokes']; slots=drawing['slots']; tip=drawing['tip']
        check('Contour strokes hidden in cosmic void',all(o.hide_render and o['reveal']==0 for o in strokes))
        for index in (0,len(slots)//2,len(slots)-1):
            slot=slots[index]; obj=strokes[index]
            f=frame((slot.start+slot.end)/2,settings); scene.frame_set(int(f),subframe=f-int(f))
            check(f'Contour stroke {index} ({obj["category"]}) reveals halfway',abs(obj['reveal']-.5)<.001)
            expected=sample_polyline(drawing['coordinates'][slot.path.id],.5)
            check(f'Drawing tip follows active contour {index}',math.dist(tip.location,expected)<.002)
            check(f'Future contours remain hidden {index}',all(o.hide_render for o in strokes[index+1:]))
        order=[s.path.category for s in slots]
        check('Crown is drawn first and feet last',order[0]=='crown' and order[-1]=='feet')
        check('Drawing tip lives inside the composition',tip.parent and tip.parent.parent is None and tip.parent.name.startswith('Reference composition'))
    scene.frame_set(round(frame(18,settings)))
    check('Crown visible during head assembly',not scene.objects['Unified celestial crown'].hide_render)
    check('Legs remain hidden before their phase',all(o.hide_render for o in bodies if o.data.materials[0].name=='Celestial legs'))
    scene.frame_set(round(frame(66,settings)))
    check('Full mesh anatomy visible in final form',all(not o.hide_render for o in bodies))
    if settings.show_greeting: check('Greeting visible with completed form',not text.hide_render)
    if drawing: check('All golden contours persist after manifestation',all(abs(o['reveal']-1)<.001 and not o.hide_render for o in drawing['strokes']))
    head=scene.objects['Continuous head and trunk']
    check('Continuous head/trunk is actual sculpted mesh',head.type=='MESH' and len(head.data.vertices)>5000)
    check('Physical fingers and palm are unified',scene.objects['Continuous blessing hand'].type=='MESH')
    check('Body surfaces use procedural shading',all(o.data.materials[0].use_nodes for o in bodies))
    check('No flat vector line-art collection in default scene','Ganesha strokes' not in scene.collection.children)
    camera=tuple(scene.camera.location)
    galaxy=scene.objects['Rich galaxy 0']; orientation=tuple(galaxy.rotation_euler)
    shader=bpy.data.materials['Celestial torso'].node_tree
    noise=next(n for n in shader.nodes if n.type=='TEX_NOISE'); before=noise.inputs['W'].default_value
    scene.frame_set(round(frame(75,settings)))
    check('Final camera motion continues',tuple(scene.camera.location)!=camera)
    check('Final galaxy motion continues',tuple(galaxy.rotation_euler)!=orientation)
    check('Cosmic surface noise evolves',noise.inputs['W'].default_value!=before)
    check('No runtime image textures',not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes))
    check('Object drivers valid',all(fc.driver.is_valid for o in scene.objects if o.animation_data for fc in o.animation_data.drivers))
    (output/'sculptural_validation.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2))
    print(f'SCULPTURAL VALIDATION: {len(checks)} checks passed',flush=True)
