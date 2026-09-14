"""Portrait cosmic composition with textured galaxies and dense nebular filaments."""
import math
import random
import bpy
from setup_scene import collection,sphere,aim
from cosmic.particles import cloud
from cosmic.stars import build as starfield
from shaders.celestial_surface import galaxy_disc,rich_cloud
from shaders.cosmic_materials import planet_material,atmosphere_material
from shaders.divine_glow import emission,time_expression
from ganesha.sculpture import filament,appear

def plane(name,pos,scale,material,col,rotation=0):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[],[(0,1,2,3)])
    mesh.materials.append(material); obj=bpy.data.objects.new(name,mesh); col.objects.link(obj)
    obj.location=pos; obj.scale=scale; obj.rotation_euler.z=rotation
    return obj

def build(scene,settings,sculpture):
    t=time_expression(settings)
    if settings.enable_stars: starfield(scene,settings)
    galaxies=collection('Galaxies',scene); nebulas=collection('Nebula',scene); planets=collection('Planets',scene)
    galaxy_mat=galaxy_disc('Luminous spiral galaxy',settings)
    if settings.enable_galaxies:
        for i,(pos,scale,angle) in enumerate([
            ((-6.6,7.4,-5),(3.6,2.6,1),.55),((5.7,8.3,-7),(2.2,1.10,1),.12),
            ((6.8,5.4,-5),(1.95,1.4,1),-.5),((-4.9,-.2,-7),(1.3,.8,1),.8),
            ((4.9,-2.1,-8),(2.0,1.1,1),.2),((0,-5.75,-1.4),(5.2,1.22,1),-.05)]):
            obj=plane(f'Rich galaxy {i}',pos,scale,galaxy_mat,galaxies)
            obj.driver_add('rotation_euler',2).driver.expression=f'{angle}+{t}*.002'
            appear(obj,4,8,settings)
        for i in range(6,settings.galaxy_count):
            x=(-1 if i%2 else 1)*(5.5+(i%3)*.35)
            obj=plane(f'Rich galaxy {i}',(x,1.5-(i-6)*1.6,-10),(.70,.35,1),galaxy_mat,galaxies)
            obj.driver_add('rotation_euler',2).driver.expression=f'{i*.6}+{t}*.002'
            appear(obj,4,8,settings)
    if settings.enable_nebula:
        nebula=rich_cloud('Detailed cosmic nebula',settings)
        for i,(pos,scale,angle) in enumerate([
            ((-4,3,-7),(4.5,7,1),-.35),((4,1,-6),(4,7,1),.32),
            ((0,-3.8,-5),(6.6,3.1,1),-.12),((0,5,-10),(7,4,1),.20),
            ((-4,-6,-3),(4,2.8,1),.60),((4,-5.5,-4),(4,2.4,1),-.35)]):
            obj=plane(f'Billowing nebula {i}',pos,scale,nebula,nebulas)
            obj.driver_add('rotation_euler',2).driver.expression=f'{angle}+.015*sin({t}*.032+{i})'
            appear(obj,4,8,settings)
    if settings.enable_planets:
        # Reference layout: two large lit worlds at lower left, a ringed world lower right, scattered moons.
        surface=planet_material(city_lights=40); atmosphere=atmosphere_material((.55,.68,1),1.6,11)
        worlds=[((-6.9,-3.9,0),2.1,False),((-4.3,-7.9,1.2),1.8,False),((4.3,-6.3,1),.78,True),((7.1,2.9,-1),.36,True),
            ((-6.5,.95,0),.3,False),((-6.3,-.75,0),.22,False),((-2.7,-3.95,.6),.2,False),((2.9,-4.5,.8),.13,False),
            ((5.6,-2.1,.3),.12,False),((6.4,-2.3,.2),.1,False),((-4.4,7.3,-1),.22,False),((-1.0,-8.1,1),.18,False),((4.3,-.9,.4),.1,False)]
        ring_dust=emission('Planet ring dust',(.55,.42,.3),1.2)
        for i,(pos,r,ringed) in enumerate(worlds):
            obj=sphere(f'Celestial planet {i}',pos,r,surface,planets,40,20)
            obj.driver_add('rotation_euler',1).driver.expression=f'{t}*.012+{i}'
            sphere(f'Planet atmospheric rim {i}',pos,r*1.02,atmosphere,planets,40,20)
            if ringed:
                for k in (1.45,1.55,1.66,1.8,1.95):
                    R=r*k
                    pts=[(pos[0]+R*math.cos(a),pos[1]+.22*R*math.sin(a)-.12*R*math.cos(a),pos[2]+.3*R*math.sin(a)) for a in [j*math.tau/100 for j in range(100)]]
                    filament('Saturnian dust ring',pts,ring_dust,planets,max(.004,.018*r/.67),True)
    # Thousands of real star particles hug the silhouette and spiral in space.
    energy=collection('Cosmic filaments and energy',scene); rng=random.Random(2026)
    gold=sculpture['gold']; blue=emission('Nebular silver stars',(.36,.57,1),3)
    if settings.enable_halo:
        halo=collection('Halo',scene)
        points=[]
        for i in range(450):
            a=rng.uniform(0,math.tau); r=rng.gauss(1,.03)
            points.append((2.1*r*math.cos(a),3.2+2.8*r*math.sin(a),-.7+rng.uniform(-.05,.05)))
        obj,_,_=cloud('Sacred particle corona',points,[rng.uniform(.003,.009) for _ in points],gold,halo)
        obj.driver_add('rotation_euler',2).driver.expression=f'.012*sin({t}*.035)'
        appear(obj,27,34,settings)
    if settings.enable_volumetrics:
        from shaders.nebula_shader import volume_material
        obj=sphere('Low-density surrounding volume',(0,1,-2),1,volume_material(settings),nebulas,16,8)
        obj.scale=(6,8,1.0)
    for group,material in ([(0,gold),(1,blue)] if settings.enable_particles else []):
        pts=[]; sizes=[]
        for i in range(2400 if settings.quality=='LOW' else 6000):
            a=rng.uniform(0,math.tau); height=rng.gauss(.9,2.6)
            r=2.7+.7*math.sin(height*1.4)+rng.gauss(0,.42)
            x=r*math.cos(a)
            z=-.35+1.2*math.sin(a)
            pts.append((x,height,z)); sizes.append(rng.uniform(.002,.008))
        obj,_,_=cloud(f'Divine envelope stars {group}',pts,sizes,material,energy)
        obj.driver_add('rotation_euler',1).driver.expression=f'.025*sin({t}*.06)'
        appear(obj,8,58,settings)
    # A rising river of golden stars connects the galactic lotus vortex to the seated presence.
    pts=[]; sizes=[]
    for _ in range(900 if settings.quality=='LOW' else 2200):
        u=rng.random()**.8; a=rng.uniform(0,math.tau)+u*9
        r=.05+.34*(1-u)**2.2+abs(rng.gauss(0,.035))
        pts.append((r*math.cos(a)+.10*math.sin(u*8),-5.75+u*2.55,.6*r*math.sin(a)))
        sizes.append(rng.uniform(.004,.013)*(1.4-u*.6))
    obj,_,_=cloud('Ascending creation energy',pts,sizes,gold,energy)
    # Object origin sits on the stream axis, so the river swirls in place rather than orbiting the scene origin.
    obj.location=(0,0,.65)
    obj.driver_add('rotation_euler',1).driver.expression=f'.35*sin({t}*.4)'
    appear(obj,4,8,settings)
    for i in range(2):
        pts=[(.012*math.cos(u*20+i*3)+.10*math.sin(u*8),-5.75+u*2.55,.65) for u in [j/59 for j in range(60)]]
        obj=filament('Ascending creation core',pts,sculpture['white'],energy,.006-.002*i); appear(obj,4,8,settings)
    core=sphere('Galactic lotus vortex core',(0,-5.72,-.9),.2,sculpture['white'],energy,24,12)
    core.scale=(1.6,.45,1); appear(core,4,8,settings)
    # Sparse four-point star glints: geometric light accents, not sprites.
    for i in range(18):
        x=rng.uniform(-5.6,5.6); y=rng.uniform(-6.1,6.5); z=rng.uniform(-1,1)
        length=rng.uniform(.025,.095)
        for dx,dy in ((length,0),(0,length*1.4)):
            obj=filament('Stellar diffraction glint',[(x-dx,y-dy,z),(x,y,z+.015),(x+dx,y+dy,z)],sculpture['white'],energy,.0015)
            appear(obj,8,58,settings)
    return {'galaxies':galaxies,'nebula':nebulas,'energy':energy}
