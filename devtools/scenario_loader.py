# devtools/scenario_loader.py

import yaml
import os
from typing import Dict, List, Optional
from game.game_state import GameState
from game.unit import Unit
from game.sprite_manager import SpriteManager
from game.fx_manager import FXManager
from game.sound_manager import SoundManager

class ScenarioLoader:
    """Loads and validates scenario files for the game."""
    
    def __init__(self):
        self.supported_sprites = ["knight", "rogue", "mage", "archer", "paladin", "shadow", "berserker"]
        self.supported_ai_types = ["aggressive", "defensive", "passive"]
    
    def load_scenario(self, scenario_path: str, sprite_manager: SpriteManager, 
                     fx_manager: FXManager, sound_manager: SoundManager) -> GameState:
        """Load a scenario from a YAML file."""
        
        if not os.path.exists(scenario_path):
            raise FileNotFoundError(f"Scenario file not found: {scenario_path}")
        
        with open(scenario_path, 'r') as f:
            scenario_data = yaml.safe_load(f)
        
        # Validate scenario data
        self._validate_scenario(scenario_data)
        
        # Create game state
        game_state = GameState()
        
        # Set scenario metadata
        game_state.name = scenario_data.get("name", "Unknown Scenario")
        game_state.description = scenario_data.get("description", "")
        game_state.map_id = scenario_data.get("map_id", "default")
        
        # Load units
        units_data = scenario_data.get("units", [])
        for unit_data in units_data:
            self._load_unit(unit_data, game_state, sprite_manager)
        
        return game_state
    
    def _validate_scenario(self, scenario_data: Dict) -> None:
        """Validate scenario data structure."""
        required_fields = ["name", "units"]
        for field in required_fields:
            if field not in scenario_data:
                raise ValueError(f"Scenario missing required field: {field}")
        
        if not isinstance(scenario_data["units"], list):
            raise ValueError("Scenario units must be a list")
        
        # Validate each unit
        for i, unit_data in enumerate(scenario_data["units"]):
            self._validate_unit(unit_data, i)
    
    def _validate_unit(self, unit_data: Dict, unit_index: int) -> None:
        """Validate unit data structure."""
        required_fields = ["name", "team", "sprite", "x", "y"]
        for field in required_fields:
            if field not in unit_data:
                raise ValueError(f"Unit {unit_index} missing required field: {field}")
        
        # Validate sprite
        sprite = unit_data["sprite"]
        if sprite not in self.supported_sprites:
            print(f"⚠️  Warning: Unit {unit_data['name']} uses unsupported sprite '{sprite}'")
        
        # Validate team
        team = unit_data["team"]
        if team not in ["player", "enemy", "neutral"]:
            raise ValueError(f"Unit {unit_data['name']} has invalid team: {team}")
        
        # Validate coordinates
        x, y = unit_data["x"], unit_data["y"]
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError(f"Unit {unit_data['name']} has invalid coordinates: ({x}, {y})")
        
        # Validate AI type if present
        if "ai" in unit_data:
            ai_type = unit_data["ai"]
            if ai_type not in self.supported_ai_types:
                print(f"⚠️  Warning: Unit {unit_data['name']} uses unsupported AI type '{ai_type}'")
    
    def _load_unit(self, unit_data: Dict, game_state: GameState, sprite_manager: SpriteManager) -> None:
        """Load a unit from scenario data."""
        
        # Create unit
        unit = Unit(
            name=unit_data["name"],
            x=unit_data["x"],
            y=unit_data["y"],
            team=unit_data["team"],
            health=unit_data.get("hp", 10)
        )
        
        # Set HP
        unit.hp = unit_data.get("hp", unit.health)
        
        # Set initial animation
        initial_animation = unit_data.get("animation", "idle")
        unit.set_animation(initial_animation)
        
        # Add unit to game state with additional data
        game_state.add_unit(unit.name, unit.team, ap=unit_data.get("ap", 3), hp=unit.hp)
        
        # Store additional unit data in the unit manager
        unit_info = game_state.units.units[unit.name]
        unit_info.update({
            "x": unit_data["x"],
            "y": unit_data["y"],
            "sprite": unit_data["sprite"],
            "animation": unit_data.get("animation", "idle"),
            "ai": unit_data.get("ai", None)
        })
        
        # Set AI behavior if specified
        if "ai" in unit_data:
            ai_type = unit_data["ai"]
            # TODO: Implement AI behavior setting
            print(f"📋 Unit {unit.name} has AI behavior: {ai_type}")
        
        print(f"✅ Loaded unit: {unit.name} ({unit.team}) at ({unit.x}, {unit.y}) with {unit.hp} HP")

def load_scenario(scenario_path: str, sprite_manager: SpriteManager, 
                 fx_manager: FXManager, sound_manager: SoundManager) -> GameState:
    """Convenience function to load a scenario."""
    loader = ScenarioLoader()
    return loader.load_scenario(scenario_path, sprite_manager, fx_manager, sound_manager)
