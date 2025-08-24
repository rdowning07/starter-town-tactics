# Standard library imports
import argparse
import json
from pathlib import Path
from typing import Dict, List

# Third-party imports
from PIL import Image

from cli.import_fighter_from_folder import discover_states, pack_strip  # reuse


def main() -> None:
    ap = argparse.ArgumentParser(description='Batch-import multiple raw folders into unit "fighter".')
    ap.add_argument('--raw-roots', type=Path, nargs='+', required=True,
                    help='List of folders, e.g. assets/raw_units/chara2_1 assets/raw_units/chara2_2')
    ap.add_argument('--unit-name', type=str, default='fighter')
    ap.add_argument('--meta-out', type=Path, default=Path('assets/units/_metadata/animation_metadata.json'))
    ap.add_argument('--assets-root', type=Path, default=Path('assets/units'))
    ap.add_argument('--pack', action='store_true', help='Pack into sprite sheets (recommended).')
    ap.add_argument('--fps', type=int, default=8)
    args = ap.parse_args()

    meta = {'version': 1, 'units': {}}
    if args.meta_out.exists():
        try:
            meta = json.loads(args.meta_out.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass
    meta.setdefault('units', {})
    unit_map: Dict[str, dict] = meta['units'].setdefault(args.unit_name, {})

    # Later folders override earlier if they define the same state
    for folder in args.raw_roots:
        states = discover_states(folder)
        for state, frames in states.items():
            if args.pack:
                out_png = args.assets_root / args.unit_name / f'{state}.png'
                w, h = pack_strip(frames, out_png)
                entry = {
                    'sheet': str(out_png).replace('\\', '/'),
                    'frame_size': [w, h],
                    'frames': len(frames),
                    'frame_duration_ms': int(1000 / max(1, args.fps)),
                    'origin': [w // 2, h],
                    'loop': state.startswith('walk_'),
                }
            else:
                w, h = Image.open(frames[0]).size
                entry = {
                    'frame_files': [str(p).replace('\\', '/') for p in frames],
                    'frames': len(frames),
                    'frame_duration_ms': int(1000 / max(1, args.fps)),
                    'origin': [w // 2, h],
                    'loop': state.startswith('walk_'),
                }
            unit_map[state] = entry

    args.meta_out.parent.mkdir(parents=True, exist_ok=True)
    args.meta_out.write_text(json.dumps(meta, indent=2), encoding='utf-8')
    print(f'Batch imported {len(unit_map)} states into unit "{args.unit_name}" at {args.meta_out}')


if __name__ == '__main__':
    main()
