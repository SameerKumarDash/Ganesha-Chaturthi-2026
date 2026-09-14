import bpy
scene=bpy.context.scene
scene.use_nodes=True
g=scene.node_tree.nodes.new('CompositorNodeGlare')
print('GLARE SOCKETS',[(x.name,x.type) for x in g.inputs])
print('RENDER COMPOSITOR PROPERTIES',[p.identifier for p in scene.render.bl_rna.properties if 'composit' in p.identifier])
print('SCENE COMPOSITOR PROPERTIES',[p.identifier for p in scene.bl_rna.properties if 'composit' in p.identifier])
