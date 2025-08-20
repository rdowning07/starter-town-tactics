"""
Camera system for smooth panning and viewport management.
Integrates with existing renderer and UI systems.
"""

from typing import Tuple, Optional
import math


class Camera:
    """
    Camera system for smooth panning and viewport management.
    
    Provides smooth camera movement, viewport calculations, and coordinate transformations
    between world space and screen space.
    """
    
    def __init__(self, screen_size: Tuple[int, int], tile_size: int = 32, world_size: Optional[Tuple[int, int]] = None):
        """
        Initialize camera.
        
        Args:
            screen_size: (width, height) of the screen in pixels
            tile_size: Size of each tile in pixels
            world_size: Optional (width, height) of the world in tiles for bounds checking
        """
        self.screen_width, self.screen_height = screen_size
        self.tile_size = tile_size
        self.world_width, self.world_height = world_size or (100, 100)
        
        # Camera position (in world pixels)
        self.x = 0.0
        self.y = 0.0
        
        # Target position for smooth movement
        self.target_x = 0.0
        self.target_y = 0.0
        
        # Smooth movement settings
        self.smooth_factor = 0.1
        self.min_movement_threshold = 0.5  # Stop moving when close enough to target
        
        # Camera bounds (in world pixels)
        self.min_x = 0
        self.min_y = 0
        self.max_x = max(0, self.world_width * tile_size - screen_size[0])
        self.max_y = max(0, self.world_height * tile_size - screen_size[1])
        
        # Zoom support (for future expansion)
        self.zoom = 1.0
        self.target_zoom = 1.0
        
    def update(self, dt: float = 1.0):
        """
        Update camera position with smooth movement.
        
        Args:
            dt: Delta time (not used in current implementation but available for frame-rate independence)
        """
        # Smooth movement towards target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        # Only move if we're far enough from target
        if abs(dx) > self.min_movement_threshold or abs(dy) > self.min_movement_threshold:
            self.x += dx * self.smooth_factor
            self.y += dy * self.smooth_factor
        else:
            # Snap to target when close enough
            self.x = self.target_x
            self.y = self.target_y
        
        # Apply bounds
        self._apply_bounds()
        
        # Smooth zoom (for future use)
        if abs(self.target_zoom - self.zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * self.smooth_factor
        else:
            self.zoom = self.target_zoom
    
    def set_target(self, x: float, y: float):
        """
        Set camera target position in world coordinates.
        
        Args:
            x: Target X position in world pixels
            y: Target Y position in world pixels
        """
        self.target_x = x
        self.target_y = y
    
    def move_target(self, dx: float, dy: float):
        """
        Move camera target by a relative amount.
        
        Args:
            dx: Relative X movement in world pixels
            dy: Relative Y movement in world pixels
        """
        self.set_target(self.target_x + dx, self.target_y + dy)
    
    def center_on_tile(self, tile_x: int, tile_y: int):
        """
        Center camera on a specific tile.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
        """
        world_x = tile_x * self.tile_size
        world_y = tile_y * self.tile_size
        target_x = world_x - self.screen_width // 2
        target_y = world_y - self.screen_height // 2
        self.set_target(target_x, target_y)
    
    def center_on_world_pos(self, world_x: float, world_y: float):
        """
        Center camera on a specific world position.
        
        Args:
            world_x: World X coordinate in pixels
            world_y: World Y coordinate in pixels
        """
        target_x = world_x - self.screen_width // 2
        target_y = world_y - self.screen_height // 2
        self.set_target(target_x, target_y)
    
    def snap_to_target(self):
        """Immediately snap camera to target position (no smooth movement)."""
        self.x = self.target_x
        self.y = self.target_y
        self._apply_bounds()
    
    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: (x, y) position in world pixels
            
        Returns:
            (x, y) position in screen pixels
        """
        screen_x = int((world_pos[0] - self.x) * self.zoom)
        screen_y = int((world_pos[1] - self.y) * self.zoom)
        return screen_x, screen_y
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: (x, y) position in screen pixels
            
        Returns:
            (x, y) position in world pixels
        """
        world_x = screen_pos[0] / self.zoom + self.x
        world_y = screen_pos[1] / self.zoom + self.y
        return world_x, world_y
    
    def screen_to_tile(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convert screen coordinates to tile coordinates.
        
        Args:
            screen_pos: (x, y) position in screen pixels
            
        Returns:
            (x, y) tile coordinates
        """
        world_x, world_y = self.screen_to_world(screen_pos)
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)
        return tile_x, tile_y
    
    def tile_to_screen(self, tile_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convert tile coordinates to screen coordinates.
        
        Args:
            tile_pos: (x, y) tile coordinates
            
        Returns:
            (x, y) position in screen pixels
        """
        world_x = tile_pos[0] * self.tile_size
        world_y = tile_pos[1] * self.tile_size
        return self.world_to_screen((world_x, world_y))
    
    def get_visible_tiles(self) -> Tuple[int, int, int, int]:
        """
        Get the range of tiles visible on screen.
        
        Returns:
            (start_x, start_y, end_x, end_y) tile coordinates
        """
        # Calculate world coordinates of screen corners
        top_left_world = self.screen_to_world((0, 0))
        bottom_right_world = self.screen_to_world((self.screen_width, self.screen_height))
        
        # Convert to tile coordinates with padding
        start_x = max(0, int(top_left_world[0] // self.tile_size) - 1)
        start_y = max(0, int(top_left_world[1] // self.tile_size) - 1)
        end_x = min(self.world_width, int(bottom_right_world[0] // self.tile_size) + 2)
        end_y = min(self.world_height, int(bottom_right_world[1] // self.tile_size) + 2)
        
        return start_x, start_y, end_x, end_y
    
    def is_tile_visible(self, tile_x: int, tile_y: int) -> bool:
        """
        Check if a tile is visible on screen.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            
        Returns:
            True if tile is visible
        """
        start_x, start_y, end_x, end_y = self.get_visible_tiles()
        return start_x <= tile_x < end_x and start_y <= tile_y < end_y
    
    def is_world_pos_visible(self, world_x: float, world_y: float) -> bool:
        """
        Check if a world position is visible on screen.
        
        Args:
            world_x: World X coordinate in pixels
            world_y: World Y coordinate in pixels
            
        Returns:
            True if position is visible
        """
        screen_x, screen_y = self.world_to_screen((world_x, world_y))
        return 0 <= screen_x <= self.screen_width and 0 <= screen_y <= self.screen_height
    
    def set_world_bounds(self, world_width: int, world_height: int):
        """
        Set world bounds for camera movement.
        
        Args:
            world_width: World width in tiles
            world_height: World height in tiles
        """
        self.world_width = world_width
        self.world_height = world_height
        self.max_x = max(0, world_width * self.tile_size - self.screen_width)
        self.max_y = max(0, world_height * self.tile_size - self.screen_height)
        self._apply_bounds()
    
    def set_zoom(self, zoom: float):
        """
        Set target zoom level.
        
        Args:
            zoom: Target zoom level (1.0 = normal, >1.0 = zoomed in, <1.0 = zoomed out)
        """
        self.target_zoom = max(0.1, min(5.0, zoom))  # Clamp zoom between 0.1x and 5.0x
    
    def get_camera_info(self) -> dict:
        """
        Get camera information for debugging/UI.
        
        Returns:
            Dictionary with camera state information
        """
        return {
            "position": (self.x, self.y),
            "target": (self.target_x, self.target_y),
            "zoom": self.zoom,
            "target_zoom": self.target_zoom,
            "visible_tiles": self.get_visible_tiles(),
            "world_bounds": (self.world_width, self.world_height),
            "screen_size": (self.screen_width, self.screen_height)
        }
    
    def _apply_bounds(self):
        """Apply camera bounds to prevent going outside world."""
        self.x = max(self.min_x, min(self.x, self.max_x))
        self.y = max(self.min_y, min(self.y, self.max_y))
        self.target_x = max(self.min_x, min(self.target_x, self.max_x))
        self.target_y = max(self.min_y, min(self.target_y, self.max_y))


class CameraController:
    """
    High-level camera controller for common camera operations.
    Provides convenience methods for camera control in game contexts.
    """
    
    def __init__(self, camera: Camera):
        """
        Initialize camera controller.
        
        Args:
            camera: Camera instance to control
        """
        self.camera = camera
        self.follow_target: Optional[Tuple[float, float]] = None
        self.follow_offset: Tuple[float, float] = (0, 0)
        self.follow_smoothing = 0.05
        
        # Pan settings
        self.pan_speed = 64  # pixels per pan step
        self.fast_pan_speed = 128
        
    def update(self, dt: float = 1.0):
        """
        Update camera controller.
        
        Args:
            dt: Delta time
        """
        # Handle target following
        if self.follow_target:
            target_x, target_y = self.follow_target
            target_x += self.follow_offset[0]
            target_y += self.follow_offset[1]
            
            # Smooth follow
            current_center_x = self.camera.x + self.camera.screen_width // 2
            current_center_y = self.camera.y + self.camera.screen_height // 2
            
            dx = target_x - current_center_x
            dy = target_y - current_center_y
            
            if abs(dx) > 5 or abs(dy) > 5:  # Only follow if target moved significantly
                new_target_x = self.camera.target_x + dx * self.follow_smoothing
                new_target_y = self.camera.target_y + dy * self.follow_smoothing
                self.camera.set_target(new_target_x, new_target_y)
        
        # Update camera
        self.camera.update(dt)
    
    def pan(self, direction: str, fast: bool = False):
        """
        Pan camera in a direction.
        
        Args:
            direction: One of 'up', 'down', 'left', 'right'
            fast: Use fast pan speed if True
        """
        speed = self.fast_pan_speed if fast else self.pan_speed
        
        if direction == 'up':
            self.camera.move_target(0, -speed)
        elif direction == 'down':
            self.camera.move_target(0, speed)
        elif direction == 'left':
            self.camera.move_target(-speed, 0)
        elif direction == 'right':
            self.camera.move_target(speed, 0)
    
    def follow_unit(self, unit_pos: Tuple[float, float], offset: Tuple[float, float] = (0, 0)):
        """
        Set camera to follow a unit.
        
        Args:
            unit_pos: (x, y) position of unit in world pixels
            offset: (x, y) offset from unit position
        """
        self.follow_target = unit_pos
        self.follow_offset = offset
    
    def stop_following(self):
        """Stop following any target."""
        self.follow_target = None
    
    def center_on_unit(self, unit_pos: Tuple[float, float]):
        """
        Center camera on a unit immediately.
        
        Args:
            unit_pos: (x, y) position of unit in world pixels
        """
        self.camera.center_on_world_pos(unit_pos[0], unit_pos[1])
    
    def zoom_in(self):
        """Zoom camera in."""
        current_zoom = self.camera.target_zoom
        self.camera.set_zoom(current_zoom * 1.2)
    
    def zoom_out(self):
        """Zoom camera out."""
        current_zoom = self.camera.target_zoom
        self.camera.set_zoom(current_zoom / 1.2)
    
    def reset_zoom(self):
        """Reset zoom to 1.0."""
        self.camera.set_zoom(1.0)


# Global camera instance (for easy access across systems)
_global_camera: Optional[Camera] = None
_global_camera_controller: Optional[CameraController] = None


def initialize_camera(screen_size: Tuple[int, int], tile_size: int = 32, world_size: Optional[Tuple[int, int]] = None) -> Camera:
    """
    Initialize global camera instance.
    
    Args:
        screen_size: (width, height) of the screen in pixels
        tile_size: Size of each tile in pixels
        world_size: Optional (width, height) of the world in tiles
        
    Returns:
        Initialized camera instance
    """
    global _global_camera, _global_camera_controller
    _global_camera = Camera(screen_size, tile_size, world_size)
    _global_camera_controller = CameraController(_global_camera)
    return _global_camera


def get_camera() -> Optional[Camera]:
    """Get global camera instance."""
    return _global_camera


def get_camera_controller() -> Optional[CameraController]:
    """Get global camera controller instance."""
    return _global_camera_controller
