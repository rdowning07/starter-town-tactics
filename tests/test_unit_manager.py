import pytest
from game.unit_manager import UnitManager


def test_unit_manager_initialization():
    """Test that UnitManager initializes correctly."""
    um = UnitManager()
    assert um.units == {}
    assert um.fake_dead_units == set()


def test_register_unit():
    """Test registering a unit."""
    um = UnitManager()
    um.register_unit("unit1", "player", hp=15)
    
    assert "unit1" in um.units
    assert um.units["unit1"]["team"] == "player"
    assert um.units["unit1"]["hp"] == 15
    assert um.units["unit1"]["alive"] is True


def test_register_unit_default_hp():
    """Test registering a unit with default HP."""
    um = UnitManager()
    um.register_unit("unit1", "ai")
    
    assert um.units["unit1"]["hp"] == 10
    assert um.units["unit1"]["alive"] is True


def test_get_team():
    """Test getting a unit's team."""
    um = UnitManager()
    um.register_unit("unit1", "player")
    um.register_unit("unit2", "ai")
    
    assert um.get_team("unit1") == "player"
    assert um.get_team("unit2") == "ai"


def test_get_team_nonexistent():
    """Test getting team of nonexistent unit returns None."""
    um = UnitManager()
    assert um.get_team("nonexistent") is None


def test_get_hp():
    """Test getting a unit's HP."""
    um = UnitManager()
    um.register_unit("unit1", "player", hp=25)
    
    assert um.get_hp("unit1") == 25


def test_get_hp_nonexistent():
    """Test getting HP of nonexistent unit returns None."""
    um = UnitManager()
    assert um.get_hp("nonexistent") is None


def test_is_alive():
    """Test checking if a unit is alive."""
    um = UnitManager()
    um.register_unit("unit1", "player")
    
    assert um.is_alive("unit1") is True
    
    # Kill the unit
    um.damage_unit("unit1", 10)
    assert um.is_alive("unit1") is False


def test_is_alive_nonexistent():
    """Test checking if nonexistent unit is alive."""
    um = UnitManager()
    assert um.is_alive("nonexistent") is False


def test_is_effectively_alive():
    """Test checking if a unit is effectively alive (including fake dead)."""
    um = UnitManager()
    um.register_unit("unit1", "player")
    um.register_unit("unit2", "ai")
    
    # Normal alive unit
    assert um.is_effectively_alive("unit1") is True
    
    # Kill unit2 and mark as fake dead
    um.damage_unit("unit2", 10)
    assert um.is_effectively_alive("unit2") is False
    
    um.mark_as_fake_dead("unit2")
    assert um.is_effectively_alive("unit2") is True


def test_is_effectively_alive_nonexistent():
    """Test checking if nonexistent unit is effectively alive."""
    um = UnitManager()
    assert um.is_effectively_alive("nonexistent") is False


def test_any_alive():
    """Test checking if any units of a team are alive."""
    um = UnitManager()
    um.register_unit("p1", "player")
    um.register_unit("p2", "player")
    um.register_unit("ai1", "ai")
    
    # All teams have alive units
    assert um.any_alive("player") is True
    assert um.any_alive("ai") is True
    
    # Kill one player unit
    um.damage_unit("p1", 10)
    assert um.any_alive("player") is True  # p2 is still alive
    
    # Kill all player units
    um.damage_unit("p2", 10)
    assert um.any_alive("player") is False


def test_any_alive_no_units():
    """Test any_alive with no units."""
    um = UnitManager()
    assert um.any_alive("player") is False
    assert um.any_alive("ai") is False


def test_any_effectively_alive():
    """Test checking if any units of a team are effectively alive."""
    um = UnitManager()
    um.register_unit("p1", "player")
    um.register_unit("p2", "player")
    um.register_unit("ai1", "ai")
    
    # All teams have alive units
    assert um.any_effectively_alive("player") is True
    assert um.any_effectively_alive("ai") is True
    
    # Kill one player unit and mark as fake dead
    um.damage_unit("p1", 10)
    um.mark_as_fake_dead("p1")
    assert um.any_effectively_alive("player") is True  # p1 is fake dead, p2 is alive
    
    # Kill all player units
    um.damage_unit("p2", 10)
    assert um.any_effectively_alive("player") is True  # p1 is still fake dead
    
    # Unmark fake dead
    um.unmark_fake_dead("p1")
    assert um.any_effectively_alive("player") is False


def test_get_unit_ids_by_team():
    """Test getting unit IDs by team."""
    um = UnitManager()
    um.register_unit("p1", "player")
    um.register_unit("p2", "player")
    um.register_unit("ai1", "ai")
    um.register_unit("ai2", "ai")
    
    player_units = um.get_unit_ids_by_team("player")
    ai_units = um.get_unit_ids_by_team("ai")
    
    assert set(player_units) == {"p1", "p2"}
    assert set(ai_units) == {"ai1", "ai2"}


def test_get_unit_ids_by_team_empty():
    """Test getting unit IDs for team with no units."""
    um = UnitManager()
    assert um.get_unit_ids_by_team("player") == []
    assert um.get_unit_ids_by_team("ai") == []


def test_damage_unit():
    """Test damaging a unit."""
    um = UnitManager()
    um.register_unit("unit1", "player", hp=10)
    
    # Damage but don't kill
    um.damage_unit("unit1", 5)
    assert um.get_hp("unit1") == 5
    assert um.is_alive("unit1") is True
    
    # Damage to kill
    um.damage_unit("unit1", 5)
    assert um.get_hp("unit1") == 0
    assert um.is_alive("unit1") is False


def test_damage_unit_nonexistent():
    """Test damaging a nonexistent unit."""
    um = UnitManager()
    # Should not raise an exception
    um.damage_unit("nonexistent", 10)


def test_damage_unit_overkill():
    """Test damaging a unit beyond death."""
    um = UnitManager()
    um.register_unit("unit1", "player", hp=10)

    um.damage_unit("unit1", 15)
    assert um.get_hp("unit1") == 0  # HP should be clamped to 0, not negative
    assert not um.is_alive("unit1")


def test_mark_as_fake_dead():
    """Test marking a unit as fake dead."""
    um = UnitManager()
    um.register_unit("unit1", "player")
    
    # Initially not fake dead
    assert "unit1" not in um.fake_dead_units
    
    # Mark as fake dead
    um.mark_as_fake_dead("unit1")
    assert "unit1" in um.fake_dead_units
    
    # Mark again (should be idempotent)
    um.mark_as_fake_dead("unit1")
    assert "unit1" in um.fake_dead_units


def test_unmark_fake_dead():
    """Test unmarking a unit as fake dead."""
    um = UnitManager()
    um.register_unit("unit1", "player")
    
    # Mark as fake dead
    um.mark_as_fake_dead("unit1")
    assert "unit1" in um.fake_dead_units
    
    # Unmark
    um.unmark_fake_dead("unit1")
    assert "unit1" not in um.fake_dead_units
    
    # Unmark again (should be safe)
    um.unmark_fake_dead("unit1")
    assert "unit1" not in um.fake_dead_units


def test_fake_dead_with_actual_death():
    """Test interaction between fake dead and actual death."""
    um = UnitManager()
    um.register_unit("unit1", "player", hp=10)
    
    # Kill the unit
    um.damage_unit("unit1", 10)
    assert um.is_alive("unit1") is False
    assert um.is_effectively_alive("unit1") is False
    
    # Mark as fake dead
    um.mark_as_fake_dead("unit1")
    assert um.is_alive("unit1") is False
    assert um.is_effectively_alive("unit1") is True
    
    # Unmark fake dead
    um.unmark_fake_dead("unit1")
    assert um.is_alive("unit1") is False
    assert um.is_effectively_alive("unit1") is False


def test_get_all_units():
    """Test getting all units."""
    um = UnitManager()
    um.register_unit("p1", "player", hp=10)
    um.register_unit("ai1", "ai", hp=15)
    
    all_units = um.get_all_units()
    
    assert "p1" in all_units
    assert "ai1" in all_units
    assert all_units["p1"]["team"] == "player"
    assert all_units["ai1"]["team"] == "ai"
    assert all_units["p1"]["hp"] == 10
    assert all_units["ai1"]["hp"] == 15


def test_get_living_units():
    """Test getting living units."""
    um = UnitManager()
    um.register_unit("p1", "player")
    um.register_unit("p2", "player")
    um.register_unit("ai1", "ai")
    
    # All units alive
    living = um.get_living_units()
    assert set(living) == {"p1", "p2", "ai1"}
    
    # Kill one unit
    um.damage_unit("p1", 10)
    living = um.get_living_units()
    assert set(living) == {"p2", "ai1"}
    
    # Kill all units
    um.damage_unit("p2", 10)
    um.damage_unit("ai1", 10)
    living = um.get_living_units()
    assert living == []


def test_remove_unit():
    """Test removing a unit."""
    um = UnitManager()
    um.register_unit("unit1", "player", hp=10)
    
    assert um.is_alive("unit1") is True
    
    um.remove_unit("unit1")
    assert um.is_alive("unit1") is False


def test_remove_unit_nonexistent():
    """Test removing a nonexistent unit."""
    um = UnitManager()
    # Should not raise an exception
    um.remove_unit("nonexistent")


def test_remove_unit_already_dead():
    """Test removing an already dead unit."""
    um = UnitManager()
    um.register_unit("unit1", "player", hp=10)
    
    # Kill the unit
    um.damage_unit("unit1", 10)
    assert um.is_alive("unit1") is False
    
    # Remove it (should not change state)
    um.remove_unit("unit1")
    assert um.is_alive("unit1") is False


# === Edge Case Tests ===

def test_negative_hp_unit():
    """Test unit with negative HP raises ValueError."""
    um = UnitManager()
    with pytest.raises(ValueError, match="HP must be positive"):
        um.register_unit("unit1", "player", hp=-5)


def test_zero_hp_unit():
    """Test unit with zero HP raises ValueError."""
    um = UnitManager()
    with pytest.raises(ValueError, match="HP must be positive"):
        um.register_unit("unit1", "player", hp=0)


def test_duplicate_unit_registration():
    """Test registering a unit with duplicate ID."""
    um = UnitManager()
    um.register_unit("unit1", "player", hp=10)
    um.register_unit("unit1", "ai", hp=15)  # Overwrite
    
    assert um.get_team("unit1") == "ai"
    assert um.get_hp("unit1") == 15


def test_fake_dead_nonexistent_unit():
    """Test marking nonexistent unit as fake dead returns False."""
    um = UnitManager()
    
    # Should return False for nonexistent unit
    assert not um.mark_as_fake_dead("nonexistent")
    assert "nonexistent" not in um.fake_dead_units


# === Performance Tests ===

def test_performance_large_number_of_units():
    """Test performance with large number of units."""
    um = UnitManager()
    
    # Add 1000 units
    for i in range(1000):
        um.register_unit(f"unit_{i}", "player" if i % 2 == 0 else "ai", hp=10)
    
    # Test any_alive performance
    import time
    start_time = time.time()
    player_alive = um.any_alive("player")
    player_time = time.time() - start_time
    
    start_time = time.time()
    ai_alive = um.any_alive("ai")
    ai_time = time.time() - start_time
    
    # Should be fast even with 1000 units
    assert player_time < 0.1
    assert ai_time < 0.1
    assert player_alive is True
    assert ai_alive is True


def test_performance_effectively_alive():
    """Test performance of effectively alive checks."""
    um = UnitManager()
    
    # Add 500 units
    for i in range(500):
        um.register_unit(f"unit_{i}", "player" if i % 2 == 0 else "ai", hp=10)
    
    # Mark some as fake dead
    for i in range(0, 100, 2):
        um.mark_as_fake_dead(f"unit_{i}")
    
    import time
    start_time = time.time()
    player_effectively_alive = um.any_effectively_alive("player")
    player_time = time.time() - start_time
    
    start_time = time.time()
    ai_effectively_alive = um.any_effectively_alive("ai")
    ai_time = time.time() - start_time
    
    # Should be fast
    assert player_time < 0.1
    assert ai_time < 0.1
    assert player_effectively_alive is True
    assert ai_effectively_alive is True 