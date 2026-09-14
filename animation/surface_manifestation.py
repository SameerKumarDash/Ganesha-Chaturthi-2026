"""Progressive golden contour drawing and instanced stellar sparks on real mesh surfaces."""
import random
import bpy
from mathutils import Vector
from cosmic.particles import cloud
from setup_scene import collection
from ganesha.sculpture import appear
from ganesha.path_loader import VectorPath
from ganesha.manifestation import build_strokes
from animation.timeline import PHASES
from animation.particle_flow import build as attraction
from animation.tip_trail import build as trail

def contour_paths(guides):
    """Sculpture guides -> VectorPath records, stably ordered by manifestation phase."""
    rank={c:i for i,p in enumerate(PHASES) for c in p.categories}
    ordered=sorted(guides,key=lambda g:rank.get(g[1],len(PHASES)))
    paths=[]; coords={}
    for i,(name,category,points,width) in enumerate(ordered):
        path=VectorPath(f's{i:03d}',name,category,i,tuple(points),width,False,False)
        paths.append(path); coords[path.id]=tuple(tuple(p) for p in points)
    return paths,coords

def build(scene,sculpture,settings):
    col=collection('Living surface starlight',scene)
    rng=random.Random(1082026)
    bpy.context.view_layer.update()
    for obj in sculpture['anatomy']:
        if obj.type!='MESH': continue
        transform=obj.matrix_world; normal_matrix=transform.to_3x3().inverted().transposed()
        candidates=[]
        for v in obj.data.vertices:
            normal=(normal_matrix@v.normal).normalized()
            # Grazing normals sit on the camera silhouette: the reference's glittering golden rim.
            if .0<normal.z<.45:
                jitter=Vector((rng.uniform(-.012,.012),rng.uniform(-.012,.012),rng.uniform(-.012,.012)))
                co=transform@v.co+normal*.018+jitter
                candidates.append(tuple(co))
        count=min(len(candidates),160 if settings.quality=='LOW' else 320)
        if not count: continue
        pts=rng.sample(candidates,count)
        dust,_,_=cloud('Surface sparks - '+obj.name,pts,[rng.uniform(.004,.014) for _ in pts],sculpture['gold'],col)
        appear(dust,obj['manifest_end']-.4,obj['manifest_end'],settings)
    # The luminous point traces each anatomical contour; dust converges on that exact point.
    paths,coords=contour_paths(sculpture['guides'])
    manifestation=build_strokes(scene,paths,coords,settings,'Divine contour strokes',tip_radius=.085)
    sculpture['manifestation']=manifestation
    attraction(scene,manifestation['tip'],settings)
    trail(scene,manifestation,settings)
    return manifestation['tip']
