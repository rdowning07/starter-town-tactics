"""
UI State Manager - tracks UI interactions and state.
Integrated with GameState, SimRunner, and TurnController architecture.
"""

from typing import Optional, Tuple, List
from dataclasses import dataclass, field

# @api
# @refactor
@dataclass
class UIState:
    """Tracks UI state for Starter Town Tactics with full architecture integration."""

    # Screen state
    current_screen: str = "game"  # menu, game, pause, victory, defeat

    # Unit selection
    selected_unit: Optional[str] = None
    hovered_unit: Optional[str] = None

    # Tile interaction
    hovered_tile: Optional[Tuple[int, int]] = None
    selected_tile: Optional[Tuple[int, int]] = None

    # Action menu
    show_action_menu: bool = False
    action_menu_pos: Optional[Tuple[int, int]] = None
    action_menu_rect: Optional[Tuple[int, int, int, int]] = None

    # Movement/attack targeting
    show_movement_range: bool = False
    movement_tiles: List[Tuple[int, int]] = field(default_factory=list)

    show_attack_targets: bool = False
    attack_targets: List[Tuple[int, int]] = field(default_factory=list)

    # UI feedback
    show_tooltip: bool = False
    tooltip_text: str = ""
    tooltip_pos: Optional[Tuple[int, int]] = None

    # Animation state
    animations: List[dict] = field(default_factory=list)

    def reset_selection(self):
        """Reset all selection state."""
        self.selected_unit = None
        self.hovered_unit = None
        self.selected_tile = None
        self.show_action_menu = False
        self.action_menu_pos = None
        self.show_movement_range = False
        self.show_attack_targets = False
        self.movement_tiles.clear()
        self.attack_targets.clear()

    def select_unit(self, unit_id: str):
        """Select a unit and show action menu."""
        self.selected_unit = unit_id
        self.show_action_menu = True
        print(f"[UIState] Selected unit: {unit_id}")

    def hover_tile(self, tile_pos: Tuple[int, int]):
        """Update hovered tile position."""
        self.hovered_tile = tile_pos

    def set_movement_range(self, tiles: List[Tuple[int, int]]):
        """Set the movement range tiles."""
        self.movement_tiles = tiles
        self.show_movement_range = True
        self.show_attack_targets = False

    def set_attack_targets(self, tiles: List[Tuple[int, int]]):
        """Set the attack target tiles."""
        self.attack_targets = tiles
        self.show_attack_targets = True
        self.show_movement_range = False

    def show_tooltip_at(self, text: str, pos: Tuple[int, int]):
        """Show a tooltip at the given position."""
        self.tooltip_text = text
        self.tooltip_pos = pos
        self.show_tooltip = True

    def hide_tooltip(self):
        """Hide the tooltip."""
        self.show_tooltip = False
        self.tooltip_text = ""
        self.tooltip_pos = None

    # Backward compatibility for Week 1 implementation
    @property
    def selected_unit_id(self) -> Optional[str]:
        """Backward compatibility property."""
        return self.selected_unit

    @property
    def action_menu_visible(self) -> bool:
        """Backward compatibility property."""
        return self.show_action_menu

    def update_hover(self, tile_pos: Tuple[int, int]):
        """Backward compatibility method."""
        self.hovered_tile = tile_pos

    def deselect_unit(self):
        """Backward compatibility method."""
        print(f"[UIState] Deselected unit: {self.selected_unit}")
        self.reset_selection()
