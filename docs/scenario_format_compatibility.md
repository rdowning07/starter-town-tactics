# Scenario Format Compatibility Guide

## Overview

The ScenarioManager now supports **two scenario formats** for maximum flexibility:

1. **Legacy Format**: Full-featured with unit definitions
2. **New Simplified Format**: Streamlined for action sequences

## Format Comparison

### Legacy Format (Full-Featured)
```yaml
name: "Demo Battle Scenario"
description: "A simple battle scenario with AI and player units"
map_id: "arena"
objective: "Defeat all enemy units"
max_turns: 12

units:
  - name: "ai_alpha"
    team: "enemy"
    sprite: "knight"
    x: 3
    y: 3
    ap: 2
    hp: 10
    animation: "idle"
    ai: "aggressive"

camera:
  - action: "pan"
    targets: [[96, 96], [192, 192], [288, 288]]
    speed: 8
    delay: 0.3

ai:
  - unit: "ai_alpha"
    action: "attack"
    target: "p_bravo"

actions:
  - unit: "p_bravo"
    action: "prepare_for_battle"

next_scenario:
  condition: "victory"
  victory_scenario: "victory_ending.yaml"
  defeat_scenario: "defeat_ending.yaml"
  default_scenario: "continue_battle.yaml"
```

### New Simplified Format (Action-Focused)
```yaml
scenario: "Battle Start"
camera:
  - action: "pan"
    targets:
      - [100, 100]  # Starting position
      - [400, 400]  # Intermediate position
      - [600, 600]  # Final position
    speed: 10
    delay: 0.5

ai:
  - unit: "enemy_unit_1"
    action: "attack"
    target: "player_unit"
  - unit: "enemy_unit_2"
    action: "move"
    target: [500, 500]

actions:
  - unit: "player_unit"
    action: "prepare_for_battle"

next_scenario: "victory_celebration.yaml"
```

## Key Differences

| Feature | Legacy Format | New Format |
|---------|---------------|------------|
| **Top-level key** | `name` | `scenario` |
| **Unit definitions** | ✅ Included in `units` section | ❌ Must be loaded separately |
| **Branching complexity** | Complex conditional objects | Simple string paths |
| **Metadata** | Full metadata support | Minimal metadata |
| **Use case** | Complete battle scenarios | Action sequences & cutscenes |

## Compatibility Status

### ✅ Fully Compatible Scenarios

**Legacy Format:**
- `demo_battle.yaml` - Full battle scenario with units
- `boss_fake_death.yaml` - Boss battle with complex branching
- `survive_the_horde.yaml` - Survival scenario
- `skirmish_4v4.yaml` - Multi-unit battle
- `demo_cutscene.yaml` - Cutscene demonstration
- `scripted_loss_intro.yaml` - Scripted sequence

**New Format:**
- `battle_start.yaml` - Simplified battle start sequence
- `victory_celebration.yaml` - Victory celebration sequence

### 🔄 Branching Scenarios

**Complex Branching (Legacy):**
```yaml
next_scenario:
  condition: "victory"
  victory_scenario: "victory_ending.yaml"
  defeat_scenario: "defeat_ending.yaml"
  default_scenario: "continue_battle.yaml"
```

**Simple Branching (New):**
```yaml
next_scenario: "victory_celebration.yaml"
```

## Usage Examples

### Loading Legacy Format
```python
from devtools.scenario_manager import create_scenario_manager

# Create scenario manager
scenario_manager = create_scenario_manager(camera, ai_controller, player_unit, game_state)
scenario_manager.set_managers(sprite_manager, fx_manager, sound_manager)

# Load legacy format (includes units)
game_state = scenario_manager.load_scenario("devtools/scenarios/demo_battle.yaml")
```

### Loading New Format
```python
# Load new format (units must be loaded separately)
game_state = scenario_manager.load_scenario("devtools/scenarios/battle_start.yaml")

# Units need to be loaded from elsewhere
# This could be from a separate unit configuration file
# or from the game state that already has units loaded
```

### Mixed Format Workflow
```python
# 1. Load units from legacy format
game_state = scenario_manager.load_scenario("devtools/scenarios/demo_battle.yaml")

# 2. Load action sequence from new format
scenario_manager.load_scenario("devtools/scenarios/battle_start.yaml")

# 3. Check for branching
if scenario_manager.check_and_trigger_branching(scenario_data):
    print("Branching triggered!")
```

## Migration Guide

### From Legacy to New Format

**Step 1: Extract Units**
```yaml
# Move units to separate file: units.yaml
units:
  - name: "player_unit"
    team: "player"
    sprite: "knight"
    x: 5
    y: 5
    hp: 15
    ap: 3
```

**Step 2: Simplify Scenario**
```yaml
# Convert to new format
scenario: "Battle Start"
camera:
  - action: "pan"
    targets: [[100, 100], [400, 400], [600, 600]]
    speed: 10
    delay: 0.5

ai:
  - unit: "enemy_unit_1"
    action: "attack"
    target: "player_unit"

actions:
  - unit: "player_unit"
    action: "prepare_for_battle"

next_scenario: "victory_celebration.yaml"
```

### From New to Legacy Format

**Step 1: Add Metadata**
```yaml
name: "Battle Start"
description: "A battle scenario with cinematic camera work"
map_id: "arena"
objective: "Defeat enemies"
max_turns: 10
```

**Step 2: Add Units Section**
```yaml
units:
  - name: "player_unit"
    team: "player"
    sprite: "knight"
    x: 5
    y: 5
    hp: 15
    ap: 3
    animation: "idle"
  - name: "enemy_unit_1"
    team: "enemy"
    sprite: "rogue"
    x: 8
    y: 8
    hp: 10
    ap: 2
    animation: "idle"
    ai: "aggressive"
```

**Step 3: Enhance Branching**
```yaml
next_scenario:
  condition: "victory"
  victory_scenario: "victory_celebration.yaml"
  defeat_scenario: "defeat_ending.yaml"
```

## Best Practices

### When to Use Legacy Format
- **Complete battle scenarios** with full unit definitions
- **Complex branching logic** with multiple conditions
- **Scenarios requiring detailed metadata**
- **Self-contained scenarios** that don't depend on external unit definitions

### When to Use New Format
- **Action sequences** and cutscenes
- **Simple branching** with single next scenario
- **Scenarios where units are defined elsewhere**
- **Quick prototyping** and testing
- **Cinematic sequences** focused on camera and actions

### Hybrid Approach
- Use **legacy format** for main battle scenarios
- Use **new format** for transition sequences and cutscenes
- Load units once with legacy format, then use new format for actions

## Testing Both Formats

### Test Legacy Format
```bash
PYTHONPATH=/path/to/project python devtools/scenario_automation_demo.py --scenario devtools/scenarios/demo_battle.yaml --auto
```

### Test New Format
```bash
PYTHONPATH=/path/to/project python devtools/scenario_automation_demo.py --scenario devtools/scenarios/battle_start.yaml --auto
```

## Conclusion

Both scenario formats are fully supported and can be used interchangeably based on your needs:

- **Legacy Format**: For complete, self-contained scenarios
- **New Format**: For streamlined action sequences
- **Hybrid Approach**: Best of both worlds for complex games

The ScenarioManager automatically detects the format and handles it appropriately, ensuring backward compatibility while supporting the new simplified structure.
