"""Blender entry point. Use launcher.py from regular Python."""
import argparse
import json
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

def arguments():
    p=argparse.ArgumentParser(description='Divine Cosmic Ganesha / Blender')
    p.add_argument('--quality',default=None,choices=('LOW','MEDIUM','HIGH','ULTRA'))
    p.add_argument('--style',default='SCULPTURAL',choices=('SCULPTURAL','VECTOR'))
    p.add_argument('--vector',default='data/ganesha_vector_data.json')
    p.add_argument('--speed',type=float,default=1)
    p.add_argument('--save',action='store_true')
    p.add_argument('--render-seconds',type=float,nargs='+')
    p.add_argument('--debug',action='store_true')
    p.add_argument('--no-autoplay',action='store_true')
    p.add_argument('--validate',action='store_true')
    return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])

def main():
    try: import bpy
    except ImportError: raise RuntimeError('Run python launcher.py or blender --python main.py; bpy is bundled with Blender.')
    from config import get_settings,QUALITY
    from setup_scene import setup
    from ganesha.path_loader import load_paths
    from ganesha.manifestation import build
    from cosmic.universe import build as build_universe
    from animation.camera_animator import animate
    from animation.light_animator import build as lights
    from animation.timeline import frame,PHASES,validate_phases
    from animation.controls import register,prepare_view,cinema_view
    args=arguments(); started=time.perf_counter()
    settings=get_settings(args.quality or QUALITY,animation_speed=args.speed,show_performance_info=args.debug,
                          bloom_intensity=.9 if args.style=='SCULPTURAL' else .28)
    vector=Path(args.vector)
    if not vector.is_absolute(): vector=ROOT/vector
    # Runtime assets must reside in the isolated project, even with --vector.
    if not vector.resolve().is_relative_to(ROOT):
        raise ValueError('Copy external vector JSON into this project/data first, then pass its relative path.')
    data=load_paths(vector,samples=settings.curve_resolution*2)
    validate_phases()
    print(f'Loaded {len(data.paths)}/{data.source_count} paths; quality={settings.quality}',flush=True)
    if args.style=='SCULPTURAL':
        from sculptural_scene import build as sculptural_build
        scene,manifestation,cosmos=sculptural_build(settings)
    else:
        scene=setup(settings)
        manifestation=build(scene,data,settings)
        build_universe(scene,manifestation,settings); animate(scene.camera,settings); lights(scene,settings)
    scene.render.filepath=str(ROOT/'output')+'/'
    scene['project']='Divine Cosmic Ganesha'; scene['quality']=settings.quality
    scene['source_paths']=len(data.paths); scene['animation_speed']=settings.animation_speed
    for phase in PHASES: scene.timeline_markers.new(phase.name,frame=round(frame(phase.start,settings)))
    register(); prepare_view(scene); scene.frame_set(1)
    output=ROOT/'output'; output.mkdir(exist_ok=True)
    if settings.show_performance_info:
        from animation.performance import diagnose
        diagnose(scene,settings,output)
    if args.validate:
        if args.style=='VECTOR':
            from tests.blender_validation import validate
            validate(scene,manifestation,settings,output)
        else:
            from tests.sculptural_validation import validate
            validate(scene,manifestation,settings,output)
    if args.save:
        scene.frame_set(1)
        bpy.ops.wm.save_as_mainfile(filepath=str(output/('divine_ganesha.blend' if args.style=='SCULPTURAL' else 'vector_ganesha.blend')))
    for seconds in args.render_seconds or []:
        scene.frame_set(round(frame(seconds,settings)))
        prefix='sculptural' if args.style=='SCULPTURAL' else 'preview'
        scene.render.filepath=str(output/f'{prefix}_{seconds:06.2f}s.png')
        start=time.perf_counter(); bpy.ops.render.render(write_still=True)
        print(f'RENDER {seconds}s: {time.perf_counter()-start:.3f} seconds',flush=True)
    report={'blender':bpy.app.version_string,'quality':settings.quality,'source_paths':len(data.paths),
            'scene_objects':len(scene.objects),'elapsed_build_and_validation_seconds':round(time.perf_counter()-started,3),
            'diagnostics':data.diagnostics}
    (output/'last_run.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)
    if not bpy.app.background and not args.no_autoplay:
        cinema_view()
        scene.frame_set(1); bpy.ops.screen.animation_play()

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(f'GANESHA ERROR: {exc}',file=sys.stderr,flush=True)
        raise
