"""
Animation Manager - manages sprite animations with QA hooks and validation.
Integrated with existing architecture and includes comprehensive animation validation.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pygame

from game.sprite_validator import SpriteValidator


# @api
# @refactor
class Animation:
    """Represents a sprite animation with validation and QA hooks."""

    def __init__(self, frames: List[pygame.Surface], frame_time: int = 100, name: str = "unknown"):
        self.frames = frames
        self.frame_time = frame_time
        self.name = name
        self.index = 0
        self.timer = 0
        self.playing = True
        self.loop = True

        # Validation data
        self.frame_count = len(frames)
        self.total_duration = frame_time * len(frames)

        # QA tracking
        self.play_count = 0
        self.frame_errors = []
        self.last_frame_time = 0

        # Validate animation
        self.valid = self._validate_animation()

    def _validate_animation(self) -> bool:
        """Validate animation frames."""
        if not self.frames:
            return False

        # Check all frames have same size
        frame_size = self.frames[0].get_size()
        for i, frame in enumerate(self.frames):
            if frame.get_size() != frame_size:
                self.frame_errors.append(f"Frame {i} has wrong size: {frame.get_size()}")
                return False

        # Check for empty frames
        for i, frame in enumerate(self.frames):
            if self._is_frame_empty(frame):
                self.frame_errors.append(f"Frame {i} is empty or transparent")
                return False

        return True

    def _is_frame_empty(self, frame: pygame.Surface) -> bool:
        """Check if frame is empty or fully transparent."""
        try:
            # Convert to array for analysis
            pixels = pygame.surfarray.array3d(frame)

            # Check if all pixels are transparent or very similar
            if frame.get_alpha() is not None:
                alpha = pygame.surfarray.array3d(frame.convert_alpha())[:, :, 3]
                if alpha.max() < 10:  # Very low alpha
                    return True

            # Check if all pixels are very similar (likely empty)
            color_variance = pixels.var(axis=(0, 1)).mean()
            return color_variance < 100  # Low variance indicates empty frame
        except (NotImplementedError, ImportError):
            # Fallback: simple transparency check
            if frame.get_alpha() is not None:
                # Sample a few pixels to check if frame is mostly transparent
                sample_points = [
                    (0, 0),
                    (frame.get_width() // 2, frame.get_height() // 2),
                    (frame.get_width() - 1, frame.get_height() - 1),
                ]
                transparent_count = 0
                for x, y in sample_points:
                    if 0 <= x < frame.get_width() and 0 <= y < frame.get_height():
                        color = frame.get_at((x, y))
                        if len(color) >= 4 and color[3] < 10:  # Very low alpha
                            transparent_count += 1
                return transparent_count >= len(sample_points) * 0.8  # 80% transparent
            return False

    def update(self, dt: int):
        """Update animation frame."""
        if not self.playing or not self.valid:
            return

        self.timer += dt
        if self.timer >= self.frame_time:
            self.index = (self.index + 1) % len(self.frames)
            self.timer = 0

            # Track frame timing for QA
            current_time = time.time()
            if self.last_frame_time > 0:
                actual_frame_time = (current_time - self.last_frame_time) * 1000
                if abs(actual_frame_time - self.frame_time) > 50:  # 50ms tolerance
                    self.frame_errors.append(f"Frame timing off: {actual_frame_time:.1f}ms vs {self.frame_time}ms")
            self.last_frame_time = current_time

    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Get current animation frame."""
        if not self.valid or not self.frames:
            return None

        self.play_count += 1
        return self.frames[self.index]

    def reset(self):
        """Reset animation to beginning."""
        self.index = 0
        self.timer = 0
        self.playing = True

    def pause(self):
        """Pause animation."""
        self.playing = False

    def resume(self):
        """Resume animation."""
        self.playing = True

    def set_frame_time(self, frame_time: int):
        """Set animation frame time."""
        self.frame_time = frame_time
        self.total_duration = frame_time * len(self.frames)

    def get_qa_data(self) -> Dict[str, Any]:
        """Get QA data for this animation."""
        return {
            "name": self.name,
            "valid": self.valid,
            "frame_count": self.frame_count,
            "frame_time": self.frame_time,
            "total_duration": self.total_duration,
            "play_count": self.play_count,
            "frame_errors": self.frame_errors,
            "frame_size": self.frames[0].get_size() if self.frames else (0, 0),
        }


class AnimationManager:
    """Manages multiple animations with QA hooks and validation."""

    def __init__(self, sprite_validator: Optional[SpriteValidator] = None, logger=None):
        self.animations: Dict[str, Animation] = {}
        self.sprite_validator = sprite_validator
        self.logger = logger
        self.qa_data = {"total_animations": 0, "valid_animations": 0, "total_play_time": 0, "animation_errors": []}

    def load_animation(self, name: str, sprite_sheet_path: Path, frame_time: int = 100) -> bool:
        """Load animation from sprite sheet."""
        try:
            if not sprite_sheet_path.exists():
                if self.logger:
                    self.logger.log_event(
                        "animation_load_error", {"name": name, "error": f"Sprite sheet not found: {sprite_sheet_path}"}
                    )
                return False

            # Load sprite sheet
            sheet = pygame.image.load(str(sprite_sheet_path))

            # Slice into frames (assuming horizontal sprite sheet)
            frame_width = 64  # Standard frame width
            frame_height = 64  # Standard frame height

            frames = []
            sheet_width = sheet.get_width()
            frame_count = sheet_width // frame_width

            for i in range(frame_count):
                frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                frame = sheet.subsurface(frame_rect)
                frames.append(frame)

            # Create animation
            animation = Animation(frames, frame_time, name)
            self.animations[name] = animation

            # Update QA data
            self.qa_data["total_animations"] += 1
            if animation.valid:
                self.qa_data["valid_animations"] += 1
            else:
                self.qa_data["animation_errors"].append(f"{name}: {animation.frame_errors}")

            if self.logger:
                self.logger.log_event(
                    "animation_loaded", {"name": name, "frame_count": frame_count, "valid": animation.valid}
                )

            return True

        except Exception as e:
            if self.logger:
                self.logger.log_event("animation_load_error", {"name": name, "error": str(e)})
            return False

    def load_unit_animations(self, unit_type: str, unit_dir: Path) -> Dict[str, bool]:
        """Load all animations for a unit type."""
        results = {}

        if not unit_dir.exists():
            if self.logger:
                self.logger.log_event(
                    "unit_animations_load_error",
                    {"unit_type": unit_type, "error": f"Unit directory not found: {unit_dir}"},
                )
            return results

        # Animation frame times
        frame_times = {"idle": 500, "walk": 200, "attack": 150, "death": 300, "cast": 400}

        # Load each animation
        for anim_file in unit_dir.glob("*.png"):
            anim_name = f"{unit_type}_{anim_file.stem}"
            frame_time = frame_times.get(anim_file.stem, 200)

            success = self.load_animation(anim_name, anim_file, frame_time)
            results[anim_name] = success

        return results

    def get_animation(self, name: str) -> Optional[Animation]:
        """Get animation by name."""
        return self.animations.get(name)

    def play_animation(self, name: str):
        """Start playing an animation."""
        animation = self.get_animation(name)
        if animation:
            animation.playing = True
            animation.reset()

    def pause_animation(self, name: str):
        """Pause an animation."""
        animation = self.get_animation(name)
        if animation:
            animation.pause()

    def update_animations(self, dt: int):
        """Update all animations."""
        for animation in self.animations.values():
            animation.update(dt)
            if animation.playing:
                self.qa_data["total_play_time"] += dt

    def render_animation(self, screen: pygame.Surface, name: str, position: Tuple[int, int]):
        """Render an animation at position."""
        animation = self.get_animation(name)
        if animation and animation.valid:
            current_frame = animation.get_current_frame()
            if current_frame:
                screen.blit(current_frame, position)
                return True
        return False

    def get_animation_status(self, name: str) -> Dict[str, Any]:
        """Get status of an animation."""
        animation = self.get_animation(name)
        if animation:
            return {
                "name": animation.name,
                "valid": animation.valid,
                "playing": animation.playing,
                "current_frame": animation.index,
                "frame_count": animation.frame_count,
                "play_count": animation.play_count,
                "frame_errors": animation.frame_errors,
            }
        return {"error": "Animation not found"}

    def get_qa_report(self) -> Dict[str, Any]:
        """Get comprehensive QA report for all animations."""
        report = {"summary": self.qa_data.copy(), "animations": {}}

        for name, animation in self.animations.items():
            report["animations"][name] = animation.get_qa_data()

        # Calculate success rate
        if self.qa_data["total_animations"] > 0:
            success_rate = (self.qa_data["valid_animations"] / self.qa_data["total_animations"]) * 100
            report["summary"]["success_rate"] = success_rate

        return report

    def validate_all_animations(self) -> Dict[str, List[str]]:
        """Validate all loaded animations and return issues."""
        issues = {}

        for name, animation in self.animations.items():
            if not animation.valid:
                issues[name] = animation.frame_errors

        return issues

    def export_qa_data(self, output_file: Path):
        """Export QA data to file."""
        import json

        qa_report = self.get_qa_report()

        with open(output_file, "w") as f:
            json.dump(qa_report, f, indent=2)

        print(f"📊 Animation QA report saved: {output_file}")

    def reset_qa_data(self):
        """Reset QA tracking data."""
        self.qa_data = {
            "total_animations": len(self.animations),
            "valid_animations": sum(1 for anim in self.animations.values() if anim.valid),
            "total_play_time": 0,
            "animation_errors": [],
        }

        for animation in self.animations.values():
            animation.play_count = 0
            animation.frame_errors = []


# Global animation manager instance
_animation_manager = None


def get_animation_manager() -> AnimationManager:
    """Get global animation manager instance."""
    global _animation_manager
    if _animation_manager is None:
        _animation_manager = AnimationManager()
    return _animation_manager


def load_animation(name: str, sprite_sheet_path: Path, frame_time: int = 100) -> bool:
    """Load animation using global manager."""
    manager = get_animation_manager()
    return manager.load_animation(name, sprite_sheet_path, frame_time)


def play_animation(name: str):
    """Play animation using global manager."""
    manager = get_animation_manager()
    manager.play_animation(name)


def render_animation(screen: pygame.Surface, name: str, position: Tuple[int, int]) -> bool:
    """Render animation using global manager."""
    manager = get_animation_manager()
    return manager.render_animation(screen, name, position)
