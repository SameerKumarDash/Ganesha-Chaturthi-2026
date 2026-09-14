"""Standard-library Windows launcher; no global configuration or packages."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from config import ROOT

def locate_blender(explicit=None):
    candidates=[]
    if explicit: candidates.append(Path(explicit))
    if os.environ.get('BLENDER_EXE'): candidates.append(Path(os.environ['BLENDER_EXE']))
    found=shutil.which('blender')
    if found: candidates.append(Path(found))
    candidates.extend(sorted((ROOT/'tools').glob('blender-4.*-windows-x64/blender.exe'),reverse=True))
    for base in (Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Blender Foundation',):
        if base.exists(): candidates.extend(sorted(base.glob('Blender 4*/blender.exe'),reverse=True))
    for path in candidates:
        if path.is_file(): return path.resolve()
    raise RuntimeError('Blender not found. Install Blender 4.5 LTS, set BLENDER_EXE, or pass --blender "C:\\path\\blender.exe".')

def main():
    parser=argparse.ArgumentParser(description='Launch the isolated Divine Cosmic Ganesha scene')
    parser.add_argument('--blender'); parser.add_argument('--background',action='store_true')
    parser.add_argument('--check',action='store_true')
    args,forward=parser.parse_known_args()
    for name in ('main.py','config.py','data/ganesha_vector_data.json'):
        if not (ROOT/name).is_file(): raise RuntimeError(f'Required project file missing: {name}')
    blender=locate_blender(args.blender)
    env=os.environ.copy()
    for key,part in [('BLENDER_USER_RESOURCES','tools/user'),('TEMP','output/tmp'),('TMP','output/tmp')]:
        folder=ROOT/part; folder.mkdir(parents=True,exist_ok=True); env[key]=str(folder)
    version=subprocess.run([str(blender),'--version'],capture_output=True,text=True,env=env,timeout=30,check=True).stdout
    if not any(f'Blender 4.{i}.' in version for i in (2,3,4,5)):
        raise RuntimeError(f'Blender 4.2-4.5 required. Found: {version.splitlines()[0]}')
    print(f'{version.splitlines()[0]} at {blender}',flush=True)
    if args.check: return 0
    cmd=[str(blender),'--factory-startup','--python-exit-code','1']
    if args.background: cmd.append('--background')
    cmd+=['--python',str(ROOT/'main.py'),'--',*forward]
    return subprocess.call(cmd,cwd=ROOT,env=env)

if __name__=='__main__':
    try: sys.exit(main())
    except (RuntimeError,ValueError,subprocess.SubprocessError,OSError) as exc:
        print(f'GANESHA LAUNCHER: {exc}',file=sys.stderr); sys.exit(1)
