"""
Team roster panel showing alive/KO status for all units.
Provides clear overview of battle state.
"""

from typing import Dict

import pygame


class RosterPanel:
    """Team roster panel showing unit status."""

    def __init__(self):
        """Initialize the roster panel."""
        self.position = (700, 150)  # Far right, below control card with more spacing
        self.background_color = (0, 0, 0, 180)  # Semi-transparent black
        self.text_color = (255, 255, 255)  # White text
        self.alive_color = (0, 255, 0)  # Green for alive
        self.ko_color = (255, 0, 0)  # Red for KO

        # Font
        self.font = None
        self.title_font = None

    def draw(self, surface: pygame.Surface, teams: Dict[int, Dict]) -> None:
        """Draw the roster panel.

        Args:
            surface: Pygame surface to draw on
            teams: Dictionary of team data with 'name' and 'units' keys
        """
        # Initialize fonts if needed
        if self.font is None:
            self.font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 20)

        # Calculate panel dimensions
        padding = 10
        line_height = 20
        max_units = 0

        # Count total units across all teams
        for team_data in teams.values():
            units = team_data.get("units", [])
            max_units = max(max_units, len(units))

        # Calculate panel size
        team_count = len(teams)
        panel_width = 250
        panel_height = team_count * 30 + max_units * line_height + padding * 2

        # Draw background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.background_color)

        # Draw border
        pygame.draw.rect(panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2)

        # Draw teams
        y_offset = padding
        for team_id, team_data in teams.items():
            team_name = team_data.get("name", f"Team {team_id}")
            units = team_data.get("units", [])

            # Draw team header
            team_surface = self.title_font.render(team_name, True, self.text_color)
            panel_surface.blit(team_surface, (padding, y_offset))
            y_offset += 25

            # Count alive/KO units
            alive_count = 0
            ko_count = 0

            for unit in units:
                if isinstance(unit, dict):
                    # Unit is a dictionary
                    is_alive = unit.get("alive", True)
                    current_hp = unit.get("hp", 0)
                    if is_alive and current_hp > 0:
                        alive_count += 1
                    else:
                        ko_count += 1
                else:
                    # Unit is an object with attributes
                    if hasattr(unit, "alive") and hasattr(unit, "hp"):
                        if unit.alive and unit.hp > 0:
                            alive_count += 1
                        else:
                            ko_count += 1
                    else:
                        # Assume alive if we can't determine status
                        alive_count += 1

            # Draw unit status
            status_text = f"Alive: {alive_count}  KO: {ko_count}"
            status_surface = self.font.render(status_text, True, self.text_color)
            panel_surface.blit(status_surface, (padding, y_offset))
            y_offset += line_height

            # Draw individual units
            for unit in units:
                if isinstance(unit, dict):
                    # Unit is a dictionary
                    unit_name = unit.get("name", "Unknown")
                    is_alive = unit.get("alive", True)
                    current_hp = unit.get("hp", 0)
                    max_hp = unit.get("max_hp", 10)

                    if is_alive and current_hp > 0:
                        color = self.alive_color
                        status = f"{current_hp}/{max_hp} HP"
                    else:
                        color = self.ko_color
                        status = "KO"
                else:
                    # Unit is an object with attributes
                    unit_name = getattr(unit, "name", "Unknown")
                    if hasattr(unit, "alive") and hasattr(unit, "hp"):
                        if unit.alive and unit.hp > 0:
                            color = self.alive_color
                            max_hp = getattr(unit, "max_hp", 10)
                            status = f"{unit.hp}/{max_hp} HP"
                        else:
                            color = self.ko_color
                            status = "KO"
                    else:
                        color = self.alive_color
                        status = "Alive"

                # Draw unit name and status
                unit_text = f"  {unit_name}: {status}"
                unit_surface = self.font.render(unit_text, True, color)
                panel_surface.blit(unit_surface, (padding, y_offset))
                y_offset += line_height

            y_offset += 5  # Space between teams

        # Blit panel to main surface
        surface.blit(panel_surface, self.position)
