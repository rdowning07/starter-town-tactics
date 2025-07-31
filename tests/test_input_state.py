import pygame
import pytest

from game.input_state import InputState
from game.unit import Unit
from tests.utils.dummy_game import DummyGame  # Use the correct DummyGame


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
    assert input_state.state == "selected"  # Fix state name


def test_confirm_moves_unit_and_ends_turn():
    input_state, knight, game = make_input_state_with_unit()
    input_state.cursor_x, input_state.cursor_y = 1, 1
    input_state.confirm_selection()
    # Ensure knight has full moves and (1,2) is empty (orthogonal move)
    knight.remaining_moves = knight.move_range
    if hasattr(game, 'grid'):
        game.grid.get_tile(1, 2).unit = None
    print('Before move: remaining_moves:', knight.remaining_moves)
    input_state.cursor_x, input_state.cursor_y = 1, 2
    input_state.confirm_selection()
    assert input_state.selected_unit is None
    assert input_state.state == "idle"
    assert knight.x == 1 and knight.y == 2
    assert game.turn_controller.current_turn == 1  # Use turn_controller


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


def test_clear_mouse_click_sets_none():
    input_state = InputState()
    input_state.mouse_click = (1, 2)
    input_state.clear_mouse_click()
    assert input_state.mouse_click is None

def test_move_cursor_clamps_to_bounds():
    class DummyGame:
        def __init__(self):
            self.grid = type("Grid", (), {"width": 2, "height": 2})()
    input_state = InputState(DummyGame())
    input_state.cursor_x, input_state.cursor_y = 0, 0
    input_state.move_cursor(-1, -1)
    assert input_state.cursor_x == 0 and input_state.cursor_y == 0
    input_state.move_cursor(10, 10)
    assert input_state.cursor_x == 1 and input_state.cursor_y == 1

def test_confirm_selection_early_return():
    input_state = InputState()
    # Should not raise or change state
    input_state.state = "idle"
    input_state.confirm_selection()
    assert input_state.state == "idle"
