"""All artistic and performance controls; importable without Blender."""
from dataclasses import dataclass, replace
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent
QUALITY = 'MEDIUM'  # Reference-focused presentation; use LOW on slower graphics.
FPS = 60
PRESETS = {
    'LOW': (900, 180, 6, 8, 2, 16, 1280, 720, False),
    'MEDIUM': (2500, 650, 7, 12, 3, 32, 1920, 1080, False),
    'HIGH': (5000, 1200, 9, 16, 4, 48, 1920, 1080, True),
    'ULTRA': (9000, 2200, 12, 24, 5, 64, 2560, 1440, True),
}
DEPTHS = {'crown': .55, 'forehead': .4, 'face': .55, 'eyes': .6,
          'tilak': .65, 'trunk': .95, 'ears': .1, 'arms': .5, 'hands': .75,
          'necklace': .7, 'jewelry': .7, 'torso': .2, 'waist': .2,
          'dhoti': .05, 'legs': .15, 'feet': .25, 'silhouette': 0.0}

@dataclass(frozen=True)
class Settings:
    quality: str = QUALITY
    fps: int = FPS
    animation_speed: float = 1.0
    star_count: int = 900
    particle_count: int = 180
    galaxy_count: int = 6
    curve_resolution: int = 8
    bevel_resolution: int = 2
    samples: int = 16
    render_width: int = 1280
    render_height: int = 720
    enable_volumetrics: bool = False
    enable_stars: bool = True
    enable_particles: bool = True
    enable_nebula: bool = True
    enable_galaxies: bool = True
    enable_planets: bool = True
    enable_halo: bool = True
    bloom_intensity: float = .28
    show_performance_info: bool = False
    world_width: float = 10.0
    world_height: float = 12.0
    depth_wave: float = .065
    stroke_scale: float = .006
    seed: int = 108
    final_hold_seconds: float = 600.0
    show_greeting: bool = False  # Optional festival text; the reference artwork has none.

    def __post_init__(self):
        if self.quality not in PRESETS:
            raise ValueError(f'Unknown quality {self.quality!r}; choose {tuple(PRESETS)}')
        if self.fps <= 0 or not math.isfinite(self.animation_speed) or self.animation_speed <= 0:
            raise ValueError('FPS and animation speed must be positive and finite')
        if min(self.render_width, self.render_height, self.curve_resolution, self.samples) <= 0:
            raise ValueError('Resolution and samples must be positive')
        if min(self.star_count, self.particle_count, self.galaxy_count) < 0:
            raise ValueError('Object counts cannot be negative')

def get_settings(quality=QUALITY, **overrides):
    quality = quality.upper()
    if quality not in PRESETS:
        raise ValueError(f'Invalid quality {quality!r}; expected {", ".join(PRESETS)}')
    names = ('star_count', 'particle_count', 'galaxy_count', 'curve_resolution',
             'bevel_resolution', 'samples', 'render_width', 'render_height', 'enable_volumetrics')
    return replace(Settings(quality=quality, **dict(zip(names, PRESETS[quality]))), **overrides)
