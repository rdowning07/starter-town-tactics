import pygame


class CameraController:
    def __init__(self, screen_width, screen_height):
        # Screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Initial camera position
        self.position = pygame.Vector2(0, 0)
        self.target = None  # Will be set when following a unit

        # Movement speed for transitions
        self.speed = 5
        self.panning = False
        self.panning_targets = []
        self.current_target_index = 0

        # For smooth movement
        self.smooth_target = None
        self.smooth_speed = 5

    def move_to(self, x, y):
        """Instantly move the camera to a target position."""
        self.position = pygame.Vector2(x, y)

    def follow_target(self, target):
        """Start following a target (unit or position)."""
        self.target = target

    def smooth_move_to(self, target, speed=None):
        """Set a smooth movement target - actual movement happens in update()."""
        if speed is None:
            speed = self.speed
        self.smooth_target = pygame.Vector2(target[0], target[1])
        self.smooth_speed = speed

    def cinematic_pan(self, targets, speed=5):
        """Perform cinematic panning across multiple targets."""
        self.panning = True
        self.panning_targets = targets.copy()
        self.speed = speed
        self.current_target_index = 0
        # Start with the first target
        if self.panning_targets:
            self.smooth_move_to(self.panning_targets[0], speed)

    def update(self):
        """Update camera position based on target or cinematic pan."""
        # Handle smooth movement
        if self.smooth_target:
            direction = self.smooth_target - self.position
            distance = direction.length()

            if distance > self.smooth_speed:  # Use speed as threshold
                direction.normalize_ip()
                self.position += direction * self.smooth_speed
            else:
                # Close enough, snap to target
                self.position = self.smooth_target
                self.smooth_target = None

                # If we're panning, move to next target
                if self.panning and self.panning_targets:
                    self.current_target_index += 1
                    if self.current_target_index < len(self.panning_targets):
                        next_target = self.panning_targets[self.current_target_index]
                        self.smooth_move_to(next_target, self.speed)
                    else:
                        # Finished all targets
                        self.panning = False

        # Handle target following (only if not doing smooth movement)
        elif self.target:
            # Convert target to Vector2 if it's not already
            if hasattr(self.target, "x") and hasattr(self.target, "y"):
                target_pos = pygame.Vector2(self.target.x, self.target.y)
            else:
                target_pos = pygame.Vector2(self.target[0], self.target[1])

            direction = target_pos - self.position
            distance = direction.length()

            if distance > self.speed:  # Use speed as threshold
                direction.normalize_ip()
                self.position += direction * self.speed

    def get_viewport(self):
        """Returns the portion of the world the camera can see."""
        return pygame.Rect(self.position.x, self.position.y, self.screen_width, self.screen_height)
