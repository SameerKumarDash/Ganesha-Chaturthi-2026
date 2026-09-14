"""Reference-inspired sculptural scene, now the default visual presentation."""
import math
import bpy
from setup_scene import setup,collection,aim
from ganesha.sculpture import build as build_sculpture,appear
from cosmic.rich_universe import build as build_cosmos
from animation.timeline import frame
from shaders.divine_glow import emission,driver,time_expression

def build(settings):
    scene=setup(settings)
    dimensions={'LOW':(800,960),'MEDIUM':(1200,1440),'HIGH':(1600,1920),'ULTRA':(2000,2400)}
    scene.render.resolution_x,scene.render.resolution_y=dimensions[settings.quality]
    scene.eevee.taa_render_samples=max(32,settings.samples)
    scene.camera.data.sensor_fit='VERTICAL'; scene.camera.data.sensor_height=34
    scene.camera.data.lens=50
    t=time_expression(settings)
    x=f'(.10*sin({t}*.04)+1.8*sin(max(0,{t}-65)*.025))'
    z=f'(25.4-.65*min(1,{t}/65))'
    scene.camera.driver_add('location',0).driver.expression=x
    scene.camera.driver_add('location',1).driver.expression='-.42'
    scene.camera.driver_add('location',2).driver.expression=z
    scene.camera.driver_add('rotation_euler',1).driver.expression=f'atan2({x},{z})'
    scene.camera.rotation_euler.x=0; scene.camera.rotation_euler.z=0
    scene.camera.data.dof.use_dof=False
    # Strong grazing light shapes physical facial planes and hands.
    for name,pos,color,power,size in [
        ('Sacred left key',(-4,5,5),(1,.69,.34),850,5),
        ('Celestial blue fill',(3,2,5),(.30,.49,1),420,4),
        ('Golden right rim',(4,3,-1),(1,.47,.12),1100,3),
        ('Crown halo light',(-1,6,-1),(1,.70,.33),900,3),
        ('Lower galaxy reflected light',(0,-4,3),(.32,.48,1),240,4)]:
        data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.color=color; data.shape='DISK'; data.size=size
        obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=pos; aim(obj,(0,1,.3))
    sculpture=build_sculpture(scene,settings); cosmos=build_cosmos(scene,settings,sculpture)
    if settings.enable_particles:
        from animation.surface_manifestation import build as surface_effects
        sculpture['tip']=surface_effects(scene,sculpture,settings)
    # Match the reference's broad silhouette and close portrait framing.
    root=bpy.data.objects.new('Reference composition - divine figure',None); scene.collection.objects.link(root)
    for name in ('Celestial anatomy','Sacred crown and jewelry','Living surface starlight','Divine contour strokes','Divine drawing tip'):
        col=scene.collection.children.get(name)
        if col:
            # Tip satellites stay parented to the moving tip itself.
            for child in col.objects:
                if child.parent is None: child.parent=root
    root.scale=(1.42,1.18,1.05); root.location.y=-.18
    scene['visual_style']='SCULPTURAL'
    if not settings.show_greeting:  # The reference composition carries no text.
        return scene,sculpture,cosmos
    greeting=collection('Festival greeting',scene)
    text=bpy.data.curves.new('Happy Ganesh Chaturthi 2026','FONT')
    text.body='Happy Ganesh Chaturthi 2026'; text.align_x='CENTER'; text.align_y='CENTER'
    text.size=.38; text.space_character=1.08; text.extrude=.0015; text.bevel_depth=.0006
    text.resolution_u=12
    mat=emission('Festival greeting warm gold',(1,.74,.39),1.7)
    node=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
    driver(node.inputs['Strength'],f'1.7*min(1,max(0,({t}-61)/4))')
    text.materials.append(mat)
    obj=bpy.data.objects.new('Happy Ganesh Chaturthi 2026',text); greeting.objects.link(obj)
    obj.location=(0,-7.26,2); appear(obj,61,65,settings)
    scene['greeting']='Happy Ganesh Chaturthi 2026'
    return scene,sculpture,cosmos
