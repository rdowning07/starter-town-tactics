# game/keyboard_controller.py

import pygame

from game.input_state import InputState


class KeyboardController:
    def __init__(self, input_state: InputState):
        self.input_state = input_state

    def handle_key_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        key = event.key
        if key == pygame.K_LEFT:
            self.input_state.move_cursor(-1, 0)
        elif key == pygame.K_RIGHT:
            self.input_state.move_cursor(1, 0)
        elif key == pygame.K_UP:
            self.input_state.move_cursor(0, -1)
        elif key == pygame.K_DOWN:
            self.input_state.move_cursor(0, 1)
        elif key == pygame.K_RETURN:
            self.input_state.confirm_selection()
        elif key == pygame.K_ESCAPE:
            self.input_state.cancel_selection()
