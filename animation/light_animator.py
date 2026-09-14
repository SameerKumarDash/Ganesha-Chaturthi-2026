import bpy
from setup_scene import aim
from animation.timeline import PHASES,frame

def build(scene,settings):
    lights=[]
    for name,pos,color,power,size in [
        ('Warm divine front',(-2,3,6),(1,.68,.35),180,7),
        ('Indigo rim',(4,1,-1),(.24,.36,1),110,5),
        ('Celestial planet rim',(-8,6,0),(1,.72,.4),280,5)]:
        data=bpy.data.lights.new(name,'AREA'); data.color=color; data.shape='DISK'; data.size=size
        obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=pos; aim(obj)
        for phase in PHASES:
            data.energy=power*phase.light; data.keyframe_insert(data_path='energy',frame=frame(phase.start,settings))
        lights.append(obj)
    return lights
