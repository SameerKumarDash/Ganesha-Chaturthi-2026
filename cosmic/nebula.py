import bpy
from setup_scene import collection,sphere
from shaders.nebula_shader import nebula_material,volume_material
from shaders.divine_glow import time_expression

def build(scene,settings):
    col=collection('Nebula',scene); t=time_expression(settings)
    for i,(pos,scale,color) in enumerate([
        ((-9,4,-17),(15,7,2),(.065,.10,.25)),
        ((9,-2,-22),(14,9,2),(.09,.045,.19)),
        ((0,-9,-25),(22,5,2),(.025,.06,.12))]):
        mat=nebula_material(f'Nebula Material {i}',color,settings)
        mesh=bpy.data.meshes.new(f'Nebula cloud plane {i}')
        mesh.from_pydata([(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[],[(0,1,2,3)])
        obj=bpy.data.objects.new(f'Drifting nebula {i}',mesh); col.objects.link(obj)
        obj.location=pos; obj.scale=scale; mesh.materials.append(mat)
        obj.driver_add('rotation_euler',2).driver.expression=f'{i*.7}+.03*sin({t}*.04)'
    if settings.enable_volumetrics:
        obj=sphere('Low density cosmic volume',(0,1,-4),1,volume_material(settings),col)
        obj.scale=(7,7,2)
    return col
