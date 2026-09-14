from setup_scene import collection,sphere
from shaders.cosmic_materials import planet_material,atmosphere_material
from shaders.divine_glow import time_expression

def build(scene,settings):
    col=collection('Planets',scene); mat=planet_material(); atmosphere=atmosphere_material()
    for i,(pos,r) in enumerate([((8,1.9,-7),.78),((-8.5,-3.1,-9),.48)]):
        planet=sphere(f'Slow planet {i}',pos,r,mat,col,32,16)
        planet.driver_add('rotation_euler',1).driver.expression=f'{time_expression(settings)}*.018'
        sphere(f'Atmosphere {i}',pos,r*1.015,atmosphere,col,32,16)
    return col
