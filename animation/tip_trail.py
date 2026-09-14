"""Small cached trailing motes. Geometry never rebuilds during playback."""
from bisect import bisect_right
from setup_scene import sphere
from animation.timeline import frame
from animation.stroke_animator import linear_animation
from ganesha.depth_mapper import sample_polyline
import math

def build(scene,manifestation,settings):
    slots=manifestation['slots']; coords=manifestation['coordinates']
    starts=[s.start for s in slots]
    col=manifestation['tip'].users_collection[0]
    for i in range(7):
        mote=sphere(f'Fading tip trail {i}',(0,0,0),.018*(1-i*.09),manifestation['materials']['tip_gold'],col,8,4)
        mote.scale=(0,)*3; mote.keyframe_insert(data_path='scale',frame=1)
        delay=.035*(i+1)
        for step in range(8*20,59*20):
            seconds=step/20; sampled=seconds-delay
            index=max(0,bisect_right(starts,sampled)-1); slot=slots[index]
            if slot.start<=sampled<=slot.end:
                u=(sampled-slot.start)/(slot.end-slot.start)
                p=sample_polyline(coords[slot.path.id],u)
                mote.location=(p[0]+i*.003*math.sin(seconds),p[1]+i*.004,p[2]-.012*i)
                mote.scale=(1,)*3
            else: mote.scale=(0,)*3
            mote.keyframe_insert(data_path='location',frame=frame(seconds,settings))
            mote.keyframe_insert(data_path='scale',frame=frame(seconds,settings))
        mote.scale=(0,)*3; mote.keyframe_insert(data_path='scale',frame=frame(59,settings))
        linear_animation(mote)
