"""Length-based Trim Curve before Curve to Mesh; shared node group."""
import bpy

def trim_group(settings):
    group=bpy.data.node_groups.new('Divine stroke - exact length reveal','GeometryNodeTree')
    for name,kind,io in [('Geometry','NodeSocketGeometry','INPUT'),('Reveal','NodeSocketFloat','INPUT'),
                          ('Radius','NodeSocketFloat','INPUT'),('Material','NodeSocketMaterial','INPUT'),
                          ('Geometry','NodeSocketGeometry','OUTPUT')]:
        group.interface.new_socket(name=name,in_out=io,socket_type=kind)
    n=group.nodes; l=group.links
    inp=n.new('NodeGroupInput'); out=n.new('NodeGroupOutput')
    trim=n.new('GeometryNodeTrimCurve'); trim.mode='FACTOR'
    circle=n.new('GeometryNodeCurvePrimitiveCircle')
    circle.inputs['Resolution'].default_value=4+settings.bevel_resolution*2
    mesh=n.new('GeometryNodeCurveToMesh')
    mesh.inputs['Fill Caps'].default_value=True
    mat=n.new('GeometryNodeSetMaterial')
    l.new(inp.outputs['Geometry'],trim.inputs['Curve'])
    l.new(inp.outputs['Reveal'],trim.inputs['End'])
    l.new(inp.outputs['Radius'],circle.inputs['Radius'])
    l.new(trim.outputs['Curve'],mesh.inputs['Curve'])
    l.new(circle.outputs['Curve'],mesh.inputs['Profile Curve'])
    l.new(mesh.outputs['Mesh'],mat.inputs['Geometry'])
    l.new(inp.outputs['Material'],mat.inputs['Material'])
    l.new(mat.outputs['Geometry'],out.inputs['Geometry'])
    return group

def socket_id(group,name):
    return next(s.identifier for s in group.interface.items_tree if s.name==name and s.in_out=='INPUT')

def build_curve(path,points,group,material,collection,settings):
    curve=bpy.data.curves.new(path.name,'CURVE')
    curve.dimensions='3D'
    curve.resolution_u=settings.curve_resolution
    spline=curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points): p.co=(*co,1)
    # Closed paths explicitly repeat first point: Trim Curve must stay non-cyclic.
    obj=bpy.data.objects.new(f'Stroke {path.id} - {path.name}',curve)
    collection.objects.link(obj)
    obj['reveal']=0.0
    obj['category']=path.category
    obj['source_id']=path.id
    obj['source_filled']=path.is_filled
    obj.id_properties_ui('reveal').update(min=0,max=1)
    mod=obj.modifiers.new('Progressive energy stroke','NODES'); mod.node_group=group
    mod[socket_id(group,'Radius')]=max(.004,min(.035,path.width*settings.stroke_scale))
    mod[socket_id(group,'Material')]=material
    key=socket_id(group,'Reveal')
    d=mod.driver_add(f'["{key}"]').driver
    d.expression='reveal'
    v=d.variables.new(); v.name='reveal'; v.type='SINGLE_PROP'
    v.targets[0].id=obj; v.targets[0].data_path='["reveal"]'
    return obj
