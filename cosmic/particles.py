"""Point clouds with one shared low-poly instance, no per-star objects."""
import bpy

def cloud(name,points,radii,material,col):
    mesh=bpy.data.meshes.new(name+' points'); mesh.from_pydata(points,[],[]); mesh.update()
    attr=mesh.attributes.new('radius','FLOAT','POINT')
    attr.data.foreach_set('value',radii)
    obj=bpy.data.objects.new(name,mesh); col.objects.link(obj)
    group=bpy.data.node_groups.new(name+' instancing','GeometryNodeTree')
    group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    n=group.nodes; l=group.links
    inp=n.new('NodeGroupInput'); out=n.new('NodeGroupOutput')
    ico=n.new('GeometryNodeMeshIcoSphere'); ico.inputs['Radius'].default_value=1; ico.inputs['Subdivisions'].default_value=1
    mat=n.new('GeometryNodeSetMaterial'); mat.inputs['Material'].default_value=material
    radius=n.new('GeometryNodeInputNamedAttribute'); radius.data_type='FLOAT'; radius.inputs['Name'].default_value='radius'
    instances=n.new('GeometryNodeInstanceOnPoints')
    l.new(ico.outputs['Mesh'],mat.inputs['Geometry'])
    l.new(mat.outputs['Geometry'],instances.inputs['Instance'])
    l.new(inp.outputs['Geometry'],instances.inputs['Points'])
    l.new(radius.outputs['Attribute'],instances.inputs['Scale'])
    l.new(instances.outputs['Instances'],out.inputs['Geometry'])
    mod=obj.modifiers.new('Efficient shared instances','NODES'); mod.node_group=group
    return obj,group,instances
