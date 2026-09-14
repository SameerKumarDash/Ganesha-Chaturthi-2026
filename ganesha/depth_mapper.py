"""Aspect-preserving normalization and gentle anatomical depth."""
import math
from config import DEPTHS

def normalize(point, width, height, settings):
    if width <= 0 or height <= 0:
        raise ValueError('Canvas dimensions must be positive')
    scale = min(settings.world_width / width, settings.world_height / height)
    return (point[0] - width / 2) * scale, (height / 2 - point[1]) * scale

def map_path(path, data, settings):
    distances = [0.0]
    for a,b in zip(path.points, path.points[1:]):
        distances.append(distances[-1] + math.dist(a,b))
    total = distances[-1] or 1.0
    base = DEPTHS.get(path.category, DEPTHS['silhouette'])
    result = []
    for p, d in zip(path.points, distances):
        x,y = normalize(p, data.width, data.height, settings)
        u = d / total
        wave = settings.depth_wave * math.sin(2 * math.pi * u)
        bulge = .16 * math.sin(math.pi * u)**2 if path.category == 'trunk' else 0
        result.append((x,y,base + wave + bulge))
    return tuple(result)

def arc_lengths(points):
    lengths = [0.0]
    for a,b in zip(points, points[1:]):
        lengths.append(lengths[-1] + math.dist(a,b))
    return lengths

def sample_polyline(points, fraction):
    from bisect import bisect_right
    lengths = arc_lengths(points)
    target = max(0, min(1, fraction)) * lengths[-1]
    i = min(len(points)-2, max(0, bisect_right(lengths, target)-1))
    u = (target-lengths[i]) / max(1e-12, lengths[i+1]-lengths[i])
    return tuple(a+(b-a)*u for a,b in zip(points[i],points[i+1]))
