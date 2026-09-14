"""Optional update-cost diagnostic; deliberately does not label it viewport FPS."""
import json
import statistics
import time
import bpy
from animation.timeline import frame

def diagnose(scene,settings,output):
    samples=[]
    for i in range(120):
        started=time.perf_counter()
        scene.frame_set(round(frame(30,settings))+i)
        bpy.context.view_layer.update()
        samples.append((time.perf_counter()-started)*1000)
    result={'objects':len(scene.objects),'geometry_node_groups':len(bpy.data.node_groups),
            'median_scene_update_ms':round(statistics.median(samples),3),
            'p95_scene_update_ms':round(sorted(samples)[113],3),
            'note':'Scene evaluation only. Excludes viewport drawing and compositing; not a measured playback FPS.'}
    (output/'performance.json').write_text(json.dumps(result,indent=2))
    print('PERFORMANCE '+json.dumps(result),flush=True)
    scene.frame_set(1)
