import random
from setup_scene import collection
from cosmic.particles import cloud
from shaders.divine_glow import emission,driver,time_expression

def build(scene,settings):
    col=collection('Stars',scene); rng=random.Random(settings.seed)
    t=time_expression(settings)
    # Twelve independent phase groups, distributed across three depths.
    for i in range(12):
        mat=emission(f'Star Emission {i}',(.63+.025*i,.74+.015*i,1),1.6)
        emit=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
        driver(emit.inputs['Strength'],f'(1.6+.5*sin({t}*{.37+i*.047}+{i*1.91}))*(.16+.84*min(1,max(0,{t}/8)))')
        count=settings.star_count//12+(i<settings.star_count%12)
        points=[]; sizes=[]
        for _ in range(count):
            z=rng.uniform(-38,-7) if i<9 else rng.uniform(-6,2)
            points.append((rng.uniform(-25,25),rng.uniform(-16,16),z))
            sizes.append(rng.uniform(.007,.025) if i<10 else rng.uniform(.018,.042))
        obj,_,_=cloud(f'Star stratum {i}',points,sizes,mat,col)
        obj.driver_add('rotation_euler',2).driver.expression=f'.003*sin({t}*.035+{i})'
        obj.driver_add('location',0).driver.expression=f'.10*sin({t}*.025+{i})'
    return col
