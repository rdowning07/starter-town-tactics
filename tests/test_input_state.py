import pygame
import pytest

from game.input_state import InputState
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


class DummySprites:
    def get_sprite(self, category, name):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        surf.fill((0, 255, 0, 128))  # green transparent
        return surf


def make_input_state_with_unit():
    game = DummyGame()
    knight = Unit("Knight", 1, 1, "Red")
    game.add_unit(knight)
    input_state = InputState(game)
    return input_state, knight, game


def test_confirm_selects_unit():
    input_state, knight, _ = make_input_state_with_unit()
    input_state.cursor_x, input_state.cursor_y = 1, 1
    input_state.confirm_selection()
    assert input_state.selected_unit == knight
    assert input_state.state == "unit_selected"


def test_confirm_moves_unit_and_ends_turn():
    input_state, knight, game = make_input_state_with_unit()
    input_state.cursor_x, input_state.cursor_y = 1, 1
    input_state.confirm_selection()
    input_state.cursor_x, input_state.cursor_y = 2, 2
    input_state.confirm_selection()
    assert input_state.selected_unit is None
    assert input_state.state == "idle"
    assert knight.x == 2 and knight.y == 2
    assert game.current_turn == 1


def test_confirm_does_nothing_on_empty_tile():
    game = DummyGame()
    input_state = InputState(game)
    input_state.cursor_x = 0
    input_state.cursor_y = 0
    input_state.confirm_selection()
    assert input_state.selected_unit is None
    assert input_state.state == "idle"


def test_cancel_selection():
    input_state, knight, _ = make_input_state_with_unit()
    input_state.cursor_x, input_state.cursor_y = 1, 1
    input_state.confirm_selection()
    input_state.cancel_selection()
    assert input_state.selected_unit is None
    assert input_state.state == "idle"


def test_draw_cursor_does_not_crash():
    input_state, _, _ = make_input_state_with_unit()
    surface = pygame.Surface((160, 160))
    sprites = DummySprites()
    try:
        input_state.draw_cursor(surface, 32, 0, 0, sprites)
    except Exception as e:
        pytest.fail(f"draw_cursor raised exception: {e}")
