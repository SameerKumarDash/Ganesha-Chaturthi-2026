"""Soft procedural clouds with no image textures or external assets."""
import bpy
from shaders.divine_glow import driver,time_expression

def nebula_material(name,color,settings,body=False):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    mat.surface_render_method='BLENDED'
    n=mat.node_tree.nodes; l=mat.node_tree.links; n.clear()
    out=n.new('ShaderNodeOutputMaterial'); tex=n.new('ShaderNodeTexCoord')
    noise=n.new('ShaderNodeTexNoise'); noise.noise_dimensions='4D'
    noise.inputs['Scale'].default_value=3.8 if body else 2.4
    noise.inputs['Detail'].default_value=3
    driver(noise.inputs['W'],f'{time_expression(settings)}*.014')
    l.new(tex.outputs['Generated'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.25
    ramp.color_ramp.elements[0].color=(.0004,.001,.004,1)
    ramp.color_ramp.elements[1].position=.8
    ramp.color_ramp.elements[1].color=(*color,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0])
    emit=n.new('ShaderNodeEmission'); emit.inputs['Strength'].default_value=.55 if body else .65
    l.new(ramp.outputs['Color'],emit.inputs['Color'])
    trans=n.new('ShaderNodeBsdfTransparent'); mix=n.new('ShaderNodeMixShader')
    l.new(trans.outputs[0],mix.inputs[1]); l.new(emit.outputs[0],mix.inputs[2])
    # Generated coordinate distance produces invisible cloud boundaries.
    separate=n.new('ShaderNodeSeparateXYZ'); l.new(tex.outputs['Generated'],separate.inputs[0])
    xy=n.new('ShaderNodeCombineXYZ'); xy.inputs['Z'].default_value=.5
    l.new(separate.outputs['X'],xy.inputs['X']); l.new(separate.outputs['Y'],xy.inputs['Y'])
    distance=n.new('ShaderNodeVectorMath'); distance.operation='DISTANCE'
    distance.inputs[1].default_value=(.5,.5,.5)
    l.new(xy.outputs[0],distance.inputs[0])
    fall=n.new('ShaderNodeMapRange')
    fall.inputs['From Min'].default_value=.10
    fall.inputs['From Max'].default_value=.48
    fall.inputs['To Min'].default_value=.65 if body else .8
    fall.inputs['To Max'].default_value=0
    l.new(distance.outputs['Value'],fall.inputs['Value'])
    fade=n.new('ShaderNodeMath'); fade.operation='MULTIPLY'
    l.new(fall.outputs[0],fade.inputs[0])
    t=time_expression(settings)
    driver(fade.inputs[1],f'min(1,max(0,({t}-{58 if body else 0})/{7 if body else 12}))')
    opacity=n.new('ShaderNodeMath'); opacity.operation='MULTIPLY'
    opacity.inputs[1].default_value=.48 if body else .8
    l.new(fade.outputs[0],opacity.inputs[0]); l.new(opacity.outputs[0],mix.inputs[0])
    l.new(mix.outputs[0],out.inputs['Surface'])
    return mat

def volume_material(settings):
    mat=bpy.data.materials.new('Faint cosmic volume'); mat.use_nodes=True
    n=mat.node_tree.nodes; l=mat.node_tree.links; n.clear()
    out=n.new('ShaderNodeOutputMaterial'); volume=n.new('ShaderNodeVolumePrincipled')
    volume.inputs['Color'].default_value=(.13,.17,.35,1)
    volume.inputs['Density'].default_value=.006
    l.new(volume.outputs[0],out.inputs['Volume'])
    return mat
