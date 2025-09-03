# Standard library imports
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Third-party imports
import pygame

FrameSpec = Dict[str, Union[str, int, bool, List[str]]]
AnimMap = Dict[str, FrameSpec]


class AnimationCatalog:
    def __init__(self, manifest_path: Path) -> None:
        self._manifest_path = manifest_path
        self._root = manifest_path.parent
        self._units: Dict[str, AnimMap] = {}
        self._sheets: Dict[str, pygame.Surface] = {}
        self._frames_cache: Dict[str, List[pygame.Surface]] = {}
        self._load()

    def _load(self) -> None:
        data = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        for unit_key, anims in data.get("units", {}).items():
            self._units[unit_key] = anims

    def get(self, unit_key: str, state: str) -> Optional[FrameSpec]:
        return self._units.get(unit_key, {}).get(state)

    def _load_sheet(self, sheet_rel: str) -> Optional[pygame.Surface]:
        if sheet_rel in self._sheets:
            return self._sheets[sheet_rel]
        path = (self._root / sheet_rel).resolve()
        try:
            surf = pygame.image.load(str(path)).convert_alpha()
        except (pygame.error, OSError, ValueError):
            return None
        self._sheets[sheet_rel] = surf
        return surf

    def frames_for(self, meta: FrameSpec) -> Optional[List[pygame.Surface]]:
        if "frame_files" in meta:
            key = "files:" + "|".join(meta["frame_files"])  # type: ignore[index]
        else:
            key = "sheet:" + str(meta.get("sheet"))

        if key in self._frames_cache:
            return self._frames_cache[key]

        frames: List[pygame.Surface] = []

        if "frame_files" in meta:
            for rel in meta["frame_files"]:  # type: ignore[index]
                path = (self._root / rel).resolve()
                try:
                    frames.append(pygame.image.load(str(path)).convert_alpha())
                except (pygame.error, OSError, ValueError):
                    continue
        elif "sheet" in meta:
            sheet_rel = str(meta["sheet"])
            sheet = self._load_sheet(sheet_rel)
            if sheet is None:
                return None
            fw, fh = meta.get("frame_size", [32, 32])  # type: ignore[assignment]
            total = int(meta.get("frames", 1))
            for i in range(total):
                rect = pygame.Rect(i * fw, 0, fw, fh)
                frame = pygame.Surface((fw, fh), pygame.SRCALPHA, 32).convert_alpha()
                frame.blit(sheet, (0, 0), rect)
                frames.append(frame)
        else:
            return None

        self._frames_cache[key] = frames
        return frames

    @staticmethod
    def frame_index(meta: FrameSpec, elapsed_ms: int) -> int:
        dur = int(meta.get("frame_duration_ms", 125))
        total = int(meta.get("frames", 1))
        loop = bool(meta.get("loop", True))
        if dur <= 0 or total <= 0:
            return 0
        idx = elapsed_ms // dur
        return int(idx % total) if loop else int(min(total - 1, idx))
