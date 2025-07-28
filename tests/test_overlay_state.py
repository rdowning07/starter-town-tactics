# tests/test_overlay_state.py

import pygame
from game.overlay.overlay_state import OverlayState


def simulate_keypress(key):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key})


def test_overlay_toggles():
    state = OverlayState()

    # Initial state is all True
    assert state.show_movement is True
    assert state.show_terrain is True
    assert state.show_attack is True
    assert state.show_threat is True

    # Toggle movement
    state.handle_key_event(simulate_keypress(pygame.K_1))
    assert state.show_movement is False
    state.handle_key_event(simulate_keypress(pygame.K_1))
    assert state.show_movement is True

    # Toggle terrain
    state.handle_key_event(simulate_keypress(pygame.K_2))
    assert state.show_terrain is False
    state.handle_key_event(simulate_keypress(pygame.K_2))
    assert state.show_terrain is True

    # Toggle attack
    state.handle_key_event(simulate_keypress(pygame.K_3))
    assert state.show_attack is False
    state.handle_key_event(simulate_keypress(pygame.K_3))
    assert state.show_attack is True

    # Toggle threat
    state.handle_key_event(simulate_keypress(pygame.K_4))
    assert state.show_threat is False
    state.handle_key_event(simulate_keypress(pygame.K_4))
    assert state.show_threat is True
