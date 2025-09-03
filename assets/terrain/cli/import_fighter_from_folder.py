# Standard library imports
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

# Third-party imports
from PIL import Image


def discover_states(unit_dir: Path) -> Dict[str, List[Path]]:
    files = sorted([p for p in unit_dir.glob("*.png") if p.is_file()])

    state_map: Dict[str, List[Path]] = {}

    # Stands
    for p in files:
        if p.name.endswith("_stand.png"):
            prefix = p.name[:-10]  # remove '_stand.png'
            # Prefix typically 'down', 'left', 'right', 'up'
            state_map[f"idle_{prefix}"] = [p]

    # Walk loops
    rx = re.compile(r"^(.*)_walk(\d+)\.png$")
    walk_groups: Dict[str, List[Path]] = {}
    for p in files:
        m = rx.match(p.name)
        if not m:
            continue
        key = m.group(1)  # e.g., 'down', 'left'
        walk_groups.setdefault(key, []).append(p)

    for key, frames in walk_groups.items():
        frames_sorted = sorted(frames, key=lambda pp: int(re.search(r"(\d+)", pp.stem).group(1) or "0"))
        state_map[f"walk_{key}"] = frames_sorted

    return state_map


def pack_strip(frames: List[Path], out_png: Path) -> tuple[int, int]:
    imgs = [Image.open(p).convert("RGBA") for p in frames]
    w, h = imgs[0].size
    out_png.parent.mkdir(parents=True, exist_ok=True)
    strip = Image.new("RGBA", (w * len(imgs), h), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        if im.size != (w, h):
            im = im.resize((w, h), Image.NEAREST)
        strip.paste(im, (i * w, 0))
    strip.save(out_png)
    return w, h


def main() -> None:
    ap = argparse.ArgumentParser(description='Import one raw folder as unit "fighter" into metadata.')
    ap.add_argument("--raw-root", type=Path, required=True, help="e.g., assets/raw_units/chara2_1")
    ap.add_argument("--unit-name", type=str, default="fighter")
    ap.add_argument("--meta-out", type=Path, default=Path("assets/units/_metadata/animation_metadata.json"))
    ap.add_argument("--assets-root", type=Path, default=Path("assets/units"))
    ap.add_argument("--pack", action="store_true", help="Pack into sprite sheets (recommended for runtime).")
    ap.add_argument("--fps", type=int, default=8)
    args = ap.parse_args()

    states = discover_states(args.raw_root)
    meta = {"version": 1, "units": {}}
    if args.meta_out.exists():
        try:
            meta = json.loads(args.meta_out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    meta.setdefault("units", {})
    meta["units"].setdefault(args.unit_name, {})

    for state, frames in states.items():
        if args.pack:
            out_png = args.assets_root / args.unit_name / f"{state}.png"
            w, h = pack_strip(frames, out_png)
            entry = {
                "sheet": str(out_png).replace("\\", "/"),
                "frame_size": [w, h],
                "frames": len(frames),
                "frame_duration_ms": int(1000 / max(1, args.fps)),
                "origin": [w // 2, h],
                "loop": state.startswith("walk_"),
            }
        else:
            w, h = Image.open(frames[0]).size
            entry = {
                "frame_files": [str(p).replace("\\", "/") for p in frames],
                "frames": len(frames),
                "frame_duration_ms": int(1000 / max(1, args.fps)),
                "origin": [w // 2, h],
                "loop": state.startswith("walk_"),
            }
        meta["units"][args.unit_name][state] = entry

    args.meta_out.parent.mkdir(parents=True, exist_ok=True)
    args.meta_out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f'Imported {len(states)} states into unit "{args.unit_name}" at {args.meta_out}')


if __name__ == "__main__":
    main()
