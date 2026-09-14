"""Strict per-path validation with diagnostics; no bpy dependency.

Accepts a list, or {'canvas': {'width', 'height'}, 'paths': [...]}.
Cubic segments are [p0,p1,p2,p3] or dictionaries with those four keys.
Points may be [x,y] or {'x': x, 'y': y}. Unsupported entries are skipped.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import math
import warnings

@dataclass(frozen=True)
class VectorPath:
    id: str
    name: str
    category: str
    step_order: float
    points: tuple
    width: float
    is_closed: bool
    is_filled: bool
    fill_color: object = None

@dataclass(frozen=True)
class VectorData:
    paths: tuple
    width: float
    height: float
    source_count: int
    diagnostics: tuple

def number(value):
    if isinstance(value, bool):
        raise ValueError('boolean is not a coordinate')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('non-finite numeric value')
    return result

def point(value):
    if isinstance(value, dict):
        return number(value['x']), number(value['y'])
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError('point must contain exactly x and y')
    return number(value[0]), number(value[1])

def flag(value):
    if not isinstance(value, bool):
        raise ValueError('closed/filled flags must be booleans')
    return value

def extract_points(entry, samples=16):
    if entry.get('bezier_segments'):
        result = []
        for seg in entry['bezier_segments']:
            raw = [seg[k] for k in ('p0', 'p1', 'p2', 'p3')] if isinstance(seg, dict) else seg
            if len(raw) != 4:
                raise ValueError('cubic segment requires four control points')
            p = list(map(point, raw))
            if result and math.dist(result[-1], p[0]) > .01:
                raise ValueError('disconnected cubic segments; split into separate paths')
            for i in range(samples + 1):
                t = i / samples
                q = tuple((1-t)**3*p[0][a] + 3*(1-t)**2*t*p[1][a]
                          + 3*(1-t)*t*t*p[2][a] + t**3*p[3][a] for a in (0, 1))
                result.append(q)
    else:
        result = [point(p) for p in entry.get('points', [])]
    clean = []
    for p in result:
        if not clean or math.dist(p, clean[-1]) > 1e-6:
            clean.append(p)
    return clean

def load_paths(filename, samples=16, min_length=.5):
    filename = Path(filename)
    try:
        raw = json.loads(filename.read_text(encoding='utf-8-sig'))
    except FileNotFoundError as exc:
        raise ValueError(f'Vector file missing: {filename}. Supply --vector or restore data/.') from exc
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError(f'Invalid vector JSON in {filename}: {exc}') from exc
    if samples < 2:
        raise ValueError('At least two samples per cubic required')
    entries = raw.get('paths', []) if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ValueError('Vector JSON must be a path list or an object containing paths')
    canvas = raw.get('canvas', {}) if isinstance(raw, dict) else {}
    width, height = number(canvas.get('width', 2700)), number(canvas.get('height', 3300))
    if min(width, height) <= 0:
        raise ValueError('Canvas width/height must be positive')
    valid, diagnostics, seen = [], [], set()
    for index, entry in enumerate(entries):
        try:
            if not isinstance(entry, dict):
                raise ValueError('path must be an object')
            if entry.get('type', 'path') not in ('path', 'polyline', 'bezier'):
                raise ValueError(f'unsupported path type {entry["type"]!r}')
            pts = extract_points(entry, samples)
            closed = flag(entry.get('is_closed', False))
            if closed and len(pts) > 2 and math.dist(pts[0], pts[-1]) > 1e-6:
                pts.append(pts[0])
            if len(pts) < 2 or sum(math.dist(a,b) for a,b in zip(pts, pts[1:])) < min_length:
                raise ValueError('empty or micro path')
            path_id = str(entry.get('id', f'path_{index:04d}'))
            if path_id in seen:
                raise ValueError(f'duplicate path id {path_id}')
            stroke_width = number(entry.get('width', 2.0))
            if stroke_width <= 0:
                raise ValueError('width must be positive')
            path = VectorPath(path_id, str(entry.get('name', path_id)),
                              str(entry.get('category', 'silhouette')).lower(),
                              number(entry.get('step_order', index)), tuple(pts), stroke_width,
                              closed, flag(entry.get('is_filled', False)), entry.get('fill_color'))
            valid.append(path)
            seen.add(path_id)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            message = f'Path {index} skipped: {exc}'
            diagnostics.append(message)
            warnings.warn(message, stacklevel=2)
    if not valid:
        raise ValueError(f'No valid paths in {filename}; {len(diagnostics)} invalid entries')
    # Stable sorting preserves the original drawing order within a step.
    valid.sort(key=lambda path: path.step_order)
    return VectorData(tuple(valid), width, height, len(entries), tuple(diagnostics))
