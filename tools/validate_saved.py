"""Check baked scene playback after reopening without executing main.py."""
import bpy
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
strokes=[o for o in scene.objects if o.get('source_id')]
assert len(strokes)==119
scene.frame_set(1)
assert all(o.hide_render for o in strokes)
scene.frame_set(1861)
partial=sum(not o.hide_render for o in strokes)
assert 0<partial<len(strokes)
tip=scene.objects['Active drawing point']; a=tuple(tip.location)
scene.frame_set(1863)
assert tuple(tip.location)!=a
scene.frame_set(3961)
assert all(not o.hide_render and abs(o['reveal']-1)<.001 for o in strokes)
assert all(fc.driver.is_valid for o in scene.objects if o.animation_data for fc in o.animation_data.drivers)
print('SAVED FILE: opening, progressive strokes, moving tip, final visibility and drivers verified',flush=True)
(root/'output/saved_validation.json').write_text(json.dumps({'passed':True,'source_paths':len(strokes),'partial_paths_at_31s':partial},indent=2))
