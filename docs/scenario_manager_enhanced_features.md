# ScenarioManager Enhanced Features

## Overview

The ScenarioManager has been enhanced with new functionality for dynamic condition evaluation, advanced branching, and AI behavior management. This document covers the new features and how to use them.

## New Features

### 1. Dynamic Condition Evaluation

The `evaluate_condition()` method allows for dynamic condition checking based on game state:

```python
def evaluate_condition(self, condition: str) -> bool:
    """Evaluates dynamic conditions based on the game state."""
    if condition == "player_wins":
        return self._is_battle_won()
    elif condition == "player_loses":
        return self._is_battle_lost()
    elif condition == "all_enemies_defeated":
        return self._is_battle_won()
    elif condition == "victory":
        return self._is_battle_won()
    elif condition == "defeat":
        return self._is_battle_lost()
    else:
        print(f"⚠️ Unknown condition: {condition}")
        return False
```

#### Supported Conditions

- `"player_wins"` - Returns true if all enemy units are defeated
- `"player_loses"` - Returns true if all player units are defeated
- `"all_enemies_defeated"` - Same as player_wins
- `"victory"` - Same as player_wins
- `"defeat"` - Same as player_loses

### 2. Advanced Branching with `branch_conditions`

New scenario format supports multiple conditional branches:

```yaml
scenario: "Victory or Defeat"
camera:
  - action: "pan"
    targets:
      - [200, 200]
      - [400, 400]
    speed: 10

ai:
  - unit: "enemy_unit_1"
    action: "attack"
    target: "player_unit"

actions:
  - unit: "player_unit"
    action: "prepare_for_battle"

branch_conditions:
  - condition: "player_wins"
    next_scenario: "victory_celebration.yaml"
  - condition: "player_loses"
    next_scenario: "defeat_ending.yaml"
```

#### Branch Conditions Format

```yaml
branch_conditions:
  - condition: "condition_name"
    next_scenario: "scenario_file.yaml"
  - condition: "another_condition"
    next_scenario: "another_scenario.yaml"
```

The system evaluates conditions in order and loads the first scenario where the condition is true.

### 3. AI Behavior System

Enhanced AI behavior based on unit type and game state:

```python
def ai_behavior(self, unit, game_state):
    """Defines AI behavior based on unit type and game state."""
    if unit.ai == "aggressive":
        # Move towards player and attack
        player_units = [name for name, data in game_state.units.get_all_units().items()
                      if data.get('team') == 'player']
        if player_units:
            target_name = player_units[0]
            print(f"🤖 {unit.name} (aggressive) attacks {target_name}")
    elif unit.ai == "defensive":
        # Check for low health and retreat if necessary
        unit_data = game_state.units.units.get(unit.name, {})
        current_hp = unit_data.get('hp', 10)
        max_hp = unit_data.get('max_hp', 10)

        if current_hp < max_hp / 2:
            print(f"🤖 {unit.name} (defensive) retreats due to low health")
        else:
            print(f"🤖 {unit.name} (defensive) heals or defends")
    elif unit.ai == "passive":
        # Do nothing unless provoked
        print(f"🤖 {unit.name} (passive) waits")
```

#### AI Behavior Types

- **Aggressive**: Attacks player units when possible
- **Defensive**: Retreats when health is low, otherwise heals/defends
- **Passive**: Waits and doesn't take action unless provoked

## Backward Compatibility

All existing functionality remains fully compatible:

### Legacy Format Support

```yaml
name: "Legacy Scenario"
units:
  - name: "player1"
    team: "player"
    sprite: "knight"
    x: 5
    y: 5
    hp: 15
    ap: 3

next_scenario:
  condition: "victory"
  victory_scenario: "victory_ending.yaml"
  defeat_scenario: "defeat_ending.yaml"
```

### New Format Support

```yaml
scenario: "New Format"
camera:
  - action: "pan"
    targets: [[100, 100], [200, 200]]
    speed: 10

branch_conditions:
  - condition: "player_wins"
    next_scenario: "victory.yaml"
```

## Usage Examples

### Basic Condition Evaluation

```python
from devtools.scenario_manager import create_scenario_manager

# Create scenario manager
scenario_manager = create_scenario_manager(camera, ai_controller, player_unit, game_state)

# Evaluate conditions
if scenario_manager.evaluate_condition("player_wins"):
    print("Player has won!")
elif scenario_manager.evaluate_condition("player_loses"):
    print("Player has lost!")
```

### Loading Branch Conditions Scenario

```python
# Load scenario with branch conditions
game_state = scenario_manager.load_scenario("devtools/scenarios/victory_or_defeat.yaml")

# Check for branching
scenario_data = scenario_manager._load_yaml("devtools/scenarios/victory_or_defeat.yaml")
if scenario_manager.check_and_trigger_branching(scenario_data):
    print("Branching occurred!")
```

### AI Behavior Integration

```python
# AI behavior is automatically applied during AI action processing
# The system checks unit AI type and applies appropriate behavior

# Manual AI behavior application
unit_data = game_state.units.units["enemy_unit"]
scenario_manager.ai_behavior(unit_data, game_state)
```

## Scenario Format Comparison

| Feature | Legacy Format | New Format | Branch Conditions |
|---------|---------------|------------|-------------------|
| **Top-level key** | `name` | `scenario` | `scenario` |
| **Unit definitions** | ✅ Included | ❌ Separate | ❌ Separate |
| **Simple branching** | `next_scenario: "file.yaml"` | `next_scenario: "file.yaml"` | `branch_conditions` |
| **Complex branching** | `next_scenario: {condition: "victory", ...}` | `next_scenario: "file.yaml"` | `branch_conditions` |
| **Multiple conditions** | ❌ Single condition | ❌ Single condition | ✅ Multiple conditions |
| **AI behavior** | ✅ Supported | ✅ Supported | ✅ Enhanced |

## Testing

### New Test Coverage

The enhanced ScenarioManager includes comprehensive tests for new functionality:

- `test_evaluate_condition()` - Tests condition evaluation
- `test_branch_conditions_format()` - Tests new branching format
- `test_ai_behavior_aggressive()` - Tests aggressive AI behavior
- `test_ai_behavior_defensive()` - Tests defensive AI behavior
- `test_ai_behavior_passive()` - Tests passive AI behavior
- `test_check_branch_conditions_with_existing_file()` - Tests branching with existing files

### Running Tests

```bash
# Run all scenario manager tests
python -m pytest tests/test_scenario_manager.py -v

# Run specific new feature tests
python -m pytest tests/test_scenario_manager.py::test_evaluate_condition -v
```

## Migration Guide

### From Legacy to Enhanced Format

**Step 1: Convert Simple Branching**
```yaml
# Old
next_scenario: "victory.yaml"

# New (same)
next_scenario: "victory.yaml"
```

**Step 2: Convert Complex Branching**
```yaml
# Old
next_scenario:
  condition: "victory"
  victory_scenario: "victory.yaml"
  defeat_scenario: "defeat.yaml"

# New
branch_conditions:
  - condition: "player_wins"
    next_scenario: "victory.yaml"
  - condition: "player_loses"
    next_scenario: "defeat.yaml"
```

**Step 3: Add AI Behavior**
```yaml
# Units automatically get AI behavior based on their 'ai' field
units:
  - name: "enemy1"
    team: "enemy"
    ai: "aggressive"  # Will use aggressive behavior
  - name: "enemy2"
    team: "enemy"
    ai: "defensive"   # Will use defensive behavior
```

## Best Practices

### When to Use Each Format

1. **Legacy Format**: For complete scenarios with unit definitions
2. **New Format**: For action sequences without unit definitions
3. **Branch Conditions**: For complex branching logic with multiple conditions

### Condition Naming

- Use descriptive condition names: `"player_wins"`, `"all_enemies_defeated"`
- Keep conditions simple and focused
- Document custom conditions in scenario comments

### AI Behavior

- Set appropriate AI types for units: `"aggressive"`, `"defensive"`, `"passive"`
- AI behavior is automatically applied during action processing
- Custom AI behavior can be added by extending the `ai_behavior()` method

## Conclusion

The enhanced ScenarioManager provides:

- **Dynamic condition evaluation** for flexible branching
- **Advanced branching** with multiple conditional paths
- **Enhanced AI behavior** based on unit types and game state
- **Full backward compatibility** with existing scenarios
- **Comprehensive testing** for all new features

This makes the scenario system more powerful and flexible while maintaining ease of use and compatibility with existing content.
