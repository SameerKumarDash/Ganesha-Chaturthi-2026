from shaders.divine_glow import time_expression
from setup_scene import aim

def animate(camera,settings):
    t=time_expression(settings)
    # Camera tracks a static center using a constraint; bounded post-reveal orbit.
    import bpy
    target=bpy.data.objects.new('Reverent camera focus',None)
    camera.users_scene[0].collection.objects.link(target); target.location=(0,.45,0)
    x=f'(.20*sin({t}*.045)+3.1*sin(max(0,{t}-65)*.025))'
    z=f'(31-1.3*min(1,{t}/65)+.15*sin(max(0,{t}-65)*.025))'
    camera.driver_add('location',0).driver.expression=x
    camera.driver_add('location',1).driver.expression=f'.45+.06*sin({t}*.05)'
    camera.driver_add('location',2).driver.expression=z
    # XY artwork uses global Y as up. Track To's global-Z convention rolls it.
    camera.driver_add('rotation_euler',0).driver.expression=f'-.002*sin({t}*.05)'
    camera.driver_add('rotation_euler',1).driver.expression=f'atan2({x},{z})'
    camera.rotation_euler.z=0
