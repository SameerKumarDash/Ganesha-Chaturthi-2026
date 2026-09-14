import math
import random
import bpy
from setup_scene import collection
from cosmic.particles import cloud
from shaders.divine_glow import emission,driver,time_expression

def build(scene,settings):
    col=collection('Halo',scene); t=time_expression(settings)
    mat=emission('Halo Gold',(1,.57,.22),.7)
    e=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
    driver(e.inputs['Strength'],f'.6*min(1,max(0,({t}-27)/7))*(1+.035*sin({t}*.7))')
    center=(0,2.75,-.75)
    for i,r in enumerate((2.28,2.40)):
        curve=bpy.data.curves.new('Sacred concentric ring','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.005 if i else .009; curve.bevel_resolution=2
        spline=curve.splines.new('POLY'); spline.points.add(159)
        for j,p in enumerate(spline.points):
            a=j/160*math.tau; p.co=(r*math.cos(a),r*math.sin(a),0,1)
        spline.use_cyclic_u=True
        obj=bpy.data.objects.new('Quiet sacred ring',curve); col.objects.link(obj); obj.location=center; curve.materials.append(mat)
    rng=random.Random(108)
    points=[]
    for i in range(220):
        a=rng.random()*math.tau; r=rng.gauss(2.34,.035)
        points.append((r*math.cos(a),r*math.sin(a),rng.uniform(-.04,.04)))
    obj,_,_=cloud('Halo golden motes',points,[.009]*len(points),mat,col)
    obj.location=center
    obj.driver_add('rotation_euler',2).driver.expression=f'{t}*.012'
    from animation.timeline import frame
    for obj in col.objects:
        for f,hidden in ((1,True),(frame(27,settings),False)):
            obj.hide_render=hidden; obj.keyframe_insert(data_path='hide_render',frame=f)
            obj.hide_viewport=hidden; obj.keyframe_insert(data_path='hide_viewport',frame=f)
    return col
