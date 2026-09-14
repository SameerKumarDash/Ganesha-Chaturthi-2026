"""Inventory only this project; include third-party portable runtime files."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'FILE_MANIFEST.txt'
out.touch(exist_ok=True)
entries=[]
for path in sorted(ROOT.rglob('*')):
    if path.is_file():
        entries.append(f'{path.relative_to(ROOT).as_posix()}\t{path.stat().st_size} bytes')
out.write_text('All project files, including generated files and portable Blender.\n'
               'Manifest self-size reflects its previous generation.\n\n'+'\n'.join(entries)+'\n',encoding='utf-8')
print(f'Inventoried {len(entries)} files in {out}')
