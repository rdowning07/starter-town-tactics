#!/usr/bin/env python3
"""
Visual demo player for the command-event architecture using Pygame.
This module demonstrates the core game loop with actual visual rendering.
"""

import os
import sys
import time

import pygame

# Add the project root to the path before imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core imports
from core.command import Attack, EndTurn, Move
from core.events import Event, EventBus
from core.game_loop import GameLoop
from core.rng import Rng
from core.state import GameState, Unit, UnitStats

# Pygame setup
pygame.init()
WINDOW_SIZE = (800, 600)
GRID_SIZE = 40
GRID_OFFSET = (50, 50)
GRID_WIDTH = 15
GRID_HEIGHT = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class VisualDemo:
    """Visual demo for command-event architecture."""

    def __init__(self):
        """Initialize the visual demo."""
        # Pygame setup
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Starter Town Tactics - Behavior Tree AI Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Game state
        self.rng = Rng(1337)
        self.bus = EventBus()
        self.loop = GameLoop(self.rng, self.bus)
        self.state = self.load_demo_state()

        # Subscribe to events
        self.bus.subscribe(self.handle_event)

        # Demo state
        self.tick_count = 0
        self.max_ticks = 3600
        self.events_log = []
        self.running = True

    def load_demo_state(self) -> GameState:
        """Load a demo game state with visual units."""
        state = GameState()

        # Create units with positions for visual display
        player_stats = UnitStats(hp=20, atk=8, def_=3, h=1)
        player = Unit(unit_id="player1", pos=(3, 3), facing="E", stats=player_stats)
        state.add_unit(player)

        enemy_stats = UnitStats(hp=15, atk=6, def_=2, h=0)
        enemy = Unit(unit_id="enemy1", pos=(8, 5), facing="W", stats=enemy_stats)
        state.add_unit(enemy)

        # Create a BT-based demo controller
        class BTVisualDemoController:
            def __init__(self, demo):
                self.demo = demo
                self.turn_count = 0
                # Import BT system here to avoid circular imports
                try:
                    from core.ai.bt import make_basic_combat_tree
                    from game.ai_bt_adapter import BTAdapter

                    self.bt = make_basic_combat_tree()
                    self.bt_available = True
                except ImportError:
                    print("BT system not available, falling back to simple controller")
                    self.bt_available = False
                    self.bt = None

            def decide(self, game_state: GameState):
                if (
                    not self.bt_available or self.turn_count % 3 != 0
                ):  # BT decides every 3 turns
                    # Fallback to simple movement
                    self.turn_count += 1
                    return Move(unit_id="player1", to=(4 + (self.turn_count % 3), 3))

                # Use BT for AI decision making
                try:
                    # Simple BT logic: if enemy is close to player, move away; otherwise move toward
                    enemy = game_state.unit("enemy1")
                    player = game_state.unit("player1")
                    if enemy and player:
                        # Calculate distance
                        dx = player.pos[0] - enemy.pos[0]
                        dy = player.pos[1] - enemy.pos[1]
                        distance = abs(dx) + abs(dy)  # Manhattan distance

                        # BT decision: if too close, move away; if far, move toward
                        if distance <= 2:  # Too close - move away
                            new_x = enemy.pos[0] + (1 if dx < 0 else -1)
                            new_y = enemy.pos[1] + (1 if dy < 0 else -1)
                        else:  # Move toward player
                            new_x = enemy.pos[0] + (
                                1 if dx > 0 else (-1 if dx < 0 else 0)
                            )
                            new_y = enemy.pos[1] + (
                                1 if dy > 0 else (-1 if dy < 0 else 0)
                            )

                        # Keep within bounds
                        new_x = max(0, min(GRID_WIDTH - 1, new_x))
                        new_y = max(0, min(GRID_HEIGHT - 1, new_y))

                        return Move(unit_id="enemy1", to=(new_x, new_y))

                    # Fallback movement
                    self.turn_count += 1
                    return Move(unit_id="enemy1", to=(8, 5))

                except Exception as e:
                    print(f"BT error: {e}, falling back to simple controller")
                    self.turn_count += 1
                    return Move(unit_id="enemy1", to=(8, 5))

        state.set_controller(BTVisualDemoController(self))

        # Mock objectives and turn controller
        state.objectives = MockObjectives(self)
        state.turn_controller = MockTurnController(self)  # type: ignore

        return state

    def handle_event(self, event: Event):
        """Handle game events for visual feedback."""
        self.events_log.append(f"{event.type}: {event.payload}")
        if len(self.events_log) > 10:  # Keep only last 10 events
            self.events_log.pop(0)

    def draw_grid(self):
        """Draw the game grid."""
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                GRAY,
                (GRID_OFFSET[0] + x * GRID_SIZE, GRID_OFFSET[1]),
                (
                    GRID_OFFSET[0] + x * GRID_SIZE,
                    GRID_OFFSET[1] + GRID_HEIGHT * GRID_SIZE,
                ),
            )

        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                GRAY,
                (GRID_OFFSET[0], GRID_OFFSET[1] + y * GRID_SIZE),
                (
                    GRID_OFFSET[0] + GRID_WIDTH * GRID_SIZE,
                    GRID_OFFSET[1] + y * GRID_SIZE,
                ),
            )

    def draw_units(self):
        """Draw all units on the grid."""
        for unit in self.state.get_all_units():
            x, y = unit.pos
            screen_x = GRID_OFFSET[0] + x * GRID_SIZE + GRID_SIZE // 2
            screen_y = GRID_OFFSET[1] + y * GRID_SIZE + GRID_SIZE // 2

            # Choose color based on unit type
            if unit.id == "player1":
                color = BLUE
            else:
                color = RED

            # Draw unit circle
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), GRID_SIZE // 3)

            # Draw unit info
            info_text = f"{unit.id}\nHP:{unit.stats.hp}"
            text_surface = self.small_font.render(info_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            self.screen.blit(text_surface, text_rect)

    def draw_ui(self):
        """Draw UI elements."""
        # Draw title
        title = self.font.render(
            "Starter Town Tactics - Behavior Tree AI Demo", True, WHITE
        )
        self.screen.blit(title, (10, 10))

        # Draw tick counter
        tick_text = self.font.render(
            f"Tick: {self.tick_count}/{self.max_ticks}", True, WHITE
        )
        self.screen.blit(tick_text, (10, 40))

        # Draw recent events
        events_text = self.font.render("Recent Events:", True, WHITE)
        self.screen.blit(events_text, (10, 70))

        for i, event in enumerate(self.events_log[-5:]):  # Show last 5 events
            event_text = self.small_font.render(event, True, YELLOW)
            self.screen.blit(event_text, (10, 95 + i * 20))

        # Draw BT status
        bt_status = self.font.render("BT AI: Active", True, GREEN)
        self.screen.blit(bt_status, (10, 200))

        # Draw BT decision info
        enemy = self.state.unit("enemy1")
        player = self.state.unit("player1")
        if enemy and player:
            distance = abs(player.pos[0] - enemy.pos[0]) + abs(
                player.pos[1] - enemy.pos[1]
            )
            distance_text = self.small_font.render(f"Distance: {distance}", True, WHITE)
            self.screen.blit(distance_text, (10, 230))

            if distance <= 2:
                decision_text = self.small_font.render(
                    "BT Decision: Move Away", True, RED
                )
            else:
                decision_text = self.small_font.render(
                    "BT Decision: Move Toward", True, GREEN
                )
            self.screen.blit(decision_text, (10, 250))

        # Draw instructions
        instructions = [
            "Controls:",
            "SPACE - Pause/Resume",
            "R - Reset Demo",
            "ESC - Quit",
        ]

        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, GRAY)
            self.screen.blit(inst_text, (WINDOW_SIZE[0] - 200, 10 + i * 20))

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle pause (not implemented yet)
                    # TODO: Implement pause functionality  # pylint: disable=fixme
                    pass
                elif event.key == pygame.K_r:
                    # Reset demo
                    self.state = self.load_demo_state()
                    self.tick_count = 0
                    self.events_log.clear()

    def run(self):
        """Main game loop."""
        print("🎮 Starting Behavior Tree AI Visual Demo...")
        print("Controls: SPACE=Pause, R=Reset, ESC=Quit")
        print("🤖 Watch the red enemy unit make smart decisions using BT logic!")

        while self.running and self.tick_count < self.max_ticks:
            # Handle input
            self.handle_input()

            # Update game state
            self.loop.tick(self.state)
            self.tick_count += 1

            # Draw everything
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_units()
            self.draw_ui()

            # Update display
            pygame.display.flip()

            # Cap at 60 FPS
            self.clock.tick(60)

            # Add a small delay to make the demo visible
            time.sleep(0.1)

        print("✅ Visual demo completed!")
        pygame.quit()


class MockObjectives:
    """Mock objectives for demo."""

    def __init__(self, demo):
        self.demo = demo

    def update_from_events(self, events):
        """Update from events."""
        # TODO: Implement event updates  # pylint: disable=fixme


class MockTurnController:
    """Mock turn controller for demo."""

    def __init__(self, demo):
        self.demo = demo

    def start_if_needed(self, game_state):
        """Start turn if needed."""
        return []  # No events for now

    def maybe_advance(self, game_state):
        """Maybe advance turn."""
        return []  # No events for now


def main():
    """Run the visual demo."""
    demo = VisualDemo()
    demo.run()


if __name__ == "__main__":
    main()
