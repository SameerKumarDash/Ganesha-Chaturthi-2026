"""Reusable emission and compositor glow (Eevee Next has no legacy bloom)."""
import bpy

def emission(name,color,strength=1):
    existing=bpy.data.materials.get(name)
    if existing: return existing
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    nodes.clear()
    out=nodes.new('ShaderNodeOutputMaterial')
    emit=nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value=(*color,1)
    emit.inputs['Strength'].default_value=strength
    mat.node_tree.links.new(emit.outputs[0],out.inputs['Surface'])
    mat.diffuse_color=(*color,1)
    return mat

def driver(socket,expression):
    socket.driver_add('default_value').driver.expression=expression

def setup_glow(scene,settings):
    scene.use_nodes=True
    tree=scene.node_tree
    tree.nodes.clear()
    source=tree.nodes.new('CompositorNodeRLayers')
    glare=tree.nodes.new('CompositorNodeGlare')
    glare.glare_type='FOG_GLOW'
    glare.quality='MEDIUM'
    if 'Strength' in glare.inputs:
        glare.inputs['Threshold'].default_value=1.2
        glare.inputs['Strength'].default_value=settings.bloom_intensity
        glare.inputs['Size'].default_value=.3
    else:  # Blender 4.2-4.4 legacy glare properties.
        glare.threshold=1.2
        glare.size=7
        glare.mix=-1+settings.bloom_intensity
    out=tree.nodes.new('CompositorNodeComposite')
    tree.links.new(source.outputs['Image'],glare.inputs['Image'])
    tree.links.new(glare.outputs['Image'],out.inputs['Image'])

def time_expression(settings):
    return f'((frame-1)*{settings.animation_speed/settings.fps:.12f})'
