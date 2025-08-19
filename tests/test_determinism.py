"""
Tests for determinism: given (seed, scenario), replay same command log → identical end-state hash.
"""
import pytest
import hashlib
import json
from core.rng import Rng
from core.state import GameState, Unit, UnitStats
from core.events import EventBus
from core.game_loop import GameLoop
from core.command import Move, Attack, EndTurn
from core.objectives import create_objective


class MockController:
    """Mock controller that replays a predefined command sequence."""
    
    def __init__(self, command_log):
        self.command_log = command_log
        self.command_index = 0
    
    def decide(self, state):
        if self.command_index >= len(self.command_log):
            return EndTurn("player1")  # Default action
        
        command = self.command_log[self.command_index]
        self.command_index += 1
        return command
    
    def reset(self):
        """Reset controller for replay."""
        self.command_index = 0


def create_test_scenario(seed=1337):
    """Create a deterministic test scenario."""
    game_state = GameState()
    
    # Create units
    player = Unit(
        unit_id="player1",
        pos=(2, 2),
        stats=UnitStats(hp=20, atk=8, def_=3, h=0),
        team="player"
    )
    
    enemy = Unit(
        unit_id="enemy1", 
        pos=(6, 6),
        stats=UnitStats(hp=15, atk=6, def_=2, h=0),
        team="enemy"
    )
    
    game_state.add_unit(player)
    game_state.add_unit(enemy)
    
    # Set up RNG with fixed seed
    rng = Rng(seed)
    
    # Create objective
    objective_config = {
        "type": "Compound",
        "list": [
            {"type": "EliminateBoss", "boss_id": "enemy1"},
            {"type": "SurviveNTurns", "n": 5}
        ]
    }
    objective = create_objective(objective_config)
    game_state.objectives = objective
    
    return game_state, rng


def compute_game_state_hash(game_state):
    """Compute deterministic hash of game state."""
    state_data = {
        "tick": game_state.tick,
        "is_over": game_state.is_over(),
        "turn_index": game_state.turn_controller.turn_index,
        "current_unit": game_state.turn_controller.current_unit_id,
        "current_side": game_state.turn_controller.current_side,
        "units": {}
    }
    
    # Add unit data
    for unit_id, unit in game_state._units.items():
        state_data["units"][unit_id] = {
            "pos": unit.pos,
            "hp": unit.stats.hp,
            "atk": unit.stats.atk,
            "def": unit.stats.def_,
            "h": unit.stats.h,
            "status": sorted([str(s) for s in unit.status]),  # Sort for consistency
            "team": unit.team
        }
    
    # Add objective state if available
    if hasattr(game_state, 'objectives') and game_state.objectives:
        state_data["objective_complete"] = game_state.objectives.is_complete(game_state)
        state_data["objective_failed"] = game_state.objectives.is_failed(game_state)
    
    # Convert to deterministic JSON and hash
    state_json = json.dumps(state_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(state_json.encode()).hexdigest()


class TestBasicDeterminism:
    """Basic determinism tests."""
    
    def test_same_seed_same_initial_state(self):
        """Same seed produces same initial state."""
        state1, rng1 = create_test_scenario(seed=42)
        state2, rng2 = create_test_scenario(seed=42)
        
        hash1 = compute_game_state_hash(state1)
        hash2 = compute_game_state_hash(state2)
        
        assert hash1 == hash2
    
    def test_different_seed_different_state(self):
        """Different seeds can produce different states."""
        state1, rng1 = create_test_scenario(seed=42)
        state2, rng2 = create_test_scenario(seed=99)
        
        # Initial states should be same (seed only affects RNG, not setup)
        hash1 = compute_game_state_hash(state1)
        hash2 = compute_game_state_hash(state2)
        
        assert hash1 == hash2  # Setup is deterministic regardless of RNG seed
    
    def test_rng_determinism(self):
        """RNG produces same sequence with same seed."""
        rng1 = Rng(123)
        rng2 = Rng(123)
        
        # Generate same sequence
        sequence1 = [rng1.randint(1, 100) for _ in range(10)]
        sequence2 = [rng2.randint(1, 100) for _ in range(10)]
        
        assert sequence1 == sequence2
    
    def test_rng_different_seeds(self):
        """RNG produces different sequences with different seeds."""
        rng1 = Rng(123)
        rng2 = Rng(456)
        
        sequence1 = [rng1.randint(1, 100) for _ in range(10)]
        sequence2 = [rng2.randint(1, 100) for _ in range(10)]
        
        # Should be different (extremely unlikely to be same)
        assert sequence1 != sequence2


class TestCommandReplay:
    """Test command replay determinism."""
    
    def setup_method(self):
        """Set up test scenario."""
        self.seed = 1337
        self.command_log = [
            Move("player1", (3, 3)),
            EndTurn("player1"),
            Move("player1", (4, 4)),
            EndTurn("player1"),
            Move("player1", (5, 5)),
            EndTurn("player1"),
            Attack("player1", "enemy1"),
            EndTurn("player1"),
            Attack("player1", "enemy1"),
            EndTurn("player1"),
        ]
    
    def run_simulation(self, seed, command_log, max_ticks=20):
        """Run simulation with given parameters."""
        game_state, rng = create_test_scenario(seed)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        
        controller = MockController(command_log)
        game_state.set_controller(controller)
        
        # Run simulation
        for _ in range(max_ticks):
            if game_state.is_over():
                break
            loop.tick(game_state)
        
        return game_state
    
    def test_identical_replay(self):
        """Identical seed and commands produce identical end state."""
        # Run simulation twice
        final_state1 = self.run_simulation(self.seed, self.command_log)
        final_state2 = self.run_simulation(self.seed, self.command_log)
        
        # Compute hashes
        hash1 = compute_game_state_hash(final_state1)
        hash2 = compute_game_state_hash(final_state2)
        
        assert hash1 == hash2
    
    def test_different_seed_different_outcome(self):
        """Different seed with same commands can produce different outcomes."""
        final_state1 = self.run_simulation(seed=1337, command_log=self.command_log)
        final_state2 = self.run_simulation(seed=9999, command_log=self.command_log)
        
        hash1 = compute_game_state_hash(final_state1)
        hash2 = compute_game_state_hash(final_state2)
        
        # May be same or different depending on RNG usage in rules
        # The key is that it's deterministic for each seed
        if hash1 == hash2:
            # If same, verify by running again
            final_state3 = self.run_simulation(seed=1337, command_log=self.command_log)
            final_state4 = self.run_simulation(seed=9999, command_log=self.command_log)
            
            hash3 = compute_game_state_hash(final_state3)
            hash4 = compute_game_state_hash(final_state4)
            
            assert hash1 == hash3  # Same seed = same result
            assert hash2 == hash4  # Same seed = same result
    
    def test_different_commands_different_outcome(self):
        """Different commands produce different outcomes."""
        # Alternative command sequence
        alt_commands = [
            Move("player1", (2, 3)),
            EndTurn("player1"),
            Move("player1", (2, 4)),
            EndTurn("player1"),
            Attack("player1", "enemy1"),
            EndTurn("player1"),
        ]
        
        final_state1 = self.run_simulation(self.seed, self.command_log)
        final_state2 = self.run_simulation(self.seed, alt_commands)
        
        hash1 = compute_game_state_hash(final_state1)
        hash2 = compute_game_state_hash(final_state2)
        
        assert hash1 != hash2
    
    def test_partial_replay_consistency(self):
        """Partial replay produces consistent intermediate states."""
        # Run full simulation
        full_state = self.run_simulation(self.seed, self.command_log, max_ticks=20)
        
        # Run partial simulation (fewer ticks)
        partial_state = self.run_simulation(self.seed, self.command_log[:5], max_ticks=10)
        
        # States should be consistent (partial should be valid intermediate state)
        # This is more of a sanity check than strict determinism test
        assert partial_state.tick <= full_state.tick
        assert not partial_state.is_over() or full_state.is_over()


class TestComplexDeterminism:
    """More complex determinism scenarios."""
    
    def test_combat_determinism(self):
        """Combat outcomes are deterministic."""
        command_log = [
            Move("player1", (5, 5)),  # Move next to enemy
            EndTurn("player1"),
            Attack("player1", "enemy1"),  # Attack enemy
            EndTurn("player1"),
            Attack("player1", "enemy1"),  # Attack again
            EndTurn("player1"),
        ]
        
        # Run multiple times with same seed
        results = []
        for _ in range(3):
            final_state = self.run_simulation_with_combat(1234, command_log)
            results.append(compute_game_state_hash(final_state))
        
        # All results should be identical
        assert len(set(results)) == 1
    
    def run_simulation_with_combat(self, seed, command_log):
        """Run simulation focusing on combat determinism."""
        game_state, rng = create_test_scenario(seed)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        
        # Track combat events
        combat_events = []
        
        def combat_logger(event):
            if event.type.value in ["UNIT_ATTACKED", "UNIT_KILLED"]:
                combat_events.append(event)
        
        bus.subscribe(combat_logger)
        
        controller = MockController(command_log)
        game_state.set_controller(controller)
        
        # Run simulation
        for _ in range(15):
            if game_state.is_over():
                break
            loop.tick(game_state)
        
        return game_state
    
    def test_status_effect_determinism(self):
        """Status effects are applied deterministically."""
        # This test would require setting up status effects
        # For now, verify basic state consistency
        
        game_state, rng = create_test_scenario(1111)
        
        # Apply status effect to unit
        player = game_state.unit("player1")
        from core.rules.status import Status
        player.status = [Status.POISON]
        
        # Compute initial hash
        initial_hash = compute_game_state_hash(game_state)
        
        # Apply status effects multiple times (should be deterministic)
        from core.rules.status import on_unit_turn_start
        
        hashes = [initial_hash]
        for _ in range(3):
            on_unit_turn_start(game_state, "player1")
            hashes.append(compute_game_state_hash(game_state))
        
        # Create fresh state and apply same sequence
        game_state2, rng2 = create_test_scenario(1111)
        player2 = game_state2.unit("player1")
        player2.status = [Status.POISON]
        
        hashes2 = [compute_game_state_hash(game_state2)]
        for _ in range(3):
            on_unit_turn_start(game_state2, "player1")
            hashes2.append(compute_game_state_hash(game_state2))
        
        assert hashes == hashes2
    
    def test_objective_state_determinism(self):
        """Objective state changes are deterministic."""
        command_log = [
            Attack("player1", "enemy1"),
            EndTurn("player1"),
            Attack("player1", "enemy1"), 
            EndTurn("player1"),
            Attack("player1", "enemy1"),
            EndTurn("player1"),
        ]
        
        # Run simulation multiple times
        results = []
        for _ in range(3):
            game_state, rng = create_test_scenario(2468)
            bus = EventBus()
            loop = GameLoop(rng, bus)
            
            controller = MockController(command_log)
            game_state.set_controller(controller)
            
            # Run simulation
            for _ in range(10):
                if game_state.is_over():
                    break
                loop.tick(game_state)
            
            # Include objective state in hash
            results.append(compute_game_state_hash(game_state))
        
        # All results should be identical
        assert len(set(results)) == 1


class TestPerformanceAndLimits:
    """Test performance and edge cases for determinism."""
    
    def test_fast_execution(self):
        """Determinism tests should be fast (<1s total)."""
        import time
        
        start_time = time.time()
        
        # Run a quick determinism test
        command_log = [
            Move("player1", (3, 3)),
            Attack("player1", "enemy1"),
            EndTurn("player1"),
        ]
        
        for _ in range(5):  # Multiple runs
            game_state, rng = create_test_scenario(123)
            bus = EventBus()
            loop = GameLoop(rng, bus)
            
            controller = MockController(command_log)
            game_state.set_controller(controller)
            
            for _ in range(5):  # Short simulation
                if game_state.is_over():
                    break
                loop.tick(game_state)
        
        elapsed = time.time() - start_time
        assert elapsed < 1.0  # Should complete in under 1 second
    
    def test_empty_command_log(self):
        """Handle empty command log gracefully."""
        final_state = self.run_basic_simulation(456, [])
        hash_result = compute_game_state_hash(final_state)
        
        # Should not crash and produce valid hash
        assert len(hash_result) == 64  # SHA256 hex length
    
    def test_very_long_command_log(self):
        """Handle very long command logs."""
        # Create long command sequence
        long_commands = []
        for i in range(50):
            if i % 3 == 0:
                long_commands.append(Move("player1", (2 + i % 5, 2 + i % 5)))
            elif i % 3 == 1:
                long_commands.append(Attack("player1", "enemy1"))
            else:
                long_commands.append(EndTurn("player1"))
        
        final_state = self.run_basic_simulation(789, long_commands)
        hash_result = compute_game_state_hash(final_state)
        
        assert len(hash_result) == 64
    
    def run_basic_simulation(self, seed, command_log, max_ticks=30):
        """Basic simulation runner."""
        game_state, rng = create_test_scenario(seed)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        
        controller = MockController(command_log)
        game_state.set_controller(controller)
        
        for _ in range(max_ticks):
            if game_state.is_over():
                break
            loop.tick(game_state)
        
        return game_state
