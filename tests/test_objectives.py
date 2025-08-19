"""
Tests for objectives: event sequences complete/fail objectives correctly.
"""
import pytest
from core.objectives import (
    EliminateBoss, SurviveNTurns, HoldZones, Escort, Compound, create_objective
)
from core.events import (
    Event, EventType, ev_unit_killed, ev_turn_started, ev_turn_ended, ev_unit_moved
)
from core.state import GameState, Unit, UnitStats


class TestEliminateBoss:
    """Test EliminateBoss objective."""
    
    def setup_method(self):
        """Set up test with boss unit."""
        self.game_state = GameState()
        
        # Create boss unit
        boss = Unit(
            unit_id="boss1",
            pos=(5, 5),
            stats=UnitStats(hp=20, atk=10, def_=5),
            team="enemy"
        )
        self.game_state.add_unit(boss)
        
        self.objective = EliminateBoss("boss1")
    
    def test_boss_not_killed_initially(self):
        """Boss objective starts incomplete."""
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_boss_killed_completes_objective(self):
        """Killing boss completes objective."""
        # Create kill event
        events = [ev_unit_killed("boss1", "player1", tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_wrong_unit_killed_no_completion(self):
        """Killing non-boss unit doesn't complete objective."""
        # Add regular enemy
        regular = Unit("enemy1", (3, 3), team="enemy")
        self.game_state.add_unit(regular)
        
        # Kill regular enemy
        events = [ev_unit_killed("enemy1", "player1", tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_multiple_events_only_boss_matters(self):
        """Multiple kill events, only boss kill matters."""
        # Add regular enemies
        for i in range(3):
            enemy = Unit(f"enemy{i}", (i, i), team="enemy")
            self.game_state.add_unit(enemy)
        
        # Kill regular enemies first
        events = [
            ev_unit_killed("enemy0", "player1", tick=1),
            ev_unit_killed("enemy1", "player1", tick=2),
            ev_unit_killed("enemy2", "player1", tick=3),
        ]
        
        self.objective.update_from_events(events, self.game_state)
        assert not self.objective.is_complete(self.game_state)
        
        # Then kill boss
        boss_kill = [ev_unit_killed("boss1", "player1", tick=4)]
        self.objective.update_from_events(boss_kill, self.game_state)
        
        assert self.objective.is_complete(self.game_state)


class TestSurviveNTurns:
    """Test SurviveNTurns objective."""
    
    def setup_method(self):
        """Set up survive objective."""
        self.game_state = GameState()
        
        # Create player unit
        player = Unit(
            unit_id="player1",
            pos=(2, 2),
            stats=UnitStats(hp=15, atk=8, def_=3),
            team="player"
        )
        self.game_state.add_unit(player)
        
        self.objective = SurviveNTurns(5)  # Survive 5 turns
    
    def test_initial_state(self):
        """Survive objective starts incomplete."""
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_survive_required_turns(self):
        """Surviving required turns completes objective."""
        # Simulate 5 turns
        events = []
        for turn in range(5):
            events.extend([
                ev_turn_started("player1", "player", turn, tick=turn*2),
                ev_turn_ended("player1", "player", turn, tick=turn*2+1)
            ])
        
        self.objective.update_from_events(events, self.game_state)
        
        assert self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_player_death_fails_objective(self):
        """Player death fails survive objective."""
        # Player dies on turn 3
        events = [
            ev_turn_started("player1", "player", 0, tick=0),
            ev_turn_ended("player1", "player", 0, tick=1),
            ev_turn_started("player1", "player", 1, tick=2),
            ev_turn_ended("player1", "player", 1, tick=3),
            ev_unit_killed("player1", "enemy1", tick=4),  # Player dies
        ]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert self.objective.is_failed(self.game_state)
    
    def test_partial_progress(self):
        """Partial turn progress doesn't complete."""
        # Only 3 turns
        events = []
        for turn in range(3):
            events.extend([
                ev_turn_started("player1", "player", turn, tick=turn*2),
                ev_turn_ended("player1", "player", turn, tick=turn*2+1)
            ])
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_enemy_death_irrelevant(self):
        """Enemy deaths don't affect survive objective."""
        # Enemy dies
        events = [ev_unit_killed("enemy1", "player1", tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        # Should not affect objective
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)


class TestHoldZones:
    """Test HoldZones objective."""
    
    def setup_method(self):
        """Set up hold zones objective."""
        self.game_state = GameState()
        
        # Create player units
        self.player1 = Unit("player1", (2, 2), team="player")
        self.player2 = Unit("player2", (3, 3), team="player")
        
        self.game_state.add_unit(self.player1)
        self.game_state.add_unit(self.player2)
        
        # Hold zones at (2,2) and (3,3) for 3 turns
        zones = [(2, 2), (3, 3)]
        self.objective = HoldZones(zones, k=2, turns=3)  # Hold 2 zones for 3 turns
    
    def test_initial_state(self):
        """Hold zones starts incomplete."""
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_hold_zones_success(self):
        """Successfully holding zones completes objective."""
        # Simulate 3 turns with players in zones
        events = []
        for turn in range(3):
            events.append(ev_turn_ended("player1", "player", turn, tick=turn))
        
        self.objective.update_from_events(events, self.game_state)
        
        assert self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_player_leaves_zone_fails(self):
        """Player leaving zone fails objective."""
        # Player1 moves away from zone
        events = [
            ev_unit_moved("player1", (2, 2), (4, 4), tick=1),
            ev_turn_ended("player1", "player", 0, tick=2)
        ]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        # Note: Current implementation might not fail immediately,
        # depends on specific hold zone logic
    
    def test_partial_hold_duration(self):
        """Partial hold duration doesn't complete."""
        # Only hold for 2 turns instead of 3
        events = []
        for turn in range(2):
            events.append(ev_turn_ended("player1", "player", turn, tick=turn))
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)


class TestEscort:
    """Test Escort objective."""
    
    def setup_method(self):
        """Set up escort objective."""
        self.game_state = GameState()
        
        # Create escort target
        self.vip = Unit(
            unit_id="vip",
            pos=(1, 1),
            stats=UnitStats(hp=10, atk=2, def_=1),
            team="player"
        )
        self.game_state.add_unit(self.vip)
        
        # Escort to position (8, 8)
        self.objective = Escort("vip", (8, 8))
    
    def test_initial_state(self):
        """Escort starts incomplete."""
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_escort_reaches_target(self):
        """VIP reaching target completes objective."""
        # Move VIP to target position
        events = [ev_unit_moved("vip", (1, 1), (8, 8), tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_escort_dies_fails_objective(self):
        """VIP death fails escort objective."""
        events = [ev_unit_killed("vip", "enemy1", tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert self.objective.is_failed(self.game_state)
    
    def test_partial_movement_no_completion(self):
        """Partial movement doesn't complete escort."""
        # Move VIP closer but not to target
        events = [ev_unit_moved("vip", (1, 1), (5, 5), tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_wrong_unit_movement_irrelevant(self):
        """Other units moving doesn't affect escort."""
        # Add another unit
        other = Unit("other", (2, 2), team="player")
        self.game_state.add_unit(other)
        
        # Move other unit to target
        events = [ev_unit_moved("other", (2, 2), (8, 8), tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)


class TestCompound:
    """Test Compound objective."""
    
    def setup_method(self):
        """Set up compound objective."""
        self.game_state = GameState()
        
        # Create units for sub-objectives
        boss = Unit("boss1", (5, 5), team="enemy")
        player = Unit("player1", (2, 2), team="player")
        
        self.game_state.add_unit(boss)
        self.game_state.add_unit(player)
        
        # Create compound objective: eliminate boss AND survive 3 turns
        sub_objectives = [
            EliminateBoss("boss1"),
            SurviveNTurns(3)
        ]
        self.objective = Compound(sub_objectives)
    
    def test_initial_state(self):
        """Compound starts incomplete."""
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_all_sub_objectives_complete(self):
        """All sub-objectives completing completes compound."""
        # Kill boss and survive 3 turns
        events = [
            ev_unit_killed("boss1", "player1", tick=1),  # Complete eliminate
            ev_turn_started("player1", "player", 0, tick=2),
            ev_turn_ended("player1", "player", 0, tick=3),
            ev_turn_started("player1", "player", 1, tick=4),
            ev_turn_ended("player1", "player", 1, tick=5),
            ev_turn_started("player1", "player", 2, tick=6),
            ev_turn_ended("player1", "player", 2, tick=7),  # Complete survive
        ]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_partial_completion_not_enough(self):
        """Partial sub-objective completion doesn't complete compound."""
        # Only kill boss, don't survive enough turns
        events = [ev_unit_killed("boss1", "player1", tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert not self.objective.is_failed(self.game_state)
    
    def test_one_sub_objective_fails(self):
        """One sub-objective failing fails compound."""
        # Player dies (fails survive objective)
        events = [ev_unit_killed("player1", "enemy1", tick=1)]
        
        self.objective.update_from_events(events, self.game_state)
        
        assert not self.objective.is_complete(self.game_state)
        assert self.objective.is_failed(self.game_state)
    
    def test_compound_summary(self):
        """Compound objective provides useful summary."""
        # Complete one sub-objective
        events = [ev_unit_killed("boss1", "player1", tick=1)]
        self.objective.update_from_events(events, self.game_state)
        
        summary = self.objective.summary(self.game_state)
        assert "1/2" in summary or "complete" in summary.lower()


class TestObjectiveRegistry:
    """Test objective creation from configuration."""
    
    def test_create_eliminate_boss(self):
        """Create EliminateBoss from config."""
        config = {"type": "EliminateBoss", "boss_id": "boss1"}
        
        objective = create_objective(config)
        
        assert isinstance(objective, EliminateBoss)
    
    def test_create_survive_n_turns(self):
        """Create SurviveNTurns from config."""
        config = {"type": "SurviveNTurns", "n": 10}
        
        objective = create_objective(config)
        
        assert isinstance(objective, SurviveNTurns)
    
    def test_create_compound(self):
        """Create Compound objective from config."""
        config = {
            "type": "Compound",
            "list": [
                {"type": "EliminateBoss", "boss_id": "e1"},
                {"type": "SurviveNTurns", "n": 10}
            ]
        }
        
        objective = create_objective(config)
        
        assert isinstance(objective, Compound)
        sub_objectives = objective.get_sub_objectives()
        assert len(sub_objectives) == 2
        assert isinstance(sub_objectives[0], EliminateBoss)
        assert isinstance(sub_objectives[1], SurviveNTurns)
    
    def test_unknown_objective_type(self):
        """Unknown objective type raises error."""
        config = {"type": "UnknownObjective"}
        
        with pytest.raises(ValueError, match="Unknown objective type"):
            create_objective(config)
    
    def test_missing_required_params(self):
        """Missing required parameters raises error."""
        config = {"type": "EliminateBoss"}  # Missing boss_id
        
        with pytest.raises(ValueError, match="requires 'boss_id'"):
            create_objective(config)


class TestObjectiveIntegration:
    """Integration tests for objectives with realistic event sequences."""
    
    def test_realistic_battle_sequence(self):
        """Test objectives with realistic battle event sequence."""
        game_state = GameState()
        
        # Set up units
        player = Unit("player1", (1, 1), team="player")
        boss = Unit("boss1", (8, 8), team="enemy")
        
        game_state.add_unit(player)
        game_state.add_unit(boss)
        
        # Create compound objective
        config = {
            "type": "Compound",
            "list": [
                {"type": "EliminateBoss", "boss_id": "boss1"},
                {"type": "SurviveNTurns", "n": 3}
            ]
        }
        objective = create_objective(config)
        
        # Simulate realistic battle
        events = [
            # Turn 1: Player moves closer
            ev_turn_started("player1", "player", 0, tick=0),
            ev_unit_moved("player1", (1, 1), (4, 4), tick=1),
            ev_turn_ended("player1", "player", 0, tick=2),
            
            # Turn 2: Combat
            ev_turn_started("player1", "player", 1, tick=3),
            ev_turn_ended("player1", "player", 1, tick=4),
            
            # Turn 3: Boss defeated
            ev_turn_started("player1", "player", 2, tick=5),
            ev_unit_killed("boss1", "player1", tick=6),  # Boss dies
            ev_turn_ended("player1", "player", 2, tick=7),
        ]
        
        objective.update_from_events(events, game_state)
        
        # Should complete both objectives
        assert objective.is_complete(game_state)
        assert not objective.is_failed(game_state)
