"""
Asset Validator - comprehensive asset validation with full architecture integration.
Validates terrain tiles, sprites, animations, and integrates with existing QA systems.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from PIL import Image

from game.ui.asset_qa_scene import AssetQAScene
from game.ui.particle_qa_scene import ParticleQAScene


# @api
# @refactor
class AssetValidationResult:
    """Result of asset validation."""

    def __init__(self, asset_path: str):
        self.asset_path = asset_path
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.metadata = {}

    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add validation warning."""
        self.warnings.append(warning)


class AssetValidator:
    """Comprehensive asset validation with full architecture integration."""

    def __init__(self, asset_dir: Path = None, logger=None):
        self.asset_dir = asset_dir or Path("assets")
        self.logger = logger
        self.validation_rules = self._create_validation_rules()
        self.validation_results = {}
        self.duplicate_hashes = {}

    def _create_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Define validation rules for different asset types."""
        return {
            "terrain": {
                "expected_resolution": (32, 32),
                "allowed_extensions": [".png"],
                "required_subdirs": ["grass", "stone", "water", "forest", "mountain"],
                "max_file_size_mb": 1,
                "naming_pattern": r"^[a-z_]+\.(png)$",
            },
            "units": {
                "expected_resolution": (64, 64),
                "allowed_extensions": [".png"],
                "required_subdirs": ["idle", "walk", "attack"],
                "max_file_size_mb": 2,
                "naming_pattern": r"^[a-zA-Z_0-9]+\.(png)$",
                "animation_frames": {"idle": 2, "walk": 3, "attack": 3},
            },
            "ui": {
                "expected_resolution": None,  # Variable resolution
                "allowed_extensions": [".png"],
                "required_subdirs": ["buttons", "panels", "cursors", "icons"],
                "max_file_size_mb": 0.5,
                "naming_pattern": r"^[a-z_]+\.(png)$",
            },
            "effects": {
                "expected_resolution": None,  # Variable resolution
                "allowed_extensions": [".png"],
                "required_subdirs": ["particles", "animations"],
                "max_file_size_mb": 1,
                "naming_pattern": r"^[a-z_0-9]+\.(png)$",
            },
            "sfx": {
                "expected_resolution": None,  # Not applicable
                "allowed_extensions": [".wav", ".ogg", ".mp3"],
                "required_subdirs": [],
                "max_file_size_mb": 5,
                "naming_pattern": r"^[a-z_]+\.(wav|ogg|mp3)$",
            },
        }

    def validate_all_assets(self) -> Dict[str, List[AssetValidationResult]]:
        """Validate all assets in the asset directory."""
        all_results = {}

        if not self.asset_dir.exists():
            if self.logger:
                self.logger.log_event(
                    "asset_validation_error", {"error": f"Asset directory not found: {self.asset_dir}"}
                )
            return all_results

        # Validate each asset type
        for asset_type, rules in self.validation_rules.items():
            type_dir = self.asset_dir / asset_type
            if type_dir.exists():
                results = self._validate_asset_type(asset_type, type_dir, rules)
                all_results[asset_type] = results
            else:
                # Missing asset type directory
                result = AssetValidationResult(str(type_dir))
                result.add_error(f"Missing asset type directory: {asset_type}")
                all_results[asset_type] = [result]

        # Check for duplicates across all assets
        self._check_for_duplicates(all_results)

        # Generate comprehensive report
        self._generate_validation_report(all_results)

        return all_results

    def _validate_asset_type(
        self, asset_type: str, type_dir: Path, rules: Dict[str, Any]
    ) -> List[AssetValidationResult]:
        """Validate assets of a specific type."""
        results = []

        # Check required subdirectories
        if rules.get("required_subdirs"):
            for required_subdir in rules["required_subdirs"]:
                subdir_path = type_dir / required_subdir
                if not subdir_path.exists():
                    result = AssetValidationResult(str(subdir_path))
                    result.add_error(f"Missing required subdirectory: {required_subdir}")
                    results.append(result)

        # Validate individual files
        for file_path in type_dir.rglob("*"):
            if file_path.is_file():
                result = self._validate_individual_asset(file_path, rules, asset_type)
                results.append(result)

        # Special validation for units with animations
        if asset_type == "units":
            results.extend(self._validate_unit_animations(type_dir, rules))

        return results

    def _validate_individual_asset(
        self, file_path: Path, rules: Dict[str, Any], asset_type: str
    ) -> AssetValidationResult:
        """Validate an individual asset file."""
        result = AssetValidationResult(str(file_path))

        # Check file extension
        if file_path.suffix.lower() not in rules["allowed_extensions"]:
            result.add_error(f"Invalid file extension: {file_path.suffix}. Expected: {rules['allowed_extensions']}")

        # Check file size
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > rules["max_file_size_mb"]:
                result.add_error(f"File too large: {file_size_mb:.2f}MB > {rules['max_file_size_mb']}MB")
        except OSError as e:
            result.add_error(f"Cannot access file: {e}")
            return result

        # Check naming pattern
        import re

        if "naming_pattern" in rules:
            if not re.match(rules["naming_pattern"], file_path.name):
                result.add_warning(f"File name doesn't match expected pattern: {rules['naming_pattern']}")

        # Validate image files
        if file_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            self._validate_image_file(file_path, rules, result)

        # Store file hash for duplicate detection
        try:
            file_hash = self._calculate_file_hash(file_path)
            result.metadata["hash"] = file_hash

            if file_hash in self.duplicate_hashes:
                self.duplicate_hashes[file_hash].append(str(file_path))
            else:
                self.duplicate_hashes[file_hash] = [str(file_path)]
        except Exception as e:
            result.add_warning(f"Could not calculate file hash: {e}")

        return result

    def _validate_image_file(self, file_path: Path, rules: Dict[str, Any], result: AssetValidationResult):
        """Validate image-specific properties."""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                result.metadata["resolution"] = (width, height)
                result.metadata["format"] = img.format
                result.metadata["mode"] = img.mode

                # Check resolution
                expected_resolution = rules.get("expected_resolution")
                if expected_resolution and (width, height) != expected_resolution:
                    result.add_error(
                        f"Invalid resolution: {width}x{height}. Expected: {expected_resolution[0]}x{expected_resolution[1]}"
                    )

                # Check if image has transparency (for PNGs)
                if img.format == "PNG" and img.mode in ("RGBA", "LA", "P"):
                    result.metadata["has_transparency"] = True
                else:
                    result.metadata["has_transparency"] = False

                # Warn about very large images
                if width * height > 1024 * 1024:  # 1 megapixel
                    result.add_warning(f"Very large image: {width}x{height} pixels")

        except Exception as e:
            result.add_error(f"Cannot open image file: {e}")

    def _validate_unit_animations(self, units_dir: Path, rules: Dict[str, Any]) -> List[AssetValidationResult]:
        """Validate unit animation completeness."""
        results = []
        animation_frames = rules.get("animation_frames", {})

        for unit_dir in units_dir.iterdir():
            if unit_dir.is_dir():
                result = AssetValidationResult(str(unit_dir))

                for anim_name, expected_frames in animation_frames.items():
                    anim_dir = unit_dir / anim_name
                    if not anim_dir.exists():
                        result.add_error(f"Missing animation directory: {anim_name}")
                        continue

                    # Count frames
                    frame_files = [f for f in anim_dir.iterdir() if f.suffix.lower() == ".png"]
                    if len(frame_files) != expected_frames:
                        result.add_error(
                            f"Animation {anim_name} has {len(frame_files)} frames, expected {expected_frames}"
                        )

                    # Check frame naming consistency
                    expected_names = [f"frame_{i:02d}.png" for i in range(expected_frames)]
                    actual_names = [f.name for f in sorted(frame_files)]

                    for expected_name in expected_names:
                        if expected_name not in actual_names:
                            result.add_warning(f"Missing expected frame: {anim_name}/{expected_name}")

                if result.errors or result.warnings:
                    results.append(result)

        return results

    def _check_for_duplicates(self, all_results: Dict[str, List[AssetValidationResult]]):
        """Check for duplicate files across all assets."""
        duplicates_found = []

        for file_hash, file_paths in self.duplicate_hashes.items():
            if len(file_paths) > 1:
                duplicates_found.append({"hash": file_hash, "files": file_paths, "count": len(file_paths)})

                # Add warnings to affected results
                for asset_type, results in all_results.items():
                    for result in results:
                        if result.asset_path in file_paths:
                            other_files = [f for f in file_paths if f != result.asset_path]
                            result.add_warning(f"Duplicate file detected. Also found at: {', '.join(other_files[:2])}")

        if self.logger and duplicates_found:
            self.logger.log_event(
                "asset_duplicates_found",
                {
                    "duplicate_groups": len(duplicates_found),
                    "total_duplicates": sum(d["count"] for d in duplicates_found),
                },
            )

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _generate_validation_report(self, all_results: Dict[str, List[AssetValidationResult]]):
        """Generate comprehensive validation report."""
        total_assets = sum(len(results) for results in all_results.values())
        total_errors = sum(sum(len(r.errors) for r in results) for results in all_results.values())
        total_warnings = sum(sum(len(r.warnings) for r in results) for results in all_results.values())
        valid_assets = sum(sum(1 for r in results if r.is_valid) for results in all_results.values())

        print("\n" + "=" * 60)
        print("🎨 COMPREHENSIVE ASSET VALIDATION REPORT")
        print("=" * 60)

        print(f"📊 Summary:")
        print(f"  ✅ Total Assets Checked: {total_assets}")
        print(f"  ✅ Valid Assets: {valid_assets}")
        print(f"  ❌ Assets with Errors: {total_assets - valid_assets}")
        print(f"  ⚠️  Total Warnings: {total_warnings}")
        print(f"  🚫 Total Errors: {total_errors}")

        if total_assets > 0:
            success_rate = (valid_assets / total_assets) * 100
            print(f"  📈 Success Rate: {success_rate:.1f}%")

        # Report by asset type
        for asset_type, results in all_results.items():
            if not results:
                continue

            type_errors = sum(len(r.errors) for r in results)
            type_warnings = sum(len(r.warnings) for r in results)
            type_valid = sum(1 for r in results if r.is_valid)

            print(f"\n🎨 {asset_type.title()} Assets:")
            print(f"  📁 Files: {len(results)}")
            print(f"  ✅ Valid: {type_valid}")
            print(f"  ❌ Errors: {type_errors}")
            print(f"  ⚠️  Warnings: {type_warnings}")

            # Show most common errors
            error_types = {}
            for result in results:
                for error in result.errors:
                    error_key = error.split(":")[0] if ":" in error else error
                    error_types[error_key] = error_types.get(error_key, 0) + 1

            if error_types:
                print(f"  🔍 Common Issues:")
                for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f"    - {error_type}: {count} occurrences")

        # Duplicate files report
        duplicate_groups = sum(1 for paths in self.duplicate_hashes.values() if len(paths) > 1)
        if duplicate_groups > 0:
            print(f"\n🔍 Duplicate Files:")
            print(f"  📁 Duplicate Groups: {duplicate_groups}")

            # Show a few examples
            shown = 0
            for file_hash, file_paths in self.duplicate_hashes.items():
                if len(file_paths) > 1 and shown < 3:
                    print(f"  🔗 {len(file_paths)} copies of:")
                    for path in file_paths[:2]:
                        print(f"    - {path}")
                    if len(file_paths) > 2:
                        print(f"    - ... and {len(file_paths) - 2} more")
                    shown += 1

        print("\n" + "=" * 60)

        # Log report
        if self.logger:
            self.logger.log_event(
                "asset_validation_complete",
                {
                    "total_assets": total_assets,
                    "valid_assets": valid_assets,
                    "total_errors": total_errors,
                    "total_warnings": total_warnings,
                    "success_rate": (valid_assets / total_assets * 100) if total_assets > 0 else 0,
                    "duplicate_groups": duplicate_groups,
                },
            )

    def validate_scenario_assets(self, scenario_file: Path) -> List[AssetValidationResult]:
        """Validate assets referenced in a scenario file."""
        results = []

        if not scenario_file.exists():
            result = AssetValidationResult(str(scenario_file))
            result.add_error(f"Scenario file not found: {scenario_file}")
            return [result]

        try:
            import yaml

            with open(scenario_file, "r") as f:
                scenario_data = yaml.safe_load(f)

            # Check assets referenced in scenario
            referenced_assets = set()

            # Extract enemy types
            for step in scenario_data.get("steps", []):
                for enemy in step.get("enemies", []):
                    enemy_type = enemy.get("type", "")
                    if enemy_type:
                        referenced_assets.add(f"units/{enemy_type}")

            # Check if referenced assets exist
            for asset_ref in referenced_assets:
                asset_path = self.asset_dir / asset_ref
                result = AssetValidationResult(str(asset_path))

                if not asset_path.exists():
                    result.add_error(f"Referenced asset not found: {asset_ref}")
                else:
                    result.metadata["referenced_in_scenario"] = True

                results.append(result)

        except Exception as e:
            result = AssetValidationResult(str(scenario_file))
            result.add_error(f"Error parsing scenario file: {e}")
            results.append(result)

        return results

    def generate_asset_manifest(self, output_file: Path = None) -> Dict[str, Any]:
        """Generate asset manifest for the game."""
        manifest = {
            "version": "1.0",
            "generated_at": "2024-01-01",  # Could use actual timestamp
            "asset_types": {},
            "total_assets": 0,
            "validation_summary": {},
        }

        # Validate all assets first
        validation_results = self.validate_all_assets()

        for asset_type, results in validation_results.items():
            type_manifest = {"count": len(results), "valid_count": sum(1 for r in results if r.is_valid), "files": []}

            for result in results:
                if result.is_valid:
                    file_info = {"path": result.asset_path, "metadata": result.metadata}
                    type_manifest["files"].append(file_info)

            manifest["asset_types"][asset_type] = type_manifest
            manifest["total_assets"] += len(results)

        # Save manifest if output file specified
        if output_file:
            try:
                with open(output_file, "w") as f:
                    json.dump(manifest, f, indent=2)

                if self.logger:
                    self.logger.log_event(
                        "asset_manifest_generated",
                        {"output_file": str(output_file), "total_assets": manifest["total_assets"]},
                    )
            except Exception as e:
                if self.logger:
                    self.logger.log_event("asset_manifest_error", {"output_file": str(output_file), "error": str(e)})

        return manifest

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of last validation run."""
        if not self.validation_results:
            return {"status": "no_validation_run"}

        total_assets = sum(len(results) for results in self.validation_results.values())
        valid_assets = sum(sum(1 for r in results if r.is_valid) for results in self.validation_results.values())

        return {
            "total_assets": total_assets,
            "valid_assets": valid_assets,
            "success_rate": (valid_assets / total_assets * 100) if total_assets > 0 else 0,
            "asset_types": list(self.validation_results.keys()),
            "duplicate_groups": sum(1 for paths in self.duplicate_hashes.values() if len(paths) > 1),
        }


# Standalone validation functions for backward compatibility
def validate_assets(asset_dir: Path = None, logger=None) -> Dict[str, List[AssetValidationResult]]:
    """Standalone asset validation function."""
    validator = AssetValidator(asset_dir, logger)
    return validator.validate_all_assets()


def generate_asset_report(asset_dir: Path = None, output_file: Path = None) -> bool:
    """Generate comprehensive asset report."""
    try:
        validator = AssetValidator(asset_dir)
        manifest = validator.generate_asset_manifest(output_file)
        return True
    except Exception as e:
        print(f"Error generating asset report: {e}")
        return False
