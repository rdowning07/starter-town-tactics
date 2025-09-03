"""
Demo loader that safely integrates with the existing game/ architecture.
Provides a bridge between the scenario system and the demo applications.
"""

from __future__ import annotations

import os
from typing import Any, Optional, Tuple

import yaml

from game.ai_controller import AIController
from game.fx_manager import FXManager

# Import existing modules
from game.game_state import GameState
from game.overlay.overlay_state import OverlayState
from game.sound_manager import SoundManager
from game.sprite_manager import SpriteManager
from game.unit import Unit

# Try to import the real scenario loader
try:
    from devtools.scenario_loader import load_scenario as _load_scenario

    HAS_REAL_LOADER = True
except ImportError:
    HAS_REAL_LOADER = False
    print("⚠️  Real scenario loader not available, using fallback")

# Try to import CameraController
try:
    from CameraController import CameraController  # type: ignore

    HAS_CAMERA = True
except ImportError:
    CameraController = None  # type: ignore
    HAS_CAMERA = False
    print("⚠️  CameraController not available")


def load_state(scenario_path: str) -> GameState:
    """
    Load a GameState using the existing scenario system.
    Returns a GameState fully wired with managers.
    """
    # Create managers
    sprite_manager = SpriteManager()
    fx_manager = FXManager()
    sound_manager = SoundManager()

    # Try to create camera if available
    camera = None
    if HAS_CAMERA:
        try:
            camera = CameraController(960, 540)
        except Exception as e:
            print(f"⚠️  Failed to create camera: {e}")

    # Try to use real scenario loader first
    if HAS_REAL_LOADER and os.path.exists(scenario_path):
        try:
            print(f"🎬 Using real scenario loader for: {scenario_path}")
            game_state = _load_scenario(
                scenario_path,
                sprite_manager=sprite_manager,
                fx_manager=fx_manager,
                sound_manager=sound_manager,
                camera=camera,
            )

            # Attach managers for later access
            if not hasattr(game_state, "sprite_manager"):
                setattr(game_state, "sprite_manager", sprite_manager)
            if not hasattr(game_state, "fx_manager"):
                setattr(game_state, "fx_manager", fx_manager)
            if not hasattr(game_state, "sound_manager"):
                setattr(game_state, "sound_manager", sound_manager)
            if not hasattr(game_state, "camera") and camera is not None:
                setattr(game_state, "camera", camera)

            # Create overlay state for renderer integration
            if not hasattr(game_state, "overlay_state"):
                setattr(game_state, "overlay_state", OverlayState())

            # Wire up the sim runner with the game state for FX integration
            if hasattr(game_state, "sim_runner"):
                game_state.sim_runner.set_game_state(game_state)

            return game_state

        except Exception as e:
            print(f"⚠️  Real scenario loader failed: {e}")
            print("📋 Falling back to legacy loader...")

    # Fallback to legacy loader
    game_state = GameState()

    # Try to load from scenario file if it exists
    if os.path.exists(scenario_path):
        try:
            game_state = _load_from_scenario_file(scenario_path, game_state, sprite_manager, fx_manager, sound_manager)
        except Exception as e:
            print(f"⚠️  Failed to load scenario {scenario_path}: {e}")
            print("📋 Falling back to default demo state...")
            game_state = _create_default_demo_state(game_state)
    else:
        print(f"⚠️  Scenario file not found: {scenario_path}")
        print("📋 Creating default demo state...")
        game_state = _create_default_demo_state(game_state)

    # Store managers for later use (GameState doesn't have these attributes by default)
    # We'll store them in a way that doesn't conflict with existing attributes
    setattr(game_state, "sprite_manager", sprite_manager)
    setattr(game_state, "fx_manager", fx_manager)
    setattr(game_state, "sound_manager", sound_manager)
    if camera is not None:
        setattr(game_state, "camera", camera)

    # Create overlay state for renderer integration
    setattr(game_state, "overlay_state", OverlayState())

    # Wire up the sim runner with the game state for FX integration
    game_state.sim_runner.set_game_state(game_state)

    return game_state


def _load_from_scenario_file(
    scenario_path: str,
    game_state: GameState,
    sprite_manager: SpriteManager,
    fx_manager: FXManager,
    sound_manager: SoundManager,
) -> GameState:
    """Load game state from a scenario YAML file."""
    with open(scenario_path, "r", encoding="utf-8") as f:
        scenario_data = yaml.safe_load(f)

    # Handle different scenario formats
    if "scenario" in scenario_data:
        # New format with nested scenario
        scenario = scenario_data["scenario"]
    else:
        # Direct format
        scenario = scenario_data

    # Set metadata
    game_state.name = scenario.get("name", "Demo Battle")
    game_state.description = scenario.get("description", "A demonstration battle")
    game_state.max_turns = scenario.get("max_turns", 20)
    game_state.objective = scenario.get("objective", "Defeat all enemies")

    # Load terrain grid if available
    terrain_data = scenario.get("terrain", [])
    if terrain_data:
        game_state.terrain_grid = terrain_data

    # Load units
    units_data = scenario.get("units", [])
    for unit_data in units_data:
        _load_unit_from_scenario(unit_data, game_state)

    # Create scenario manager for compatibility
    camera = None  # No camera for simple demo
    ai_controller = AIController([])
    player_unit = None
    try:
        from devtools.scenario_manager import create_scenario_manager

        scenario_manager = create_scenario_manager(camera, ai_controller, player_unit, game_state)
        scenario_manager.set_managers(sprite_manager, fx_manager, sound_manager)
    except ImportError:
        print("⚠️  Scenario manager not available")

    return game_state


def _load_unit_from_scenario(unit_data: dict, game_state: GameState) -> None:
    """Load a unit from scenario data."""
    unit_id: str = str(unit_data.get("id", "unknown"))
    unit_type: str = str(unit_data.get("type", "knight"))
    team: str = str(unit_data.get("team", "neutral"))
    position: list = unit_data.get("position", [0, 0])
    stats: dict = unit_data.get("stats", {})

    # Create unit
    hp: int = int(stats.get("hp", 10))
    ap: int = int(stats.get("ap", 2))  # Default AP if not specified

    # Add to game state using the proper API
    game_state.add_unit(str(unit_id), str(team), ap=ap, hp=hp)

    # Set position and type
    game_state.units.units[str(unit_id)]["x"] = int(position[0])
    game_state.units.units[str(unit_id)]["y"] = int(position[1])
    game_state.units.units[str(unit_id)]["type"] = str(unit_type)

    print(f"✅ Loaded unit: {unit_id} ({team}) at {position} with {hp} HP, {ap} AP")


def _create_default_demo_state(game_state: GameState) -> GameState:
    """Create a default demo state if scenario loading fails."""
    # Set metadata
    game_state.name = "Default Demo Battle"
    game_state.description = "A demonstration battle with player and enemy units"
    game_state.max_turns = 20
    game_state.objective = "Defeat all enemies"

    # Create default terrain grid
    game_state.terrain_grid = [
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
        ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
    ]

    # Create default units
    default_units = [
        {"id": "player1", "team": "player", "x": 1, "y": 1, "hp": 20, "ap": 3},
        {"id": "enemy1", "team": "ai", "x": 5, "y": 5, "hp": 15, "ap": 2},
    ]

    for unit_data in default_units:
        unit_id = unit_data["id"]
        team = unit_data["team"]
        x = unit_data["x"]
        y = unit_data["y"]
        hp = unit_data["hp"]
        ap = unit_data["ap"]

        # Add to game state using the proper API
        game_state.add_unit(str(unit_id), str(team), ap=ap, hp=hp)

        # Set position
        game_state.units.units[str(unit_id)]["x"] = x
        game_state.units.units[str(unit_id)]["y"] = y

    return game_state


def load_state_and_assets(scenario_path: str):
    """
    Load game state and assets for enhanced demos.
    Returns (game_state, asset_manager) tuple.
    """
    from adapters.pygame.asset_manager import AssetManager

    # Load game state
    game_state = load_state(scenario_path)

    # Create asset manager (but don't load assets yet - needs pygame.display)
    asset_manager = AssetManager()

    return game_state, asset_manager


def load_assets_after_pygame_init(asset_manager):
    """
    Load assets after pygame.display is initialized.
    Call this after pygame.init() and pygame.display.set_mode().
    """
    asset_manager.load_all_common_assets()
