# ADR-0001: Command-Event Architecture

## Status
Accepted

## Context
The existing game architecture was tightly coupled with direct method calls between components. This made it difficult to:
- Test individual components in isolation
- Add new game actions without modifying multiple files
- Implement undo/redo functionality
- Decouple UI from game logic
- Add AI controllers with different strategies

## Decision
Implement a Command-Event architecture with the following components:

### Core Components
1. **Command Pattern**: All game actions are encapsulated as Command objects
   - `Move(unit_id, to)`: Move a unit to a position
   - `Attack(attacker_id, target_id)`: Attack a target
   - `EndTurn(unit_id)`: End a unit's turn

2. **Event System**: Commands generate Events that are published to subscribers
   - `Event(type, payload)`: Immutable event with type and data
   - `EventBus`: Central event publishing/subscribing system

3. **Game Loop**: Orchestrates the command-event flow
   - Gets commands from current controller (AI or Player)
   - Validates and applies commands
   - Publishes resulting events
   - Updates objectives and turn state

4. **RNG**: Deterministic random number generation for reproducible gameplay

5. **Game State**: Central state management with controller protocol

## Consequences

### Positive
- ✅ **Testability**: Commands and events can be tested in isolation
- ✅ **Extensibility**: New commands can be added without modifying existing code
- ✅ **Decoupling**: UI, AI, and game logic are separated
- ✅ **Undo/Redo**: Command history enables undo/redo functionality
- ✅ **Replay**: Event stream enables game replay
- ✅ **AI Integration**: Different AI strategies can implement the Controller protocol

### Negative
- ⚠️ **Complexity**: More abstract than direct method calls
- ⚠️ **Performance**: Slight overhead from event publishing
- ⚠️ **Learning Curve**: Developers need to understand the pattern

### Neutral
- 🔄 **Migration**: Existing code will need gradual migration to use commands
- 🔄 **Documentation**: Need to document command and event types

## Implementation Notes
- Used Protocol classes for type safety without circular imports
- Commands are immutable dataclasses for thread safety
- Events are frozen dataclasses for immutability
- RNG is seeded for deterministic gameplay
- GameState uses Controller protocol for AI/Player abstraction
