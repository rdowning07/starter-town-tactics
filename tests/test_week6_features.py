"""
Unit tests for Week 6 features.
Tests enemy AI, scenario manager, asset validator, and integration.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pygame
import yaml

from game.ai.enemy_ai import AIBehaviorType, EnemyAI
from game.asset_validator import AssetValidationResult, AssetValidator
from game.scenario_manager import ScenarioManager, ScenarioStep

# Initialize pygame for testing
pygame.init()


class TestWeek6Features(unittest.TestCase):
    def setUp(self):
        # Create mock game state
        self.game_state = Mock()
        self.game_state.units = Mock()
        self.game_state.units.units = {
            "player_1": {
                "x": 2,
                "y": 2,
                "hp": 20,
                "max_hp": 20,
                "team": "player",
                "alive": True,
                "unit_id": "player_1",
            },
            "player_2": {
                "x": 3,
                "y": 3,
                "hp": 15,
                "max_hp": 15,
                "team": "player",
                "alive": True,
                "unit_id": "player_2",
            },
            "enemy_1": {"x": 5, "y": 5, "hp": 18, "max_hp": 18, "team": "enemy", "alive": True, "unit_id": "enemy_1"},
        }
        self.game_state.turn_count = 0

    # Enemy AI Tests
    def test_enemy_ai_initialization(self):
        """Test EnemyAI initialization."""
        ai = EnemyAI("enemy_1", AIBehaviorType.AGGRESSIVE)

        self.assertEqual(ai.unit_id, "enemy_1")
        self.assertEqual(ai.behavior_type, AIBehaviorType.AGGRESSIVE)
        self.assertEqual(ai.aggression_level, 1.0)
        self.assertEqual(len(ai.patrol_path), 0)
        self.assertEqual(len(ai.behavior_history), 0)

    def test_aggressive_behavior(self):
        """Test aggressive AI behavior."""
        logger = Mock()
        ai = EnemyAI("enemy_1", AIBehaviorType.AGGRESSIVE, logger)

        action = ai.decide_action(self.game_state)

        self.assertIn(action["action"], ["attack", "move", "wait"])
        if action["action"] == "attack":
            self.assertIn("target", action)
        elif action["action"] == "move":
            self.assertIn("target_pos", action)

    def test_defensive_behavior(self):
        """Test defensive AI behavior."""
        ai = EnemyAI("enemy_1", AIBehaviorType.DEFENSIVE)

        # Set enemy to low HP
        self.game_state.units.units["enemy_1"]["hp"] = 5

        action = ai.decide_action(self.game_state)

        self.assertIn(action["action"], ["move", "wait"])
        if action["action"] == "move":
            self.assertEqual(action["reason"], "retreating_low_hp")

    def test_patrol_behavior(self):
        """Test patrol AI behavior."""
        ai = EnemyAI("enemy_1", AIBehaviorType.PATROL)

        action = ai.decide_action(self.game_state)

        # Should either patrol or switch to aggressive if player nearby
        self.assertIn(action["action"], ["move", "attack", "wait"])

    def test_adaptive_behavior(self):
        """Test adaptive AI behavior."""
        ai = EnemyAI("enemy_1", AIBehaviorType.ADAPTIVE)

        action = ai.decide_action(self.game_state)

        # Adaptive should choose appropriate behavior based on threat
        self.assertIn(action["action"], ["move", "attack", "wait"])

    def test_support_behavior(self):
        """Test support AI behavior."""
        ai = EnemyAI("enemy_1", AIBehaviorType.SUPPORT)

        # Add wounded ally
        self.game_state.units.units["enemy_2"] = {
            "x": 6,
            "y": 6,
            "hp": 5,
            "max_hp": 20,
            "team": "enemy",
            "alive": True,
            "unit_id": "enemy_2",
        }

        action = ai.decide_action(self.game_state)

        self.assertIn(action["action"], ["support", "move", "wait"])

    def test_ai_pathfinding(self):
        """Test AI pathfinding logic."""
        ai = EnemyAI("enemy_1", AIBehaviorType.AGGRESSIVE)

        current_pos = (5, 5)
        target_pos = (2, 2)

        next_pos = ai._get_move_towards_target(current_pos, target_pos, self.game_state)

        self.assertIsNotNone(next_pos)
        # Should move closer to target
        old_distance = abs(current_pos[0] - target_pos[0]) + abs(current_pos[1] - target_pos[1])
        new_distance = abs(next_pos[0] - target_pos[0]) + abs(next_pos[1] - target_pos[1])
        self.assertLessEqual(new_distance, old_distance)

    def test_ai_threat_assessment(self):
        """Test AI threat level assessment."""
        ai = EnemyAI("enemy_1", AIBehaviorType.ADAPTIVE)
        unit_data = self.game_state.units.units["enemy_1"]
        player_units = [self.game_state.units.units["player_1"], self.game_state.units.units["player_2"]]

        threat_level = ai._assess_threat_level(unit_data, player_units)

        self.assertIsInstance(threat_level, float)
        self.assertGreaterEqual(threat_level, 0.0)
        self.assertLessEqual(threat_level, 1.0)

    def test_ai_behavior_history(self):
        """Test AI behavior history tracking."""
        ai = EnemyAI("enemy_1", AIBehaviorType.ADAPTIVE)

        action_result = {"action": "attack", "reason": "target_in_range"}
        ai.update_behavior_history(action_result, True)

        self.assertEqual(len(ai.behavior_history), 1)
        self.assertEqual(ai.behavior_history[0]["action"], "attack")
        self.assertTrue(ai.behavior_history[0]["success"])

    def test_ai_behavior_change(self):
        """Test changing AI behavior type."""
        logger = Mock()
        ai = EnemyAI("enemy_1", AIBehaviorType.AGGRESSIVE, logger)

        ai.set_behavior_type(AIBehaviorType.DEFENSIVE)

        self.assertEqual(ai.behavior_type, AIBehaviorType.DEFENSIVE)

    def test_ai_status_reporting(self):
        """Test AI status reporting."""
        ai = EnemyAI("enemy_1", AIBehaviorType.PATROL)

        status = ai.get_ai_status()

        self.assertIn("unit_id", status)
        self.assertIn("behavior_type", status)
        self.assertIn("aggression_level", status)
        self.assertEqual(status["unit_id"], "enemy_1")

    # Scenario Manager Tests
    def test_scenario_manager_initialization(self):
        """Test ScenarioManager initialization."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"name": "Test Scenario", "steps": [{"name": "Step 1", "enemies": []}]}, f)
            temp_file = f.name

        try:
            scenario_manager = ScenarioManager(temp_file)

            self.assertEqual(len(scenario_manager.steps), 1)
            self.assertEqual(scenario_manager.scenario_state["name"], "Test Scenario")
            self.assertEqual(scenario_manager.current_step_index, 0)
        finally:
            Path(temp_file).unlink()

    def test_scenario_step_creation(self):
        """Test ScenarioStep creation."""
        step_data = {
            "name": "Test Step",
            "description": "A test step",
            "enemies": [{"type": "goblin", "position": [5, 5]}],
            "objectives": ["Defeat enemies"],
        }

        step = ScenarioStep(step_data)

        self.assertEqual(step.name, "Test Step")
        self.assertEqual(step.description, "A test step")
        self.assertEqual(len(step.enemies), 1)
        self.assertEqual(len(step.objectives), 1)
        self.assertFalse(step.completed)

    def test_scenario_enemy_spawning(self):
        """Test enemy spawning in scenarios."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(
                {
                    "name": "Spawn Test",
                    "steps": [
                        {
                            "name": "Spawn Step",
                            "enemies": [{"type": "goblin", "position": [7, 7], "behavior": "aggressive"}],
                        }
                    ],
                },
                f,
            )
            temp_file = f.name

        try:
            logger = Mock()
            scenario_manager = ScenarioManager(temp_file, logger=logger)
            scenario_manager.start_scenario(self.game_state)

            result = scenario_manager.run_step(self.game_state)

            self.assertTrue(result["success"])
            self.assertIn("spawned_goblin", result["actions"])
            # Check if enemy was added to game state
            goblin_units = [uid for uid in self.game_state.units.units.keys() if uid.startswith("goblin")]
            self.assertGreater(len(goblin_units), 0)
        finally:
            Path(temp_file).unlink()

    def test_scenario_escalation(self):
        """Test scenario difficulty escalation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(
                {
                    "name": "Escalation Test",
                    "steps": [
                        {
                            "name": "Escalation Step",
                            "enemies": [{"type": "orc", "position": [6, 6]}],
                            "escalation": {"enemy_hp_multiplier": 1.5, "enemy_damage_multiplier": 1.2},
                        }
                    ],
                },
                f,
            )
            temp_file = f.name

        try:
            scenario_manager = ScenarioManager(temp_file)
            scenario_manager.start_scenario(self.game_state)
            initial_escalation = scenario_manager.escalation_level

            scenario_manager.run_step(self.game_state)

            self.assertGreater(scenario_manager.escalation_level, initial_escalation)
        finally:
            Path(temp_file).unlink()

    def test_scenario_step_completion(self):
        """Test scenario step completion checking."""
        scenario_manager = ScenarioManager("nonexistent.yaml")  # Will create default
        scenario_manager.start_scenario(self.game_state)

        # Kill all enemies
        for unit_data in self.game_state.units.units.values():
            if unit_data.get("team") == "enemy":
                unit_data["alive"] = False

        is_complete = scenario_manager.check_step_completion(self.game_state)

        self.assertTrue(is_complete)

    def test_scenario_ai_processing(self):
        """Test AI turn processing in scenarios."""
        scenario_manager = ScenarioManager("nonexistent.yaml")
        scenario_manager.active_ais["enemy_1"] = EnemyAI("enemy_1", AIBehaviorType.AGGRESSIVE)

        ai_actions = scenario_manager.process_ai_turns(self.game_state)

        self.assertIsInstance(ai_actions, list)
        if ai_actions:
            self.assertIn("unit_id", ai_actions[0])
            self.assertIn("action", ai_actions[0])

    def test_scenario_status_reporting(self):
        """Test scenario status reporting."""
        scenario_manager = ScenarioManager("nonexistent.yaml")

        status = scenario_manager.get_scenario_status()

        self.assertIn("scenario_name", status)
        self.assertIn("current_step_index", status)
        self.assertIn("total_steps", status)
        self.assertIn("escalation_level", status)

    def test_scenario_reset(self):
        """Test scenario reset functionality."""
        scenario_manager = ScenarioManager("nonexistent.yaml")
        scenario_manager.current_step_index = 1
        scenario_manager.escalation_level = 2.0

        scenario_manager.reset_scenario()

        self.assertEqual(scenario_manager.current_step_index, 0)
        self.assertEqual(scenario_manager.escalation_level, 1.0)

    # Asset Validator Tests
    def test_asset_validator_initialization(self):
        """Test AssetValidator initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            asset_dir = Path(temp_dir)
            validator = AssetValidator(asset_dir)

            self.assertEqual(validator.asset_dir, asset_dir)
            self.assertIn("terrain", validator.validation_rules)
            self.assertIn("units", validator.validation_rules)

    def test_asset_validation_result(self):
        """Test AssetValidationResult functionality."""
        result = AssetValidationResult("test/path.png")

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

        result.add_error("Test error")

        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0], "Test error")

    def test_asset_validation_rules(self):
        """Test asset validation rules creation."""
        validator = AssetValidator()
        rules = validator.validation_rules

        self.assertIn("terrain", rules)
        self.assertIn("units", rules)
        self.assertIn("ui", rules)

        # Check terrain rules
        terrain_rules = rules["terrain"]
        self.assertEqual(terrain_rules["expected_resolution"], (32, 32))
        self.assertIn(".png", terrain_rules["allowed_extensions"])

    @patch("PIL.Image.open")
    def test_image_validation(self, mock_image_open):
        """Test image file validation."""
        # Mock image
        mock_img = Mock()
        mock_img.size = (32, 32)
        mock_img.format = "PNG"
        mock_img.mode = "RGBA"
        mock_image_open.return_value.__enter__.return_value = mock_img

        validator = AssetValidator()
        result = AssetValidationResult("test.png")
        rules = validator.validation_rules["terrain"]

        validator._validate_image_file(Path("test.png"), rules, result)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.metadata["resolution"], (32, 32))
        self.assertEqual(result.metadata["format"], "PNG")

    @patch("PIL.Image.open")
    def test_image_validation_wrong_size(self, mock_image_open):
        """Test image validation with wrong size."""
        # Mock image with wrong size
        mock_img = Mock()
        mock_img.size = (64, 64)  # Wrong size for terrain
        mock_img.format = "PNG"
        mock_img.mode = "RGBA"
        mock_image_open.return_value.__enter__.return_value = mock_img

        validator = AssetValidator()
        result = AssetValidationResult("test.png")
        rules = validator.validation_rules["terrain"]

        validator._validate_image_file(Path("test.png"), rules, result)

        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)

    def test_duplicate_detection(self):
        """Test duplicate file detection."""
        validator = AssetValidator()
        validator.duplicate_hashes = {"hash1": ["file1.png", "file2.png"], "hash2": ["file3.png"]}

        all_results = {"terrain": [AssetValidationResult("file1.png"), AssetValidationResult("file2.png")]}

        validator._check_for_duplicates(all_results)

        # Should add warnings to duplicate files
        for result in all_results["terrain"]:
            if result.asset_path in ["file1.png", "file2.png"]:
                self.assertGreater(len(result.warnings), 0)

    def test_scenario_asset_validation(self):
        """Test validation of assets referenced in scenarios."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"steps": [{"enemies": [{"type": "goblin"}, {"type": "orc"}]}]}, f)
            temp_file = f.name

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                validator = AssetValidator(Path(temp_dir))
                results = validator.validate_scenario_assets(Path(temp_file))

                self.assertGreater(len(results), 0)
                # Should find missing asset references
                for result in results:
                    if "goblin" in result.asset_path or "orc" in result.asset_path:
                        self.assertFalse(result.is_valid)
        finally:
            Path(temp_file).unlink()

    def test_asset_manifest_generation(self):
        """Test asset manifest generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            asset_dir = Path(temp_dir)

            # Create some test assets
            (asset_dir / "terrain").mkdir()
            (asset_dir / "terrain" / "grass.png").touch()

            validator = AssetValidator(asset_dir)
            manifest = validator.generate_asset_manifest()

            self.assertIn("version", manifest)
            self.assertIn("asset_types", manifest)
            self.assertIn("total_assets", manifest)

    def test_validation_summary(self):
        """Test validation summary generation."""
        validator = AssetValidator()

        # Mock some validation results
        validator.validation_results = {
            "terrain": [AssetValidationResult("file1.png"), AssetValidationResult("file2.png")]
        }
        validator.validation_results["terrain"][1].add_error("Test error")

        summary = validator.get_validation_summary()

        self.assertEqual(summary["total_assets"], 2)
        self.assertEqual(summary["valid_assets"], 1)
        self.assertEqual(summary["success_rate"], 50.0)

    # Integration Tests
    def test_ai_scenario_integration(self):
        """Test integration between AI and scenario systems."""
        # Create AI
        ai = EnemyAI("enemy_1", AIBehaviorType.AGGRESSIVE)

        # Create scenario manager
        scenario_manager = ScenarioManager("nonexistent.yaml")
        scenario_manager.active_ais["enemy_1"] = ai

        # Process AI turn
        ai_actions = scenario_manager.process_ai_turns(self.game_state)

        # Should get valid AI actions
        self.assertIsInstance(ai_actions, list)

    def test_scenario_asset_integration(self):
        """Test integration between scenario and asset validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"steps": [{"enemies": [{"type": "test_unit"}]}]}, f)
            temp_file = f.name

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Test scenario loading with asset validation
                scenario_manager = ScenarioManager(temp_file)
                validator = AssetValidator(Path(temp_dir))

                # Validate scenario assets
                results = validator.validate_scenario_assets(Path(temp_file))

                # Should find missing assets referenced in scenario
                missing_assets = [r for r in results if not r.is_valid]
                self.assertGreater(len(missing_assets), 0)
        finally:
            Path(temp_file).unlink()


if __name__ == "__main__":
    unittest.main()
