"""Single source of timing, including choreography metadata."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Phase:
    name: str
    start: float
    end: float
    categories: tuple = ()
    particle_intensity: float = .4
    camera: str = 'approach'
    light: float = .4
    halo: float = 0.0
    body: float = 0.0

PHASES = (
    Phase('Cosmic void',0,4,(),0,'approach',.04),
    Phase('Awakening',4,8,(),.25,'approach',.12),
    Phase('Crown',8,14,('crown',),.65,'approach',.3),
    Phase('Sacred face',14,22,('face','ears','forehead'),.5,'drift',.4),
    Phase('Serene eyes',22,27,('tilak','eyes'),.18,'drift',.45),
    Phase('Trunk',27,34,('trunk',),.65,'drift',.5,1),
    Phase('Upper form',34,48,('arms','hands','necklace','torso','jewelry'),.6,'drift',.6,1),
    Phase('Seated form',48,58,('waist','dhoti','legs','feet','silhouette'),.5,'approach',.7,1),
    Phase('Manifestation',58,65,(),.35,'approach',1,1,1),
    Phase('Divine presence',65,665,(),.15,'orbit',.8,1,1),
)

def frame(seconds, settings):
    return 1 + seconds * settings.fps / settings.animation_speed

def phase_at(seconds):
    return next((p for p in PHASES if p.start <= seconds < p.end), PHASES[-1])

def validate_phases(phases=PHASES):
    for i,p in enumerate(phases):
        if not all(math.isfinite(x) for x in (p.start,p.end)) or p.end <= p.start:
            raise ValueError(f'Invalid timing for {p.name}')
        if i and p.start < phases[i-1].end:
            raise ValueError(f'Overlapping phase {p.name}')
    return True

@dataclass(frozen=True)
class StrokeSlot:
    path: object
    start: float
    end: float

def schedule(paths):
    """Preserve sorted source order; use anatomical windows when monotonic.

    Arbitrary external drawing orders instead receive length-weighted slots
    across 8..58 seconds, avoiding surprising reordering of source artwork.
    """
    lookup = {c:p for p in PHASES for c in p.categories}
    windows = [lookup.get(p.category, PHASES[7]) for p in paths]
    groups = []
    if all(a.start <= b.start for a,b in zip(windows, windows[1:])):
        for phase in PHASES:
            members = [p for p,w in zip(paths, windows) if w is phase]
            if members:
                groups.append((phase.start,phase.end,members))
    else:
        groups = [(8,58,list(paths))]
    result=[]
    for start,end,members in groups:
        weights=[max(1, sum(math.dist(a,b) for a,b in zip(p.points,p.points[1:])))**.65 for p in members]
        cursor=start
        for path,w in zip(members,weights):
            duration=(end-start)*w/sum(weights)
            gap=min(.13,duration*.12)
            result.append(StrokeSlot(path,cursor+gap,cursor+duration))
            cursor+=duration
    return result
