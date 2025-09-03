"""
Enhanced Input Controller for MVP gameplay.
Integrates camera controls, unit selection, and action handling.
"""

from typing import Any, Dict, Optional, Set, Tuple

import pygame

from game.camera import Camera, CameraController
from game.game_state import GameState
from game.gamepad_controller import GamepadController
from game.input_state import InputState
from game.keyboard_controller import KeyboardController
from game.ui.game_actions import GameActions
from game.ui.ui_state import UIState


class InputController:
    """
    Enhanced input controller for MVP gameplay.

    Provides unified input handling for keyboard, mouse, and gamepad input,
    with integration for camera controls, unit selection, and game actions.
    """

    def __init__(self, game_state: GameState, ui_state: UIState, camera: Optional[Camera] = None):
        """
        Initialize input controller.

        Args:
            game_state: Game state instance
            ui_state: UI state instance
            camera: Optional camera instance for camera controls
        """
        self.game_state = game_state
        self.ui_state = ui_state
        self.camera = camera
        self.camera_controller = CameraController(camera) if camera else None

        # Input state tracking
        self.input_state = InputState()
        self.keyboard_controller = KeyboardController()
        self.gamepad_controller = GamepadController(self.input_state)

        # Game actions
        self.game_actions = GameActions()

        # Input settings
        self.camera_pan_speed = 64
        self.fast_pan_speed = 128
        self.mouse_edge_pan_threshold = 50  # pixels from edge to start panning
        self.enable_mouse_edge_panning = True
        self.enable_keyboard_camera = True
        self.enable_gamepad = True

        # State tracking
        self.keys_held: Set[int] = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons: Set[int] = set()
        self.last_click_time = 0
        self.double_click_threshold = 300  # milliseconds

        # Key bindings
        self.key_bindings = {
            # Camera controls
            pygame.K_w: "camera_up",
            pygame.K_s: "camera_down",
            pygame.K_a: "camera_left",
            pygame.K_d: "camera_right",
            pygame.K_q: "camera_zoom_out",
            pygame.K_e: "camera_zoom_in",
            pygame.K_r: "camera_reset",
            # Unit controls
            pygame.K_SPACE: "end_turn",
            pygame.K_TAB: "next_unit",
            pygame.K_LSHIFT: "modifier_fast",
            pygame.K_LCTRL: "modifier_precise",
            # UI controls
            pygame.K_ESCAPE: "cancel_action",
            pygame.K_RETURN: "confirm_action",
            pygame.K_h: "toggle_help",
            pygame.K_g: "toggle_grid",
            pygame.K_t: "toggle_turn_info",
            # Debug controls (if enabled)
            pygame.K_F1: "debug_info",
            pygame.K_F2: "debug_ai",
            pygame.K_F3: "debug_camera",
        }

    def update(self, dt: float = 1.0):
        """
        Update input controller.

        Args:
            dt: Delta time
        """
        # Update camera controller
        if self.camera_controller:
            self.camera_controller.update(dt)

        # Handle mouse edge panning
        if self.enable_mouse_edge_panning and self.camera:
            self._handle_mouse_edge_panning()

        # Update keyboard controller for overlay toggles
        self.keyboard_controller.update(self.input_state)

    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events.

        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_mouse_wheel(event)

    def _handle_keydown(self, event):
        """Handle key press events."""
        key = event.key
        self.keys_held.add(key)

        # Update input state
        key_name = pygame.key.name(key)
        self.input_state.set_key_down(key_name)

        # Handle key bindings
        action = self.key_bindings.get(key)
        if action:
            self._handle_action(action, True)

        # Handle special keys
        if key == pygame.K_ESCAPE:
            self.ui_state.reset_selection()

    def _handle_keyup(self, event):
        """Handle key release events."""
        key = event.key
        self.keys_held.discard(key)

        # Update input state
        key_name = pygame.key.name(key)
        self.input_state.set_key_up(key_name)

        # Handle key bindings
        action = self.key_bindings.get(key)
        if action:
            self._handle_action(action, False)

    def _handle_mouse_down(self, event):
        """Handle mouse button press events."""
        self.mouse_buttons.add(event.button)

        if event.button == 1:  # Left click
            self._handle_left_click(event.pos)
        elif event.button == 2:  # Middle click
            self._handle_middle_click(event.pos)
        elif event.button == 3:  # Right click
            self._handle_right_click(event.pos)

    def _handle_mouse_up(self, event):
        """Handle mouse button release events."""
        self.mouse_buttons.discard(event.button)

    def _handle_mouse_motion(self, event):
        """Handle mouse motion events."""
        self.mouse_pos = event.pos

        # Update UI hover state
        if self.camera:
            world_pos = self.camera.screen_to_world(event.pos)
            tile_x, tile_y = int(world_pos[0] // self.camera.tile_size), int(world_pos[1] // self.camera.tile_size)
            self.ui_state.hover_tile((tile_x, tile_y))

    def _handle_mouse_wheel(self, event):
        """Handle mouse wheel events."""
        if self.camera:
            if event.y > 0:
                self.camera.set_zoom(self.camera.target_zoom * 1.1)
            elif event.y < 0:
                self.camera.set_zoom(self.camera.target_zoom / 1.1)

    def _handle_left_click(self, pos: Tuple[int, int]):
        """Handle left mouse click."""
        if not self.camera:
            return

        # Convert screen to world coordinates
        world_pos = self.camera.screen_to_world(pos)
        tile_x = int(world_pos[0] // self.camera.tile_size)
        tile_y = int(world_pos[1] // self.camera.tile_size)

        # Check for double-click
        current_time = pygame.time.get_ticks()
        is_double_click = (current_time - self.last_click_time) < self.double_click_threshold
        self.last_click_time = current_time

        if is_double_click:
            self._handle_double_click(tile_x, tile_y)
        else:
            self._handle_single_click(tile_x, tile_y)

    def _handle_right_click(self, pos: Tuple[int, int]):
        """Handle right mouse click."""
        if not self.camera:
            return

        # Convert screen to world coordinates
        world_pos = self.camera.screen_to_world(pos)
        tile_x = int(world_pos[0] // self.camera.tile_size)
        tile_y = int(world_pos[1] // self.camera.tile_size)

        # Right click typically cancels selection or shows context menu
        if self.ui_state.selected_unit:
            # Create a mock event for the existing game actions system
            mock_event = type(
                "MockEvent",
                (),
                {
                    "type": pygame.MOUSEBUTTONDOWN,
                    "pos": (tile_x * self.camera.tile_size, tile_y * self.camera.tile_size),
                    "button": 3,
                },
            )()

            # Try to move selected unit to this position
            self.game_actions.handle_mouse_click(mock_event, self.game_state, self.ui_state, self.camera.tile_size)
        else:
            # Cancel any current action
            self.ui_state.reset_selection()

    def _handle_middle_click(self, pos: Tuple[int, int]):
        """Handle middle mouse click."""
        if self.camera and self.camera_controller:
            # Middle click to center camera
            world_pos = self.camera.screen_to_world(pos)
            self.camera.center_on_world_pos(world_pos[0], world_pos[1])

    def _handle_single_click(self, tile_x: int, tile_y: int):
        """Handle single left click."""
        if self.camera:
            # Create a mock event for the existing game actions system
            mock_event = type(
                "MockEvent",
                (),
                {
                    "type": pygame.MOUSEBUTTONDOWN,
                    "pos": (tile_x * self.camera.tile_size, tile_y * self.camera.tile_size),
                    "button": 1,
                },
            )()

            # Use existing game actions for unit selection and movement
            self.game_actions.handle_mouse_click(mock_event, self.game_state, self.ui_state, self.camera.tile_size)

        # If we selected a unit, center camera on it
        if self.ui_state.selected_unit and self.camera_controller and self.camera:
            # Get unit position (would need to be implemented in game state)
            # For now, just center on the clicked tile
            self.camera.center_on_tile(tile_x, tile_y)

    def _handle_double_click(self, tile_x: int, tile_y: int):
        """Handle double left click."""
        # Double-click for quick actions (e.g., move and attack)
        if self.ui_state.selected_unit and self.camera:
            # Create a mock event for the existing game actions system
            mock_event = type(
                "MockEvent",
                (),
                {
                    "type": pygame.MOUSEBUTTONDOWN,
                    "pos": (tile_x * self.camera.tile_size, tile_y * self.camera.tile_size),
                    "button": 1,
                },
            )()

            # Try to perform a quick action
            self.game_actions.handle_mouse_click(mock_event, self.game_state, self.ui_state, self.camera.tile_size)
            # End turn after quick action
            self.game_state.turn_controller.end_turn()

    def _handle_action(self, action: str, is_pressed: bool):
        """Handle bound actions."""
        if not is_pressed:
            return  # Only handle key press, not release for most actions

        # Camera actions
        if action.startswith("camera_") and self.camera_controller:
            fast = pygame.K_LSHIFT in self.keys_held

            if action == "camera_up":
                self.camera_controller.pan("up", fast)
            elif action == "camera_down":
                self.camera_controller.pan("down", fast)
            elif action == "camera_left":
                self.camera_controller.pan("left", fast)
            elif action == "camera_right":
                self.camera_controller.pan("right", fast)
            elif action == "camera_zoom_in":
                self.camera_controller.zoom_in()
            elif action == "camera_zoom_out":
                self.camera_controller.zoom_out()
            elif action == "camera_reset":
                self.camera_controller.reset_zoom()

        # Game actions
        elif action == "end_turn":
            self.game_state.turn_controller.end_turn()
        elif action == "next_unit":
            self._select_next_unit()
        elif action == "cancel_action":
            self.ui_state.reset_selection()
        elif action == "confirm_action":
            self._confirm_current_action()

        # UI toggles
        elif action == "toggle_grid":
            # Toggle grid display (would need UI state support)
            pass
        elif action == "toggle_turn_info":
            # Toggle turn information display
            pass
        elif action == "toggle_help":
            # Toggle help overlay
            pass

    def _handle_mouse_edge_panning(self):
        """Handle mouse edge panning."""
        if not self.camera_controller:
            return

        screen_width = self.camera.screen_width
        screen_height = self.camera.screen_height
        threshold = self.mouse_edge_pan_threshold

        x, y = self.mouse_pos

        # Check edges and pan accordingly
        if x < threshold:
            self.camera_controller.pan("left")
        elif x > screen_width - threshold:
            self.camera_controller.pan("right")

        if y < threshold:
            self.camera_controller.pan("up")
        elif y > screen_height - threshold:
            self.camera_controller.pan("down")

    def _select_next_unit(self):
        """Select next available unit."""
        current_unit = self.game_state.turn_controller.get_current_unit()
        if current_unit:
            self.ui_state.select_unit(current_unit)

            # Center camera on selected unit if possible
            if self.camera_controller:
                # Would need unit position from game state
                # For now, just stop following any target
                self.camera_controller.stop_following()

    def _confirm_current_action(self):
        """Confirm current action (e.g., movement, attack)."""
        if self.ui_state.selected_unit and self.ui_state.hovered_tile and self.camera:
            tile_x, tile_y = self.ui_state.hovered_tile
            # Create a mock event for the existing game actions system
            mock_event = type(
                "MockEvent",
                (),
                {
                    "type": pygame.MOUSEBUTTONDOWN,
                    "pos": (tile_x * self.camera.tile_size, tile_y * self.camera.tile_size),
                    "button": 1,
                },
            )()

            self.game_actions.handle_mouse_click(mock_event, self.game_state, self.ui_state, self.camera.tile_size)

    def set_camera(self, camera: Camera):
        """Set camera instance."""
        self.camera = camera
        self.camera_controller = CameraController(camera) if camera else None

    def get_input_state(self) -> InputState:
        """Get current input state."""
        return self.input_state

    def set_key_binding(self, key: int, action: str):
        """Set custom key binding."""
        self.key_bindings[key] = action

    def enable_feature(self, feature: str, enabled: bool):
        """Enable or disable input features."""
        if feature == "mouse_edge_panning":
            self.enable_mouse_edge_panning = enabled
        elif feature == "keyboard_camera":
            self.enable_keyboard_camera = enabled
        elif feature == "gamepad":
            self.enable_gamepad = enabled

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about input state."""
        return {
            "keys_held": len(self.keys_held),
            "mouse_pos": self.mouse_pos,
            "mouse_buttons": list(self.mouse_buttons),
            "selected_unit": self.ui_state.selected_unit,
            "hovered_tile": self.ui_state.hovered_tile,
            "camera_pos": (self.camera.x, self.camera.y) if self.camera else None,
            "camera_target": (self.camera.target_x, self.camera.target_y) if self.camera else None,
        }
