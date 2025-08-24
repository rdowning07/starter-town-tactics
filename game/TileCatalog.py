# Standard library imports
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

# Third-party imports
import pygame

# Local imports
# (none) — this is a self-contained loader that other modules can import


class TileCatalog:
    """Loads sliced tile images and an alias map from tiles_manifest.json.

    Usage:
        catalog = TileCatalog(Path('tiles_manifest.json'))
        surf = catalog.get_by_id('TileA2:0,0')  # optional direct id
        surf2 = catalog.get_alias('grass')      # alias to id mapping
    """

    def __init__(self, manifest_path: Path) -> None:
        self._manifest_path = manifest_path
        self._root = manifest_path.parent
        self._tile_size: Tuple[int, int] = (32, 32)
        self._id_to_surface: Dict[str, pygame.Surface] = {}
        self._aliases: Dict[str, str] = {}
        self._load()

    @property
    def tile_size(self) -> Tuple[int, int]:
        return self._tile_size

    def _load(self) -> None:
        with self._manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        w, h = data.get("tile_size", [32, 32])
        self._tile_size = (int(w), int(h))

        # Preload all tile surfaces
        tiles = data.get("tiles", [])
        for t in tiles:
            tile_id = t["id"]
            rel = t["file"]
            path = (self._root / rel).resolve()
            try:
                surface = pygame.image.load(str(path))
                # Only convert if display is initialized
                try:
                    surface = surface.convert_alpha()
                except pygame.error:
                    # Display not initialized, use surface as-is
                    pass
                self._id_to_surface[tile_id] = surface
            except (pygame.error, OSError, ValueError) as e:
                # Skip bad tiles but continue loading
                continue

        # Aliases
        aliases = data.get("starter_aliases", {})
        for k, v in aliases.items():
            if isinstance(v, str) and v in self._id_to_surface:
                self._aliases[k] = v

    def get_by_id(self, tile_id: str) -> Optional[pygame.Surface]:
        return self._id_to_surface.get(tile_id)

    def get_alias(self, name: str) -> Optional[pygame.Surface]:
        tile_id = self._aliases.get(name)
        if tile_id is None:
            return None
        return self.get_by_id(tile_id)

    def set_alias(self, name: str, tile_id: str) -> None:
        if tile_id in self._id_to_surface:
            self._aliases[name] = tile_id

    def aliases(self) -> Dict[str, str]:
        return dict(self._aliases)
