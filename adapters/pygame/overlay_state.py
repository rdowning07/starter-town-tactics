from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

Tile = Tuple[int, int]


@dataclass
class OverlayState:
    """
    Minimal overlay object that satisfies game.renderer.Renderer.render(...).
    Extend if your Renderer reads more fields.
    """

    selected: Optional[str] = None  # unit_id
    hover_tile: Optional[Tile] = None
    highlighted_tiles: List[Tile] = field(default_factory=list)
    path_preview: List[Tile] = field(default_factory=list)
    markers: List[Tile] = field(default_factory=list)

    # Compatibility with existing game.overlay.overlay_state.OverlayState
    show_movement: bool = True
    show_terrain: bool = True
    show_attack: bool = True
    show_threat: bool = True
    movement_tiles: set = field(default_factory=set)
    threat_tiles: set = field(default_factory=set)
    attack_tiles: set = field(default_factory=set)
    terrain_tiles: set = field(default_factory=set)

    # add more fields as your renderer accesses them (e.g., valid_moves, attack_targets)
