"""
Sprite Validator - validates sprite sheets with full architecture integration.
Integrated with existing AssetValidator and includes frame slicing and animation validation.
"""

import pygame
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from game.asset_validator import AssetValidator, AssetValidationResult

# @api
# @refactor
class SpriteValidator:
    """Validates sprite sheets with comprehensive frame analysis and animation validation."""

    def __init__(self, asset_dir: Path = None, logger=None):
        self.asset_dir = asset_dir or Path("assets/units")
        self.logger = logger
        self.expected_frame_size = (64, 64)  # Standard sprite frame size
        self.validation_results = {}
        self.qa_report_dir = Path("qa_reports")
        self.qa_report_dir.mkdir(exist_ok=True)

        # Animation definitions
        self.animation_types = {
            "idle": {"expected_frames": 2, "frame_time": 500},
            "walk": {"expected_frames": 3, "frame_time": 200},
            "attack": {"expected_frames": 3, "frame_time": 150},
            "death": {"expected_frames": 2, "frame_time": 300},
            "cast": {"expected_frames": 2, "frame_time": 400}
        }

        # Unit type definitions
        self.unit_types = {
            "knight": {"animations": ["idle", "walk", "attack"]},
            "mage": {"animations": ["idle", "walk", "attack", "cast"]},
            "archer": {"animations": ["idle", "walk", "attack"]},
            "goblin": {"animations": ["idle", "walk", "attack", "death"]},
            "orc": {"animations": ["idle", "walk", "attack"]}
        }

    def validate_all_sprites(self) -> Dict[str, List[AssetValidationResult]]:
        """Validate all sprite sheets in the asset directory."""
        results = {}

        if not self.asset_dir.exists():
            if self.logger:
                self.logger.log_event("sprite_validation_error", {
                    "error": f"Sprite directory not found: {self.asset_dir}"
                })
            return results

        # Validate each unit type
        for unit_type in self.unit_types.keys():
            unit_dir = self.asset_dir / unit_type
            if unit_dir.exists():
                unit_results = self._validate_unit_sprites(unit_type, unit_dir)
                results[unit_type] = unit_results
            else:
                # Missing unit type directory
                result = AssetValidationResult(str(unit_dir))
                result.add_error(f"Missing unit type directory: {unit_type}")
                results[unit_type] = [result]

        # Generate comprehensive reports
        self._generate_sprite_report(results)
        self._generate_sprite_csv(results)

        return results

    def _validate_unit_sprites(self, unit_type: str, unit_dir: Path) -> List[AssetValidationResult]:
        """Validate sprite sheets for a specific unit type."""
        results = []
        expected_animations = self.unit_types[unit_type]["animations"]

        # Check for expected animation sheets
        for anim_type in expected_animations:
            sheet_file = unit_dir / f"{anim_type}.png"
            result = AssetValidationResult(str(sheet_file))

            if sheet_file.exists():
                # Validate the sprite sheet
                self._validate_sprite_sheet(sheet_file, unit_type, anim_type, result)
            else:
                result.add_error(f"Missing animation sheet: {anim_type}.png")

            results.append(result)

        # Check for additional sprite sheets
        for sheet_file in unit_dir.glob("*.png"):
            if sheet_file.name not in [f"{anim}.png" for anim in expected_animations]:
                result = AssetValidationResult(str(sheet_file))
                result.add_warning(f"Unexpected sprite sheet: {sheet_file.name}")
                self._validate_sprite_sheet(sheet_file, unit_type, "unknown", result)
                results.append(result)

        return results

    def _validate_sprite_sheet(self, sheet_file: Path, unit_type: str, anim_type: str, result: AssetValidationResult):
        """Validate an individual sprite sheet."""
        try:
            # Load sprite sheet
            sheet = pygame.image.load(str(sheet_file))
            width, height = sheet.get_size()
            result.metadata["resolution"] = (width, height)
            result.metadata["format"] = "PNG"
            result.metadata["unit_type"] = unit_type
            result.metadata["animation_type"] = anim_type

            # Check if dimensions are valid for frame slicing
            frame_width, frame_height = self.expected_frame_size
            if width % frame_width != 0:
                result.add_error(f"Sheet width {width} not divisible by frame width {frame_width}")

            if height != frame_height:
                result.add_error(f"Sheet height {height} doesn't match frame height {frame_height}")

            # Calculate frame count
            frame_count = width // frame_width
            result.metadata["frame_count"] = frame_count

            # Check frame count against expected
            if anim_type in self.animation_types:
                expected_frames = self.animation_types[anim_type]["expected_frames"]
                if frame_count != expected_frames:
                    result.add_warning(f"Frame count {frame_count} doesn't match expected {expected_frames}")

            # Slice and validate individual frames
            frames = self._slice_sprite_sheet(sheet, frame_count)
            frame_validation = self._validate_frames(frames, unit_type, anim_type)
            result.metadata["frame_validation"] = frame_validation

            # Check for transparency
            if sheet.get_alpha() is not None:
                result.metadata["has_transparency"] = True
            else:
                result.metadata["has_transparency"] = False

            # Check file size
            file_size_mb = sheet_file.stat().st_size / (1024 * 1024)
            if file_size_mb > 2.0:  # 2MB limit for sprite sheets
                result.add_warning(f"Large file size: {file_size_mb:.2f}MB")

            result.metadata["file_size_mb"] = file_size_mb

            # Check for animation consistency
            if frame_count > 1:
                consistency_check = self._check_animation_consistency(frames)
                result.metadata["animation_consistency"] = consistency_check
                if not consistency_check["consistent"]:
                    result.add_warning(f"Animation inconsistency: {consistency_check['issues']}")

        except Exception as e:
            result.add_error(f"Cannot load sprite sheet: {e}")

    def _slice_sprite_sheet(self, sheet: pygame.Surface, frame_count: int) -> List[pygame.Surface]:
        """Slice sprite sheet into individual frames."""
        frames = []
        frame_width, frame_height = self.expected_frame_size

        for i in range(frame_count):
            frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame = sheet.subsurface(frame_rect)
            frames.append(frame)

        return frames

    def _validate_frames(self, frames: List[pygame.Surface], unit_type: str, anim_type: str) -> Dict[str, Any]:
        """Validate individual frames in a sprite sheet."""
        validation = {
            "total_frames": len(frames),
            "valid_frames": 0,
            "frame_issues": [],
            "color_analysis": []
        }

        for i, frame in enumerate(frames):
            frame_valid = True
            frame_issues = []

            # Check frame size
            if frame.get_size() != self.expected_frame_size:
                frame_issues.append(f"Wrong size: {frame.get_size()}")
                frame_valid = False

            # Check for empty/transparent frames
            if self._is_frame_empty(frame):
                frame_issues.append("Empty or fully transparent frame")
                frame_valid = False

            # Analyze frame colors
            color_analysis = self._analyze_frame_colors(frame)
            validation["color_analysis"].append(color_analysis)

            if frame_valid:
                validation["valid_frames"] += 1
            else:
                validation["frame_issues"].append(f"Frame {i}: {', '.join(frame_issues)}")

        return validation

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
            # Fallback: check if frame is mostly transparent
            if frame.get_alpha() is not None:
                # Simple transparency check
                return True
            return False

    def _analyze_frame_colors(self, frame: pygame.Surface) -> Dict[str, Any]:
        """Analyze color characteristics of a frame."""
        try:
            pixels = pygame.surfarray.array3d(frame)

            # Calculate average color
            avg_color = pixels.mean(axis=(0, 1))

            # Calculate color variance
            color_variance = pixels.var(axis=(0, 1)).mean()

            return {
                "average_color": tuple(int(c) for c in avg_color),
                "color_variance": float(color_variance),
                "has_content": color_variance > 100
            }
        except (NotImplementedError, ImportError):
            # Fallback: simple color analysis by sampling
            sample_points = [(0, 0), (frame.get_width()//2, frame.get_height()//2),
                           (frame.get_width()-1, frame.get_height()-1)]

            color_sum = [0, 0, 0]
            sample_count = 0

            for x, y in sample_points:
                if 0 <= x < frame.get_width() and 0 <= y < frame.get_height():
                    color = frame.get_at((x, y))
                    for j in range(3):  # RGB channels
                        color_sum[j] += color[j]
                    sample_count += 1

            if sample_count > 0:
                avg_color = tuple(c // sample_count for c in color_sum)
            else:
                avg_color = (128, 128, 128)

            return {
                "average_color": avg_color,
                "color_variance": 0.0,
                "has_content": True
            }

    def _check_animation_consistency(self, frames: List[pygame.Surface]) -> Dict[str, Any]:
        """Check consistency between animation frames."""
        consistency = {
            "consistent": True,
            "issues": []
        }

        if len(frames) < 2:
            return consistency

        # Check for significant size variations
        sizes = [frame.get_size() for frame in frames]
        if len(set(sizes)) > 1:
            consistency["issues"].append("Inconsistent frame sizes")
            consistency["consistent"] = False

        # Check for dramatic color changes (might indicate wrong frames)
        try:
            # Try to use surfarray for accurate color analysis
            color_analyses = [self._analyze_frame_colors(frame) for frame in frames]
            avg_colors = [analysis["average_color"] for analysis in color_analyses]

            for i in range(1, len(avg_colors)):
                color_diff = sum(abs(c1 - c2) for c1, c2 in zip(avg_colors[i-1], avg_colors[i]))
                if color_diff > 100:  # Large color change
                    consistency["issues"].append(f"Large color change between frames {i-1} and {i}")
                    consistency["consistent"] = False
        except (NotImplementedError, ImportError):
            # Fallback: simple color sampling
            for i in range(1, len(frames)):
                # Sample multiple pixels from each frame for better detection
                sample_points = [(0, 0), (frames[i-1].get_width()//2, frames[i-1].get_height()//2),
                               (frames[i-1].get_width()-1, frames[i-1].get_height()-1)]

                color1_avg = [0, 0, 0]
                color2_avg = [0, 0, 0]
                sample_count = 0

                for x, y in sample_points:
                    if 0 <= x < frames[i-1].get_width() and 0 <= y < frames[i-1].get_height():
                        color1 = frames[i-1].get_at((x, y))
                        color2 = frames[i].get_at((x, y))
                        for j in range(3):  # RGB channels
                            color1_avg[j] += color1[j]
                            color2_avg[j] += color2[j]
                        sample_count += 1

                if sample_count > 0:
                    for j in range(3):
                        color1_avg[j] //= sample_count
                        color2_avg[j] //= sample_count

                    color_diff = sum(abs(c1 - c2) for c1, c2 in zip(color1_avg, color2_avg))
                    if color_diff > 50:  # Lower threshold for fallback
                        consistency["issues"].append(f"Large color change between frames {i-1} and {i}")
                        consistency["consistent"] = False

        return consistency

    def _generate_sprite_report(self, results: Dict[str, List[AssetValidationResult]]):
        """Generate comprehensive sprite validation report."""
        print("\n" + "="*60)
        print("🎭 SPRITE VALIDATION REPORT")
        print("="*60)

        total_sheets = sum(len(unit_results) for unit_results in results.values())
        valid_sheets = sum(sum(1 for r in unit_results if r.is_valid) for unit_results in results.values())
        total_errors = sum(sum(len(r.errors) for r in unit_results) for unit_results in results.values())
        total_warnings = sum(sum(len(r.warnings) for r in unit_results) for unit_results in results.values())

        print(f"📊 Summary:")
        print(f"  🎭 Unit Types: {len(results)}")
        print(f"  📁 Total Sheets: {total_sheets}")
        print(f"  ✅ Valid Sheets: {valid_sheets}")
        print(f"  ❌ Sheets with Errors: {total_sheets - valid_sheets}")
        print(f"  ⚠️  Total Warnings: {total_warnings}")
        print(f"  🚫 Total Errors: {total_errors}")

        if total_sheets > 0:
            success_rate = (valid_sheets / total_sheets) * 100
            print(f"  📈 Success Rate: {success_rate:.1f}%")

        # Report by unit type
        for unit_type, unit_results in results.items():
            if not unit_results:
                continue

            unit_errors = sum(len(r.errors) for r in unit_results)
            unit_warnings = sum(len(r.warnings) for r in unit_results)
            unit_valid = sum(1 for r in unit_results if r.is_valid)

            print(f"\n🎭 {unit_type.title()} Unit:")
            print(f"  📁 Sheets: {len(unit_results)}")
            print(f"  ✅ Valid: {unit_valid}")
            print(f"  ❌ Errors: {unit_errors}")
            print(f"  ⚠️  Warnings: {unit_warnings}")

            # Show animation breakdown
            for result in unit_results:
                anim_type = result.metadata.get("animation_type", "unknown")
                frame_count = result.metadata.get("frame_count", 0)
                print(f"    🎬 {anim_type}: {frame_count} frames")

                if result.errors:
                    print(f"      ❌ Errors: {', '.join(result.errors)}")
                if result.warnings:
                    print(f"      ⚠️  Warnings: {', '.join(result.warnings)}")

        print("\n" + "="*60)

        # Log report
        if self.logger:
            self.logger.log_event("sprite_validation_complete", {
                "unit_types": len(results),
                "total_sheets": total_sheets,
                "valid_sheets": valid_sheets,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "success_rate": (valid_sheets / total_sheets * 100) if total_sheets > 0 else 0
            })

    def _generate_sprite_csv(self, results: Dict[str, List[AssetValidationResult]]):
        """Generate CSV report for sprite validation."""
        csv_file = self.qa_report_dir / "sprite_report.csv"

        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "unit_type", "animation_type", "file_name", "file_path", "width", "height",
                "frame_count", "valid", "has_transparency", "file_size_mb", "errors", "warnings"
            ])
            writer.writeheader()

            for unit_type, unit_results in results.items():
                for result in unit_results:
                    file_path = Path(result.asset_path)
                    writer.writerow({
                        "unit_type": unit_type,
                        "animation_type": result.metadata.get("animation_type", "unknown"),
                        "file_name": file_path.name,
                        "file_path": str(file_path),
                        "width": result.metadata.get("resolution", (0, 0))[0],
                        "height": result.metadata.get("resolution", (0, 0))[1],
                        "frame_count": result.metadata.get("frame_count", 0),
                        "valid": result.is_valid,
                        "has_transparency": result.metadata.get("has_transparency", False),
                        "file_size_mb": result.metadata.get("file_size_mb", 0),
                        "errors": "; ".join(result.errors),
                        "warnings": "; ".join(result.warnings)
                    })

        print(f"📊 CSV Report saved: {csv_file}")

    def get_sprite_manifest(self) -> Dict[str, Any]:
        """Generate sprite manifest for the game."""
        manifest = {
            "version": "1.0",
            "unit_types": {},
            "total_sheets": 0,
            "validation_summary": {}
        }

        # Validate all sprites first
        validation_results = self.validate_all_sprites()

        for unit_type, unit_results in validation_results.items():
            unit_manifest = {
                "count": len(unit_results),
                "valid_count": sum(1 for r in unit_results if r.is_valid),
                "animations": {}
            }

            for result in unit_results:
                if result.is_valid:
                    anim_type = result.metadata.get("animation_type", "unknown")
                    unit_manifest["animations"][anim_type] = {
                        "file": Path(result.asset_path).name,
                        "path": result.asset_path,
                        "frame_count": result.metadata.get("frame_count", 0),
                        "metadata": result.metadata
                    }

            manifest["unit_types"][unit_type] = unit_manifest
            manifest["total_sheets"] += len(unit_results)

        # Save manifest
        manifest_file = self.qa_report_dir / "sprite_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"📋 Sprite manifest saved: {manifest_file}")
        return manifest

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of sprite validation."""
        if not self.validation_results:
            return {"status": "no_validation_run"}

        total_sheets = sum(len(results) for results in self.validation_results.values())
        valid_sheets = sum(sum(1 for r in results if r.is_valid) for results in self.validation_results.values())

        return {
            "unit_types": len(self.validation_results),
            "total_sheets": total_sheets,
            "valid_sheets": valid_sheets,
            "success_rate": (valid_sheets / total_sheets * 100) if total_sheets > 0 else 0
        }

# Standalone validation function for backward compatibility
def validate_sprites(asset_dir: Path = None, logger=None) -> Dict[str, List[AssetValidationResult]]:
    """Standalone sprite validation function."""
    validator = SpriteValidator(asset_dir, logger)
    return validator.validate_all_sprites()

def generate_sprite_report(asset_dir: Path = None) -> bool:
    """Generate comprehensive sprite report."""
    try:
        validator = SpriteValidator(asset_dir)
        manifest = validator.get_sprite_manifest()
        return True
    except Exception as e:
        print(f"Error generating sprite report: {e}")
        return False
