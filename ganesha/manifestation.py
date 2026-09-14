import math
import bpy
from setup_scene import collection,sphere
from ganesha.depth_mapper import map_path
from ganesha.curve_builder import build_curve,trim_group
from ganesha.materials import build_materials
from animation.timeline import schedule
from animation.stroke_animator import animate_stroke,animate_tip
from shaders.divine_glow import time_expression

def build(scene,data,settings):
    coords={p.id:map_path(p,data,settings) for p in data.paths}
    return build_strokes(scene,data.paths,coords,settings)

def build_strokes(scene,paths,coords,settings,name='Ganesha strokes',tip_radius=.037):
    """Shared progressive-stroke engine: 2D vector art and 3D sculptural contours both use it."""
    col=collection(name,scene)
    mats=build_materials(settings); group=trim_group(settings)
    slots=schedule(paths); objects=[]
    for i,slot in enumerate(slots):
        obj=build_curve(slot.path,coords[slot.path.id],group,mats['gold'][i%4],col,settings)
        animate_stroke(obj,slot,settings); objects.append(obj)
    tip=build_tip(scene,mats,settings,tip_radius)
    animate_tip(tip,slots,coords,settings)
    return {'strokes':objects,'tip':tip,'materials':mats,'coordinates':coords,'slots':slots}

def build_tip(scene,mats,settings,radius=.037):
    tip_col=collection('Divine drawing tip',scene)
    tip=bpy.data.objects.new('Active drawing point',None); tip_col.objects.link(tip)
    core=sphere('White-hot tip core',(0,0,0),radius,mats['core'],tip_col)
    core.parent=tip
    t=time_expression(settings)
    for axis in range(3): core.driver_add('scale',axis).driver.expression=f'1+.08*sin({t}*3)'
    # Small satellites provide a halo without obscuring the newly drawn line.
    k=radius/.037
    for i in range(7):
        moon=sphere('Tip orbit',(0,0,0),.008*k,mats['tip_gold'],tip_col,8,4)
        moon.parent=tip
        moon.driver_add('location',0).driver.expression=f'{.08*k:.4f}*cos({t}*1.5+{i*math.tau/7})'
        moon.driver_add('location',1).driver.expression=f'{.08*k:.4f}*sin({t}*1.5+{i*math.tau/7})'
        moon.driver_add('location',2).driver.expression=f'{.04*k:.4f}*sin({t}+{i})'
    return tip
