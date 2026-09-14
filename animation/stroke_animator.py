"""Bake lightweight curves and exact, piecewise linear tip motion into .blend."""
from animation.timeline import frame
from ganesha.depth_mapper import arc_lengths

def linear_animation(id_block):
    if id_block.animation_data and id_block.animation_data.action:
        for fc in id_block.animation_data.action.fcurves:
            for k in fc.keyframe_points: k.interpolation='LINEAR'

def animate_stroke(obj,slot,settings):
    start,end=frame(slot.start,settings),frame(slot.end,settings)
    for f,value in ((1,0),(start,0),(end,1)):
        obj['reveal']=float(value); obj.keyframe_insert(data_path='["reveal"]',frame=f)
    # Explicit hiding ensures the zero-length trim has no cap or visible point.
    for f,value in ((1,True),(start,False)):
        obj.hide_render=value; obj.keyframe_insert(data_path='hide_render',frame=f)
        obj.hide_viewport=value; obj.keyframe_insert(data_path='hide_viewport',frame=f)
    linear_animation(obj)

def animate_tip(tip,slots,coordinates,settings):
    previous=None
    for slot in slots:
        points=coordinates[slot.path.id]
        lengths=arc_lengths(points); total=lengths[-1]
        start,end=frame(slot.start,settings),frame(slot.end,settings)
        if previous:
            last_end,last_point=previous
            middle=(last_end+start)/2
            tip.location=tuple((a+b)/2 for a,b in zip(last_point,points[0]))
            tip.location.z+=.10
            tip.keyframe_insert(data_path='location',frame=middle)
            tip.scale=(.15,)*3; tip.keyframe_insert(data_path='scale',frame=middle)
        for point,length in zip(points,lengths):
            tip.location=point
            tip.keyframe_insert(data_path='location',frame=start+(end-start)*length/total)
        for f in (start,end):
            tip.scale=(1,)*3; tip.keyframe_insert(data_path='scale',frame=f)
        previous=(end,points[-1])
    tip.scale=(0,)*3; tip.keyframe_insert(data_path='scale',frame=1)
    tip.keyframe_insert(data_path='scale',frame=frame(4,settings))
    tip.location=(0,2.8,.6); tip.keyframe_insert(data_path='location',frame=frame(4,settings))
    tip.scale=(.45,)*3; tip.keyframe_insert(data_path='scale',frame=frame(6,settings))
    tip.scale=(0,)*3; tip.keyframe_insert(data_path='scale',frame=frame(58.6,settings))
    linear_animation(tip)
