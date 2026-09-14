"""Analytic Geometry Nodes attraction. Seekable and independent of playback history."""
import math
import random
import bpy
from cosmic.particles import cloud
from setup_scene import collection
from shaders.divine_glow import emission,time_expression,driver
from animation.timeline import PHASES,frame

def build(scene,tip,settings):
    col=collection('Attracted cosmic dust',scene)
    rng=random.Random(settings.seed+3)
    points=[(rng.uniform(-9,9),rng.uniform(-6,6),rng.uniform(-3,2)) for _ in range(settings.particle_count)]
    mat=emission('Golden cosmic dust',(1,.61,.23),2.2)
    obj,g,instances=cloud('Universe donating energy',points,[rng.uniform(.007,.017) for _ in points],mat,col)
    n=g.nodes; l=g.links
    def math_node(operation,a,b=None):
        node=n.new('ShaderNodeMath'); node.operation=operation
        for i,v in enumerate((a,b)):
            if v is None: continue
            if isinstance(v,(int,float)): node.inputs[i].default_value=v
            else: l.new(v,node.inputs[i])
        return node.outputs[0]
    index=n.new('GeometryNodeInputIndex')
    clock=n.new('ShaderNodeValue'); driver(clock.outputs[0],time_expression(settings))
    phase=math_node('FRACT',math_node('ADD',math_node('MULTIPLY',index.outputs[0],.6180339),math_node('MULTIPLY',clock.outputs[0],.19)))
    # Birth->accelerating convergence->small arrival flash->merge.
    weight=math_node('POWER',phase,2.3)
    pos=n.new('GeometryNodeInputPosition')
    info=n.new('GeometryNodeObjectInfo'); info.transform_space='RELATIVE'; info.inputs['Object'].default_value=tip
    subtract=n.new('ShaderNodeVectorMath'); subtract.operation='SUBTRACT'
    l.new(info.outputs['Location'],subtract.inputs[0]); l.new(pos.outputs[0],subtract.inputs[1])
    scale=n.new('ShaderNodeVectorMath'); scale.operation='SCALE'
    l.new(subtract.outputs['Vector'],scale.inputs[0]); l.new(weight,scale.inputs['Scale'])
    move=n.new('GeometryNodeSetPosition')
    inp=next(x for x in n if x.bl_idname=='NodeGroupInput')
    l.new(inp.outputs['Geometry'],move.inputs['Geometry'])
    angle=math_node('ADD',math_node('MULTIPLY',index.outputs[0],2.39996),math_node('MULTIPLY',clock.outputs[0],.8))
    amplitude=math_node('MULTIPLY',math_node('SINE',math_node('MULTIPLY',phase,math.pi)),.14)
    spiral=n.new('ShaderNodeCombineXYZ')
    l.new(math_node('MULTIPLY',math_node('COSINE',angle),amplitude),spiral.inputs['X'])
    l.new(math_node('MULTIPLY',math_node('SINE',angle),amplitude),spiral.inputs['Y'])
    offset=n.new('ShaderNodeVectorMath'); offset.operation='ADD'
    l.new(scale.outputs[0],offset.inputs[0]); l.new(spiral.outputs[0],offset.inputs[1])
    l.new(offset.outputs[0],move.inputs['Offset'])
    l.new(move.outputs['Geometry'],instances.inputs['Points'])
    # A smooth birth/death envelope hides the periodic reset. Calm eye phase.
    birth=math_node('MINIMUM',1,math_node('MULTIPLY',phase,9))
    death=math_node('MINIMUM',1,math_node('MULTIPLY',math_node('SUBTRACT',1,phase),24))
    envelope=math_node('MULTIPLY',birth,death)
    strength=n.new('ShaderNodeValue')
    t=time_expression(settings)
    driver(strength.outputs[0],f'min(1,max(0,({t}-4)/3))*min(1,max(0,(59-{t})))')
    calm=n.new('ShaderNodeValue')
    for p in PHASES:
        calm.outputs[0].default_value=p.particle_intensity
        calm.outputs[0].keyframe_insert(data_path='default_value',frame=frame(p.start,settings))
    arrival=math_node('ADD',1,math_node('MULTIPLY',math_node('POWER',phase,12),2.5))
    size=math_node('MULTIPLY',math_node('MULTIPLY',envelope,arrival),math_node('MULTIPLY',strength.outputs[0],calm.outputs[0]))
    attr=next(x for x in n if x.bl_idname=='GeometryNodeInputNamedAttribute')
    l.new(math_node('MULTIPLY',attr.outputs['Attribute'],size),instances.inputs['Scale'])
    return obj
