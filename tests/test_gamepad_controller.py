import os
import sys
import pygame
import pytest

# Fix for circular import: add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game.input_state import InputState
from game.gamepad_controller import GamepadController


class DummyGame:
    def __init__(self):
        self.width = 5
        self.height = 5
        self.units = []
        self.current_turn = 1

    def add_unit(self, unit):
        self.units.append(unit)

    def next_turn(self):
        self.current_turn += 1


@pytest.fixture
def controller_and_state():
    game = DummyGame()
    input_state = InputState(game)
    controller = GamepadController(input_state, init_joystick=False)
    return controller, input_state


def test_hat_moves_cursor(controller_and_state):
    controller, input_state = controller_and_state
    input_state.cursor_x = 2
    input_state.cursor_y = 2
    event = pygame.event.Event(pygame.JOYHATMOTION, value=(-1, 0))
    controller.handle_event(event)
    assert input_state.cursor_x == 1
    assert input_state.cursor_y == 2


def test_button_confirm_selection(monkeypatch, controller_and_state):
    controller, input_state = controller_and_state
    called = {"confirm": False}
    monkeypatch.setattr(input_state, "confirm_selection", lambda: called.update(confirm=True))
    event = pygame.event.Event(pygame.JOYBUTTONDOWN, button=0)
    controller.handle_event(event)
    assert called["confirm"]


def test_button_cancel_selection(monkeypatch, controller_and_state):
    controller, input_state = controller_and_state
    called = {"cancel": False}
    monkeypatch.setattr(input_state, "cancel_selection", lambda: called.update(cancel=True))
    event = pygame.event.Event(pygame.JOYBUTTONDOWN, button=1)
    controller.handle_event(event)
    assert called["cancel"]


def test_update_moves_cursor_x(monkeypatch, controller_and_state):
    controller, input_state = controller_and_state
    input_state.cursor_x = 2
    input_state.cursor_y = 2
    controller.last_move_time = 0

    class MockJoystick:
        def get_axis(self, axis):
            return 1.0 if axis == 0 else 0.0

    controller.joystick = MockJoystick()
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 999999)

    controller.update()

    assert input_state.cursor_x == 3
    assert input_state.cursor_y == 2


def test_update_moves_cursor_y(monkeypatch, controller_and_state):
    controller, input_state = controller_and_state
    input_state.cursor_x = 2
    input_state.cursor_y = 2
    controller.last_move_time = 0

    class MockJoystick:
        def get_axis(self, axis):
            return 1.0 if axis == 1 else 0.0

    controller.joystick = MockJoystick()
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 999999)

    controller.update()

    assert input_state.cursor_x == 2
    assert input_state.cursor_y == 3
