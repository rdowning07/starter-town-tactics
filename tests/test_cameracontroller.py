import os
import sys

import pygame
import pytest

# Add the parent directory to the path so we can import CameraController
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CameraController import CameraController

# Initialize pygame for testing
pygame.init()

# Test setup
screen_width, screen_height = 800, 600


@pytest.fixture
def camera():
    """Create a fresh camera instance for each test."""
    return CameraController(screen_width, screen_height)


# Mock player target
player = pygame.Vector2(100, 100)


# Test: Camera movement to a specific point
def test_move_to(camera):
    camera.move_to(300, 400)
    assert camera.position.x == 300
    assert camera.position.y == 400


# Test: Camera following a target (e.g., player)
def test_follow_target(camera):
    camera.follow_target(player)
    assert camera.target == player


# Test: Smooth move to a new target
def test_smooth_move_to(camera):
    initial_position = camera.position.copy()
    camera.smooth_move_to(pygame.Vector2(300, 400), speed=20)  # Higher speed
    # Call update multiple times to actually move the camera
    for _ in range(50):  # More updates
        camera.update()
    assert camera.position != initial_position  # Camera should have moved
    assert camera.position.x == pytest.approx(300, abs=10)  # Check close to target
    assert camera.position.y == pytest.approx(400, abs=10)


# Test: Cinematic panning functionality
def test_cinematic_pan(camera):
    # Setup multiple targets for cinematic pan
    targets = [pygame.Vector2(200, 200), pygame.Vector2(400, 400), pygame.Vector2(600, 600)]

    camera.cinematic_pan(targets, speed=30)  # Higher speed

    # Update camera to simulate movement
    for _ in range(500):  # Many more frames to ensure completion
        camera.update()

    # Check that the camera reached the last target
    assert camera.position.x == pytest.approx(600, abs=20)
    assert camera.position.y == pytest.approx(600, abs=20)
    assert camera.panning == False  # Ensure panning has finished


# Test: Camera update with no target (should not move)
def test_camera_update_no_target(camera):
    initial_position = camera.position.copy()
    camera.update()
    assert camera.position == initial_position  # Camera shouldn't move if no target


# Test: Camera following and smooth movement combined
def test_camera_follow_and_smooth_move(camera):
    camera.follow_target(player)
    # Update multiple times to reach the player
    for _ in range(50):
        camera.update()
    assert camera.position.x == pytest.approx(player.x, abs=10)
    assert camera.position.y == pytest.approx(player.y, abs=10)

    # Clear the target so smooth movement can work
    camera.target = None

    # After following, move to a new location smoothly
    camera.smooth_move_to(pygame.Vector2(500, 500), speed=50)  # Higher speed
    # Update multiple times to reach the new target
    for _ in range(200):  # Many more updates to reach the target
        camera.update()
    assert camera.position.x == pytest.approx(500, abs=10)
    assert camera.position.y == pytest.approx(500, abs=10)


if __name__ == "__main__":
    pytest.main()
