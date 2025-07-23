import pygame
import pytest

from game.input_state import InputState
from game.keyboard_controller import KeyboardController
from game.unit import Unit


class DummyGame:
    def __init__(self, width=5, height=5):
        self.width = width
        self.height = height
        self.units = []
        self.current_turn = 1

    def add_unit(self, unit):
        self.units.append(unit)

    def next_turn(self):
        self.current_turn += 1


@pytest.fixture
def controller():
    game = DummyGame()
    input_state = InputState(game)
    return KeyboardController(input_state), input_state


def test_cursor_moves_up(controller):
    ctrl, state = controller
    state.cursor_x = 2
    state.cursor_y = 2
    ctrl.handle_key_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    assert state.cursor_y == 1


def test_cursor_moves_down(controller):
    ctrl, state = controller
    state.cursor_x = 2
    state.cursor_y = 2
    ctrl.handle_key_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert state.cursor_y == 3


def test_cursor_moves_left(controller):
    ctrl, state = controller
    state.cursor_x = 2
    state.cursor_y = 2
    ctrl.handle_key_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
    assert state.cursor_x == 1


def test_cursor_moves_right(controller):
    ctrl, state = controller
    state.cursor_x = 2
    state.cursor_y = 2
    ctrl.handle_key_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
    assert state.cursor_x == 3


def test_enter_selects_and_moves_unit():
    game = DummyGame()
    unit = Unit("Knight", 1, 1, "Red")
    game.add_unit(unit)
    input_state = InputState(game)
    controller = KeyboardController(input_state)

    # Select
    input_state.cursor_x = 1
    input_state.cursor_y = 1
    controller.handle_key_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert input_state.state == "unit_selected"

    # Move
    input_state.cursor_x = 2
    input_state.cursor_y = 2
    controller.handle_key_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert input_state.state == "idle"
    assert unit.x == 2 and unit.y == 2


def test_escape_cancels_selection():
    game = DummyGame()
    unit = Unit("Knight", 1, 1, "Red")
    game.add_unit(unit)
    input_state = InputState(game)
    input_state.cursor_x = 1
    input_state.cursor_y = 1
    input_state.confirm_selection()
    assert input_state.state == "unit_selected"

    controller = KeyboardController(input_state)
    controller.handle_key_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert input_state.state == "idle"
    assert input_state.selected_unit is None
