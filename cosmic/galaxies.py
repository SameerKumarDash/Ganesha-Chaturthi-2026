import math
import random
from setup_scene import collection
from cosmic.particles import cloud
from shaders.divine_glow import emission,time_expression,driver

def galaxy(name,position,radius,settings,col,seed=0,internal=False):
    rng=random.Random(settings.seed+seed)
    points=[]; sizes=[]
    count=360 if settings.quality=='LOW' else 800
    for i in range(count):
        r=radius*rng.random()**.75
        theta=(i%3)*math.tau/3+r/radius*5.8+rng.gauss(0,.20)
        points.append((r*math.cos(theta),.48*r*math.sin(theta),rng.gauss(0,.025)))
        sizes.append(rng.uniform(.007,.018)*(radius/2)**.3)
    for _ in range(count//5):
        points.append((rng.gauss(0,radius*.07),rng.gauss(0,radius*.035),rng.gauss(0,.03)))
        sizes.append(rng.uniform(.007,.017))
    mat=emission('Interior Galaxy Emission' if internal else 'Galaxy Emission',(.52,.57,.8),1 if internal else .8)
    if internal:
        emit=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
        driver(emit.inputs['Strength'],f'min(1,max(0,({time_expression(settings)}-58)/7))')
    else:
        emit=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
        driver(emit.inputs['Strength'],f'.65*(.025+.975*min(1,max(0,({time_expression(settings)}-4)/10)))')
    obj,_,_=cloud(name,points,sizes,mat,col)
    obj.location=position
    obj.driver_add('rotation_euler',2).driver.expression=f'{seed*.71}+{time_expression(settings)}*.0025'
    return obj

def build(scene,settings):
    col=collection('Galaxies',scene)
    positions=[((-11,5,-14),3.2),((10,-4,-12),2.2),((10,6,-19),2.5),((-8,-5,-14),.7),((5,7,-22),.65),((-13,-1,-20),.9)]
    for i in range(settings.galaxy_count):
        pos,radius=positions[i%len(positions)]
        galaxy(f'Distant spiral {i}',pos,radius*(1 if i<6 else .35),settings,col,i)
    return col
