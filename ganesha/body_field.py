"""Soft anatomical cloud lobes, with internal stars masked to those lobes."""
import random
import math
from setup_scene import collection,sphere
from shaders.nebula_shader import nebula_material
from shaders.divine_glow import emission,driver,time_expression
from cosmic.particles import cloud
from cosmic.galaxies import galaxy

# World XY center, ellipse radii. Fields sit behind the energy curves.
LOBES=((0,2.4,1.43,1.12),(0,-.65,1.4,1.5),(-1.99,2.25,.57,.90),
       (1.99,2.25,.57,.90),(-1.6,-2.6,1.1,.5),(1.6,-2.6,1.1,.5),
       (-2.23,.62,.48,.8),(2.23,.62,.48,.8),(0,.96,.42,.78),(.49,.50,.53,.38))

def build(scene,settings):
    col=collection('Cosmic body',scene)
    mat=nebula_material('Cosmic Blue Body',(.10,.075,.28),settings,body=True)
    for i,(x,y,rx,ry) in enumerate(LOBES):
        obj=sphere(f'Ethereal body field {i}',(x,y,-.30),1,mat,col,24,12)
        obj.scale=(rx,ry,.36)
    rng=random.Random(settings.seed+40); points=[]; radii=[]
    for _ in range(320 if settings.quality=='LOW' else 750):
        x,y,rx,ry=rng.choice(LOBES)
        a=rng.random()*math.tau; r=math.sqrt(rng.random())*.86
        points.append((x+rx*r*math.cos(a),y+ry*r*math.sin(a),rng.uniform(-.12,.03)))
        radii.append(rng.uniform(.005,.013))
    star=emission('Body star emission',(.55,.68,1),1)
    node=next(n for n in star.node_tree.nodes if n.type=='EMISSION')
    t=time_expression(settings)
    driver(node.inputs['Strength'],f'min(1,max(0,({t}-58)/7))*(.8+.2*sin({t}*.65))')
    obj,_,_=cloud('Interior star field',points,radii,star,col)
    obj.driver_add('location',2).driver.expression=f'.015*sin({t}*.3)'
    galaxy('Galaxy within the heart',(.15,-.60,.02),.62,settings,col,31,True)
    galaxy('Galaxy within the forehead',(.05,2.90,.02),.3,settings,col,32,True)
    from animation.timeline import frame
    for obj in col.objects:
        for f,hidden in ((1,True),(frame(58,settings),False)):
            obj.hide_render=hidden; obj.keyframe_insert(data_path='hide_render',frame=f)
            obj.hide_viewport=hidden; obj.keyframe_insert(data_path='hide_viewport',frame=f)
    return col
