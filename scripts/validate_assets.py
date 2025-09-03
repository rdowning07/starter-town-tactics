#!/usr/bin/env python3
"""
Comprehensive Asset Validation for Starter Town Tactics
Validates asset structure, files, and metadata consistency.
"""

import csv
from pathlib import Path
from typing import List

import yaml


class AssetValidator:
    """Comprehensive asset validation system."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.assets_dir = self.project_root / "assets"
        self.data_dir = self.project_root / "data"
        self.scripts_dir = self.project_root / "scripts"

        # Validation results
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks. Returns True if all passed."""
        print("🎨 Asset Validation for Starter Town Tactics")
        print("=" * 50)

        # Run all validation checks
        checks = [
            self.validate_directory_structure,
            self.validate_asset_tracker,
            self.validate_placeholder_files,
            self.validate_sprite_mapping,
            self.validate_tileset_mapping,
            self.generate_asset_report,
        ]

        all_passed = True
        for check in checks:
            try:
                if not check():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"Validation check failed: {e}")
                all_passed = False

        # Print results
        self._print_results()

        return all_passed

    def validate_directory_structure(self) -> bool:
        """Validate that all required asset directories exist."""
        required_dirs = [
            "assets/units",
            "assets/tiles/castle",
            "assets/tiles/desert",
            "assets/tiles/dungeon",
            "assets/tiles/house",
            "assets/tiles/interior",
            "assets/tiles/village",
            "assets/tiles/terrain",
            "assets/tiles/water",
            "assets/tiles/worldmap",
            "assets/ui/cursors",
            "assets/ui/icons",
            "assets/ui/panels",
            "assets/effects/particles",
            "assets/effects/summoning",
            "assets/effects/aura",
        ]

        missing_dirs = []
        for directory in required_dirs:
            if not (self.project_root / directory).exists():
                missing_dirs.append(directory)

        if missing_dirs:
            self.errors.append(f"Missing directories: {missing_dirs}")
            return False

        self.info.append("✅ All required directories exist!")
        return True

    def validate_asset_tracker(self) -> bool:
        """Validate the assets tracker CSV file."""
        tracker_path = self.data_dir / "assets_tracker.csv"

        if not tracker_path.exists():
            self.errors.append("Assets tracker not found")
            return False

        try:
            with open(tracker_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                entries = list(reader)

            if not entries:
                self.warnings.append("Assets tracker is empty")
                return True

            # Validate CSV structure
            required_fields = [
                "asset_path",
                "asset_type",
                "unit_type",
                "team_variant",
                "status",
                "license",
                "source",
                "notes",
            ]
            missing_fields = [field for field in required_fields if field not in entries[0].keys()]

            if missing_fields:
                self.errors.append(f"Assets tracker missing fields: {missing_fields}")
                return False

            # Check for duplicate entries
            paths = [entry["asset_path"] for entry in entries]
            duplicates = [path for path in set(paths) if paths.count(path) > 1]

            if duplicates:
                self.warnings.append(f"Duplicate asset paths: {duplicates}")

            self.info.append(f"✅ Assets tracker found with {len(entries)} entries")
            return True

        except Exception as e:
            self.errors.append(f"Failed to read assets tracker: {e}")
            return False

    def validate_placeholder_files(self) -> bool:
        """Check that key placeholder files exist."""
        placeholder_files = [
            "assets/tiles/castle/castle.png",
            "assets/tiles/desert/desert.png",
            "assets/tiles/dungeon/dungeon.png",
            "assets/tiles/house/house.png",
            "assets/tiles/interior/inside.png",
            "assets/tiles/village/outside.png",
            "assets/tiles/terrain/terrain.png",
            "assets/tiles/water/water.png",
            "assets/tiles/worldmap/world.png",
            "assets/effects/summoning/portal.png",
            "assets/effects/aura/buff.png",
        ]

        missing_files = []
        for file_path in placeholder_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            self.errors.append(f"Missing placeholder files: {missing_files}")
            return False

        self.info.append("✅ Key placeholder files exist!")
        return True

    def validate_sprite_mapping(self) -> bool:
        """Validate the sprite mapping master YAML."""
        mapping_path = self.project_root / "sprite_mapping_master.yaml"

        if not mapping_path.exists():
            self.warnings.append("Sprite mapping master not found")
            return True

        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                mapping = yaml.safe_load(f)

            if not mapping:
                self.warnings.append("Sprite mapping is empty")
                return True

            # Validate unit entries
            for unit_name, unit_data in mapping.items():
                if not isinstance(unit_data, dict):
                    self.errors.append(f"Invalid unit data for {unit_name}")
                    continue

                required_fields = ["sprite", "color", "tier"]
                missing_fields = [field for field in required_fields if field not in unit_data]

                if missing_fields:
                    self.errors.append(f"Unit {unit_name} missing fields: {missing_fields}")
                    continue

                # Check if sprite file exists
                sprite_path = unit_data["sprite"]
                if not (self.project_root / sprite_path).exists():
                    self.warnings.append(f"Sprite file not found: {sprite_path}")

            self.info.append(f"✅ Sprite mapping validated with {len(mapping)} units")
            return True

        except Exception as e:
            self.errors.append(f"Failed to validate sprite mapping: {e}")
            return False

    def validate_tileset_mapping(self) -> bool:
        """Validate the tileset mapping YAML."""
        mapping_path = self.data_dir / "tileset_mapping.yaml"

        if not mapping_path.exists():
            self.warnings.append("Tileset mapping not found")
            return True

        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or "tilesets" not in data:
                self.warnings.append("Tileset mapping is empty or invalid")
                return True

            tilesets = data["tilesets"]

            for tileset in tilesets:
                required_fields = ["file", "name", "tile_size"]
                missing_fields = [field for field in required_fields if field not in tileset]

                if missing_fields:
                    self.errors.append(f"Tileset {tileset.get('name', 'unknown')} missing fields: {missing_fields}")
                    continue

                # Check if tileset file exists
                file_path = tileset["file"]
                if not (self.project_root / file_path).exists():
                    self.warnings.append(f"Tileset file not found: {file_path}")

            self.info.append(f"✅ Tileset mapping validated with {len(tilesets)} tilesets")
            return True

        except Exception as e:
            self.errors.append(f"Failed to validate tileset mapping: {e}")
            return False

    def generate_asset_report(self) -> bool:
        """Generate a comprehensive asset report."""
        print("\n📊 Generating asset report...")

        # Count files by type
        counts = {"units": 0, "tiles": 0, "effects": 0, "ui": 0}

        # Count unit files
        units_dir = self.assets_dir / "units"
        if units_dir.exists():
            for unit_dir in units_dir.iterdir():
                if unit_dir.is_dir():
                    counts["units"] += len(list(unit_dir.glob("*.png")))

        # Count tile files
        tiles_dir = self.assets_dir / "tiles"
        if tiles_dir.exists():
            for tile_dir in tiles_dir.iterdir():
                if tile_dir.is_dir():
                    counts["tiles"] += len(list(tile_dir.glob("*.png")))

        # Count effect files
        effects_dir = self.assets_dir / "effects"
        if effects_dir.exists():
            for effect_dir in effects_dir.iterdir():
                if effect_dir.is_dir():
                    counts["effects"] += len(list(effect_dir.glob("*.png")))

        # Count UI files
        ui_dir = self.assets_dir / "ui"
        if ui_dir.exists():
            for ui_subdir in ui_dir.iterdir():
                if ui_subdir.is_dir():
                    counts["ui"] += len(list(ui_subdir.glob("*.png")))

        total_files = sum(counts.values())

        print("📈 Asset Counts:")
        for asset_type, count in counts.items():
            print(f"  - {asset_type.capitalize()}: {count} files")
        print(f"  - Total: {total_files} files")

        self.info.append(f"📊 Asset report generated: {total_files} total files")
        return True

    def _print_results(self):
        """Print validation results."""
        print("\n" + "=" * 50)

        if self.errors:
            print("❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.info:
            print("ℹ️  Info:")
            for info in self.info:
                print(f"  - {info}")

        if not self.errors and not self.warnings:
            print("✅ All asset validations passed!")
        elif not self.errors:
            print("✅ Asset validations passed with warnings!")
        else:
            print("❌ Asset validations failed!")

        print("=" * 50)


def main():
    """Main validation function."""
    import sys

    validator = AssetValidator()
    success = validator.validate_all()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
