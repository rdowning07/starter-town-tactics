"""
UI Panel rendering methods for the BT Fighter Demo.

This module contains the UI panel drawing methods extracted from the main demo
to improve code organization and maintainability.
"""

import pygame


class UIPanels:
    """UI panel rendering methods for the demo."""

    def __init__(self, demo):
        """Initialize UI panels with reference to demo instance."""
        self.demo = demo

    def draw_roster_panel(self, surface: pygame.Surface) -> None:
        """Draw the roster panel showing only ally team status."""
        # Create team data - only show allies, not enemies
        teams = {
            1: {  # Player team only
                "name": "Allies",
                "units": [
                    {
                        "name": "Fighter",
                        "hp": self.demo.fighter_hp,
                        "max_hp": 10,  # Based on heal function cap
                        "alive": self.demo.fighter_hp > 0,
                    },
                    {
                        "name": "Mage",
                        "hp": self.demo.mage_hp,
                        "max_hp": 15,
                        "alive": self.demo.mage_hp > 0,
                    },
                    {
                        "name": "Healer",
                        "hp": self.demo.healer_hp,
                        "max_hp": 14,  # Based on heal function cap
                        "alive": self.demo.healer_hp > 0,
                    },
                    {
                        "name": "Ranger",
                        "hp": self.demo.ranger_hp,
                        "max_hp": 14,
                        "alive": self.demo.ranger_hp > 0,
                    },
                ],
            },
        }

        self.demo.roster_panel.draw(surface, teams)

    def draw_info_panel(self, surface: pygame.Surface) -> None:
        """Draw info panel with animation and AI decision info."""
        # Position info panel to avoid overlapping with game area (720px wide)
        panel_x = 750  # Right side of screen
        panel_y = 0  # Aligned with top of allies panel (top of tiles)

        # Create info data
        alive_bandits = [h for h in self.demo.bandit_hp if h > 0]
        bandit_hp_text = f"Bandits: {len(alive_bandits)} alive"
        if alive_bandits:
            bandit_hp_text += f" (HP: {', '.join(map(str, alive_bandits))})"

        info_items = [
            f"Animation: {self.demo.fighter_animation} (HP: {self.demo.fighter_hp})",
            bandit_hp_text,
            f"AI Decision: {self.demo.bt_tick_count}",
            f"Active Effects: {len(self.demo.active_effects)}",
            f"AI Tasks: {self.demo.ai_scheduler.get_task_count()}",
            "",
            "🏆 Victory: Eliminate all enemies",
            f"Status: {'VICTORY!' if self.demo.victory_achieved else 'In Progress'}",
        ]

        # Draw background
        panel_width = 350  # Expanded for longer text
        panel_height = len(info_items) * 25 + 30  # Reduced line height from 30 to 25
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Semi-transparent black

        # Draw border
        pygame.draw.rect(
            panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2
        )

        # Draw title
        font = pygame.font.Font(None, 20)
        title_surface = font.render("GAME INFO", True, (255, 255, 255))
        panel_surface.blit(title_surface, (10, 10))

        # Draw info items
        y_offset = 35
        for item in info_items:
            text_surface = font.render(item, True, (255, 255, 255))
            panel_surface.blit(text_surface, (10, y_offset))
            y_offset += 30

        # Blit to main surface
        surface.blit(panel_surface, (panel_x, panel_y))

    def draw_architecture_panel(self, surface: pygame.Surface) -> None:
        """Draw architecture & patterns panel."""
        panel_x = 750  # Right side of screen
        panel_y = 252  # Moved up 1 tile (48px) from 300

        arch_items = [
            "Architecture & Patterns:",
            "├─ Composite: BT Structure",
            "├─ Strategy: BTContext",
            "├─ Observer: VictoryService",
            "├─ Factory: EntityFactory",
            "├─ Scheduler: AIScheduler",
            "└─ State: GameState",
        ]

        # Draw background
        panel_width = 350
        panel_height = len(arch_items) * 25 + 30
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))

        # Draw border
        pygame.draw.rect(
            panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2
        )

        # Draw title
        font = pygame.font.Font(None, 20)
        title_surface = font.render("ARCHITECTURE", True, (255, 255, 255))
        panel_surface.blit(title_surface, (10, 10))

        # Draw items
        y_offset = 35
        for item in arch_items:
            text_surface = font.render(item, True, (255, 255, 255))
            panel_surface.blit(text_surface, (10, y_offset))
            y_offset += 25

        surface.blit(panel_surface, (panel_x, panel_y))

    def draw_methods_panel(self, surface: pygame.Surface) -> None:
        """Draw methods active panel."""
        panel_x = 750  # Right side of screen

        methods_items = [
            "Methods Active:",
            "├─ _handle_input() - Player controls",
            "├─ _update_effects() - Visual effects",
            "├─ _draw_terrain() - Map rendering",
            "├─ _draw_units() - Character sprites",
            "├─ _draw_ui() - Interface panels",
            "└─ _update_ai() - AI decision making",
        ]

        # Calculate panel height and position so bottom aligns with bottom of tiles
        panel_width = 350
        panel_height = len(methods_items) * 25 + 30
        # Bottom of tiles is at y=15*48=720, so panel bottom should be at 720
        # Position panel so its bottom aligns with bottom of tiles, moved up 1 tile (48px) then down 1/4 tile (12px)
        panel_y = 684 - panel_height

        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))

        # Draw border
        pygame.draw.rect(
            panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2
        )

        # Draw title
        font = pygame.font.Font(None, 20)
        title_surface = font.render("METHODS", True, (255, 255, 255))
        panel_surface.blit(title_surface, (10, 10))

        # Draw items
        y_offset = 35
        for item in methods_items:
            text_surface = font.render(item, True, (255, 255, 255))
            panel_surface.blit(text_surface, (10, y_offset))
            y_offset += 25

        surface.blit(panel_surface, (panel_x, panel_y))

    def draw_action_log_panel(self, surface: pygame.Surface) -> None:
        """Draw action log panel showing recent character actions."""
        # Create action log data
        action_items = self.demo.action_log.copy()
        if not action_items:
            action_items = ["No actions yet..."]

        # Draw background
        panel_width = 350
        panel_height = len(action_items) * 25 + 30

        # Align with rightmost tile edge (15 * 48 = 720)
        panel_x = (
            720 - panel_width
        )  # Right edge of panel aligns with right edge of tiles

        # Align with bottommost tile edge (15 * 48 = 720)
        panel_y = (
            720 - panel_height
        )  # Bottom edge of panel aligns with bottom edge of tiles
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Semi-transparent black

        # Draw border
        pygame.draw.rect(
            panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2
        )

        # Draw title
        font = pygame.font.Font(None, 20)
        title_surface = font.render("ACTION LOG", True, (255, 255, 255))
        panel_surface.blit(title_surface, (10, 10))

        # Draw action items
        y_offset = 35
        for item in action_items:
            text_surface = font.render(item, True, (255, 255, 255))
            panel_surface.blit(text_surface, (10, y_offset))
            y_offset += 25

        surface.blit(panel_surface, (panel_x, panel_y))
