import bpy
from shaders.divine_glow import emission

def planet_material(city_lights=0.0):
    """Rough procedural world; optional scattered golden night-side lights."""
    mat=bpy.data.materials.new('Planet Surface'); mat.use_nodes=True
    n=mat.node_tree.nodes; l=mat.node_tree.links
    bsdf=n.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value=.82
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=5; noise.inputs['Detail'].default_value=2
    tex=n.new('ShaderNodeTexCoord'); l.new(tex.outputs['Generated'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(.007,.014,.03,1)
    ramp.color_ramp.elements[1].color=(.12,.17,.22,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.15; bump.inputs['Distance'].default_value=.08
    l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],bsdf.inputs['Normal'])
    if city_lights:
        # Night-side worlds: near-black crust so the rim and golden lights carry the form.
        ramp.color_ramp.elements[0].color=(.002,.003,.006,1); ramp.color_ramp.elements[1].color=(.035,.04,.055,1)
        cells=n.new('ShaderNodeTexVoronoi'); cells.inputs['Scale'].default_value=38
        l.new(tex.outputs['Generated'],cells.inputs['Vector'])
        spark=n.new('ShaderNodeMapRange'); spark.inputs['From Min'].default_value=.12; spark.inputs['From Max'].default_value=0
        l.new(cells.outputs['Distance'],spark.inputs['Value'])
        cluster=n.new('ShaderNodeMath'); cluster.operation='MULTIPLY'
        l.new(spark.outputs[0],cluster.inputs[0]); l.new(noise.outputs['Fac'],cluster.inputs[1])
        power=n.new('ShaderNodeMath'); power.operation='POWER'; power.inputs[1].default_value=3
        l.new(cluster.outputs[0],power.inputs[0])
        bsdf.inputs['Emission Color'].default_value=(1,.55,.18,1)
        strength=n.new('ShaderNodeMath'); strength.operation='MULTIPLY'; strength.inputs[1].default_value=city_lights
        l.new(power.outputs[0],strength.inputs[0]); l.new(strength.outputs[0],bsdf.inputs['Emission Strength'])
    return mat

def atmosphere_material(color=(.10,.20,.39),strength=.6,sharpness=5):
    mat=bpy.data.materials.new('Planet atmosphere'); mat.use_nodes=True; mat.surface_render_method='BLENDED'
    n=mat.node_tree.nodes; l=mat.node_tree.links; n.clear()
    out=n.new('ShaderNodeOutputMaterial'); facing=n.new('ShaderNodeLayerWeight')
    power=n.new('ShaderNodeMath'); power.operation='POWER'; power.inputs[1].default_value=sharpness
    l.new(facing.outputs['Facing'],power.inputs[0])
    transparent=n.new('ShaderNodeBsdfTransparent'); emit=n.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value=(*color,1); emit.inputs['Strength'].default_value=strength
    mix=n.new('ShaderNodeMixShader'); l.new(power.outputs[0],mix.inputs[0])
    l.new(transparent.outputs[0],mix.inputs[1]); l.new(emit.outputs[0],mix.inputs[2]); l.new(mix.outputs[0],out.inputs[0])
    return mat
