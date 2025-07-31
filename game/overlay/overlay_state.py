# game/overlay/overlay_state.py

import pygame


class OverlayState:
    def __init__(self):
        self.show_movement = True
        self.show_terrain = True
        self.show_attack = True
        self.show_threat = True
        # Add tile collections for overlay drawing
        self.movement_tiles = set()
        self.threat_tiles = set()
        self.attack_tiles = set()
        self.terrain_tiles = set()

    def handle_key_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.show_movement = not self.show_movement
            elif event.key == pygame.K_2:
                self.show_terrain = not self.show_terrain
            elif event.key == pygame.K_3:
                self.show_attack = not self.show_attack
            elif event.key == pygame.K_4:
                self.show_threat = not self.show_threat
