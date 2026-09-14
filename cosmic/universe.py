"""Assemble independently switchable cosmic layers."""
from cosmic import stars,nebula,galaxies,planets,halo
from animation import particle_flow
from ganesha import body_field

def build(scene,manifestation,settings):
    for name,module in [('stars',stars),('nebula',nebula),('galaxies',galaxies),('planets',planets),('halo',halo)]:
        if getattr(settings,'enable_'+name): module.build(scene,settings)
    if settings.enable_particles:
        particle_flow.build(scene,manifestation['tip'],settings)
        from animation.tip_trail import build as trail
        trail(scene,manifestation,settings)
    body_field.build(scene,settings)
