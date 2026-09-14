"""Milestone 3: render only the converted paths before adding effects."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import bpy
from config import get_settings
from setup_scene import setup,collection
from ganesha.path_loader import load_paths
from ganesha.depth_mapper import map_path
from ganesha.curve_builder import build_curve,trim_group
from ganesha.materials import build_materials
s=get_settings('LOW')
scene=setup(s)
data=load_paths(ROOT/'data/ganesha_vector_data.json',samples=20)
group=trim_group(s)
col=collection('Ganesha strokes',scene)
mats=build_materials(s)
for i,p in enumerate(data.paths):
    obj=build_curve(p,map_path(p,data,s),group,mats['gold'][i%4],col,s)
    obj['reveal']=1.0
scene.frame_set(3901)
scene.render.filepath=str(ROOT/'output/shape_validation.png')
bpy.ops.render.render(write_still=True)
print(f'SHAPE: {len(data.paths)}/{data.source_count} paths converted')
