# Standard library imports
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Third-party imports
import pygame


class AnimationCatalog:
    """Loads unit animation metadata and frame files."""

    def __init__(self, manifest_path: Path) -> None:
        self._manifest_path = manifest_path
        self._root = manifest_path.parent
        self._units: Dict[str, Dict[str, dict]] = {}
        self._frames: Dict[str, pygame.Surface] = {}
        self._load()

    def _load(self) -> None:
        """Load animation metadata and frame files."""
        try:
            with self._manifest_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[AnimationCatalog] Failed to load {self._manifest_path}: {e}")
            return

        units = data.get("units", {})
        for unit_key, anims in units.items():
            self._units[unit_key] = {}
            for state, meta in anims.items():
                # Support both sheet-based and frame-based animations
                if "sheet" in meta:
                    # Legacy sprite sheet support
                    sheet_rel = meta.get("sheet")
                    if sheet_rel:
                        sheet_path = (self._root / sheet_rel).resolve()
                        try:
                            if sheet_rel not in self._frames:
                                surface = pygame.image.load(str(sheet_path))
                                try:
                                    surface = surface.convert_alpha()
                                except pygame.error:
                                    pass
                                self._frames[sheet_rel] = surface
                        except (pygame.error, OSError, ValueError) as e:
                            print(f"[AnimationCatalog] Failed to load sheet {sheet_rel}: {e}")
                            continue
                elif "frame_files" in meta:
                    # New frame-based animation support
                    frame_files = meta.get("frame_files", [])
                    for frame_file in frame_files:
                        frame_path = (self._root / frame_file).resolve()
                        try:
                            if frame_file not in self._frames:
                                surface = pygame.image.load(str(frame_path))
                                try:
                                    surface = surface.convert_alpha()
                                except pygame.error:
                                    pass
                                self._frames[frame_file] = surface
                        except (pygame.error, OSError, ValueError) as e:
                            print(f"[AnimationCatalog] Failed to load frame {frame_file}: {e}")
                            continue

                self._units[unit_key][state] = meta

    def get(self, unit_key: str, state: str) -> Optional[dict]:
        """Get animation metadata for a unit and state."""
        return self._units.get(unit_key, {}).get(state)

    def get_frame(self, frame_file: str) -> Optional[pygame.Surface]:
        """Get a single frame surface."""
        return self._frames.get(frame_file)

    def get_sheet(self, meta: dict) -> Optional[pygame.Surface]:
        """Get the sprite sheet surface for animation metadata (legacy support)."""
        path = meta.get("sheet")
        if not path:
            return None
        return self._frames.get(path)

    def has_unit(self, unit_key: str) -> bool:
        """Check if a unit exists in the catalog."""
        return unit_key in self._units

    def has_state(self, unit_key: str, state: str) -> bool:
        """Check if a unit state exists in the catalog."""
        return unit_key in self._units and state in self._units[unit_key]


def frame_index(meta: dict, elapsed_ms: int) -> int:
    """Calculate the current frame index for an animation."""
    dur = int(meta.get("frame_duration_ms", 125))
    total = int(meta.get("frames", 1))
    loop = bool(meta.get("loop", True))

    if dur <= 0 or total <= 0:
        return 0

    if loop:
        return (elapsed_ms // dur) % total
    return min(total - 1, elapsed_ms // dur)


def get_current_frame(meta: dict, elapsed_ms: int) -> Optional[pygame.Surface]:
    """Get the current frame surface for an animation."""
    if "frame_files" in meta:
        # Frame-based animation
        frame_files = meta.get("frame_files", [])
        if not frame_files:
            return None
        idx = frame_index(meta, elapsed_ms)
        if idx < len(frame_files):
            return frame_files[idx]  # Return the frame file path
    elif "sheet" in meta:
        # Sheet-based animation (legacy)
        return meta.get("sheet")
    return None
