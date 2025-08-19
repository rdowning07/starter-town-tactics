from typing import Protocol, Optional, Any, Dict, List, Tuple, Iterable, TYPE_CHECKING
from dataclasses import dataclass
from .events import Event, ev_turn_started, ev_turn_ended

if TYPE_CHECKING:
    from .command import Command

# Type alias for unit references
UnitRef = str

@dataclass
class RenderTile:
    """Tile data for rendering."""
    pos: Tuple[int, int]
    move_cost: int
    
    def draw(self, screen) -> None:
        """Draw the tile on the screen."""
        # Simple colored rectangle for now
        import pygame
        x, y = self.pos
        color = (100, 100, 100) if self.move_cost > 1 else (50, 150, 50)
        pygame.draw.rect(screen, color, (x * 32, y * 32, 32, 32))
        pygame.draw.rect(screen, (255, 255, 255), (x * 32, y * 32, 32, 32), 1)

@dataclass
class RenderUnit:
    """Unit data for rendering."""
    unit_id: str
    sprite_id: str
    pixel_pos: Tuple[int, int]
    team: str

@dataclass
class GameSnapshot:
    """Snapshot of game state for rendering."""
    tiles: List[RenderTile]
    units: List[RenderUnit]
    objective_lines: List[str]

class Controller(Protocol):
    def decide(self, state: 'GameState') -> 'Command': ...

class TurnController:
    def __init__(self):
        self.turn_index = 0
        self._pending_end = False
        self._current_unit_id = "player1"
        self._current_side = "player"
    
    @property
    def current_unit_id(self) -> str:
        return self._current_unit_id
    
    @property
    def current_side(self) -> str:
        return self._current_side
    
    def flag_end_of_turn(self) -> None:
        self._pending_end = True
    
    def start_if_needed(self, s) -> Iterable[Event]:
        # Called at the beginning of a turn (or game start)
        if s.turn_started_this_tick:
            yield ev_turn_started(self.current_unit_id, self.current_side, self.schedule_index(), s.tick)
    
    def maybe_advance(self, s) -> Iterable[Event]:
        if not self._pending_end:
            return ()
        # close current
        evts: List[Event] = [ev_turn_ended(self.current_unit_id, self.current_side, self.schedule_index(), s.tick)]
        # advance scheduling to next unit/side
        self._advance_schedule(s)
        self._pending_end = False
        # open next
        evts.append(ev_turn_started(self.current_unit_id, self.current_side, self.schedule_index(), s.tick))
        return evts
    
    def schedule_index(self) -> int:
        return self.turn_index
    
    def _advance_schedule(self, s) -> None:
        # rotate to next unit; increment turn_index as your design requires
        self.turn_index += 1
        # For now, simple rotation between player and enemy
        if self._current_side == "player":
            self._current_side = "enemy"
            self._current_unit_id = "enemy1"
        else:
            self._current_side = "player"
            self._current_unit_id = "player1"

class UnitStats:
    def __init__(self, hp: int = 10, atk: int = 5, def_: int = 2, h: int = 0):
        self.hp = hp
        self.atk = atk
        self.def_ = def_
        self.h = h  # height

class Unit:
    def __init__(self, unit_id: str, pos: Tuple[int, int], facing: str = "N", stats: Optional[UnitStats] = None, team: str = "player"):
        self.id = unit_id
        self.pos = pos
        self.facing = facing
        self.stats = stats or UnitStats()
        self.status: List[str] = []  # Status effects
        self.team = team

class Map:
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self._tiles: Dict[Tuple[int, int], 'Tile'] = {}
    
    def tile(self, pos: Tuple[int, int]) -> 'Tile':
        if pos not in self._tiles:
            self._tiles[pos] = Tile(pos)
        return self._tiles[pos]
    
    def in_bounds(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height
    
    def blocked(self, pos: Tuple[int, int]) -> bool:
        # For now, assume no tiles are blocked
        return False

class Tile:
    def __init__(self, pos: Tuple[int, int], move_cost: int = 1):
        self.pos = pos
        self.move_cost = move_cost

class Rules:
    """Rules engine for game mechanics."""
    
    def can_move(self, unit: Unit, to_pos: Tuple[int, int]) -> bool:
        # Simple validation - check bounds and not blocked
        return True  # TODO: Implement proper validation
    
    def move_unit(self, unit: Unit, to_pos: Tuple[int, int]) -> None:
        unit.pos = to_pos
    
    def can_attack(self, attacker: Unit, target: Unit) -> bool:
        # Simple validation - check if units exist
        return True  # TODO: Implement proper validation
    
    def apply_attack(self, attacker: Unit, target: Unit) -> int:
        # Simple damage calculation
        damage = max(0, attacker.stats.atk - target.stats.def_)
        target.stats.hp = max(0, target.stats.hp - damage)
        return damage
    
    def on_post_action(self, game_state: 'GameState') -> List[Event]:
        # Hook for status effects and other post-action events
        return []

class GameState:
    def __init__(self) -> None:
        self.objectives: Optional[Any] = None  # Will be ObjectivesManager
        self.turn_controller = TurnController()  # Default turn controller
        self._current_controller: Optional[Controller] = None
        self._is_over = False
        self.map = Map()
        self._units: Dict[str, Unit] = {}
        self.tick = 0  # Monotonic tick counter
        self.turn_started_this_tick = False  # Flag for turn start events
        self.rules = Rules()  # Rules engine
    
    def is_over(self) -> bool:
        return self._is_over
    
    def current_controller(self) -> Controller:
        if self._current_controller is None:
            raise RuntimeError("No controller set")
        return self._current_controller
    
    def set_controller(self, controller: Controller) -> None:
        self._current_controller = controller
    
    def set_over(self, is_over: bool) -> None:
        self._is_over = is_over
    
    def unit(self, unit_ref: UnitRef) -> Unit:
        """Get a unit by reference."""
        if unit_ref not in self._units:
            raise KeyError(f"Unit {unit_ref} not found")
        return self._units[unit_ref]
    
    def add_unit(self, unit: Unit) -> None:
        """Add a unit to the game state."""
        self._units[unit.id] = unit
    
    def get_all_units(self) -> List[Unit]:
        """Get all units in the game state."""
        return list(self._units.values())
    
    def player_wiped(self) -> bool:
        """Check if all player units are dead."""
        player_units = [u for u in self._units.values() if u.team == "player"]
        return len(player_units) == 0 or all(u.stats.hp <= 0 for u in player_units)
    
    def controlled_by_player(self, pos: Tuple[int, int]) -> bool:
        """Check if a position is controlled by player units."""
        for unit in self._units.values():
            if unit.team == "player" and unit.pos == pos and unit.stats.hp > 0:
                return True
        return False
    
    def current_side(self) -> str:
        """Get the current side (player/enemy)."""
        return self.turn_controller.current_side
    
    def current_unit(self) -> Unit:
        """Get the current unit."""
        return self.unit(self.turn_controller.current_unit_id)
    
    def get_unit_at(self, pos: Tuple[int, int]) -> Optional[Unit]:
        """Get unit at the specified position, if any."""
        for unit in self._units.values():
            if unit.pos == pos and unit.stats.hp > 0:
                return unit
        return None
    
    def snapshot(self) -> 'GameSnapshot':
        """Create a snapshot of the current game state for rendering."""
        return GameSnapshot(
            tiles=self._get_tiles_for_rendering(),
            units=self._get_units_for_rendering(),
            objective_lines=self._get_objective_lines()
        )
    
    def _get_tiles_for_rendering(self) -> List['RenderTile']:
        """Get tiles for rendering."""
        tiles = []
        for x in range(self.map.width):
            for y in range(self.map.height):
                pos = (x, y)
                tile = self.map.tile(pos)
                tiles.append(RenderTile(pos, tile.move_cost))
        return tiles
    
    def _get_units_for_rendering(self) -> List['RenderUnit']:
        """Get units for rendering."""
        units = []
        for unit in self._units.values():
            if unit.stats.hp > 0:  # Only render living units
                units.append(RenderUnit(
                    unit_id=unit.id,
                    sprite_id=unit.id,  # Use unit ID as sprite ID for now
                    pixel_pos=(unit.pos[0] * 32, unit.pos[1] * 32),  # 32x32 tiles
                    team=unit.team
                ))
        return units
    
    def _get_objective_lines(self) -> List[str]:
        """Get objective text lines for rendering."""
        lines = []
        if self.objectives:
            # Add objective summary
            lines.append(f"Objective: {self.objectives.get_current_objective()}")
        lines.append(f"Turn: {self.turn_controller.turn_index}")
        lines.append(f"Current: {self.turn_controller.current_side}")
        return lines
