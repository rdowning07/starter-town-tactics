#!/usr/bin/env python3
"""
Check for Empty Assets

This script scans the assets directory to identify empty folders
and missing assets that need attention.
"""

import os
from pathlib import Path
from typing import Dict, List


def check_directory_contents(directory: Path) -> Dict:
    """Check the contents of a directory and return statistics."""

    if not directory.exists():
        return {"exists": False, "files": 0, "dirs": 0, "empty": True}

    files = []
    dirs = []

    try:
        for item in directory.iterdir():
            if item.is_file():
                files.append(item)
            elif item.is_dir():
                dirs.append(item)
    except PermissionError:
        return {"exists": True, "files": 0, "dirs": 0, "empty": True, "error": "Permission denied"}

    return {
        "exists": True,
        "files": len(files),
        "dirs": len(dirs),
        "empty": len(files) == 0 and len(dirs) == 0,
        "file_list": [f.name for f in files],
        "dir_list": [d.name for d in dirs],
    }


def scan_assets_directory(base_path: str = "assets") -> Dict:
    """Scan the entire assets directory structure."""

    base_dir = Path(base_path)
    if not base_dir.exists():
        print(f"❌ Assets directory not found: {base_path}")
        return {}

    results = {"empty_dirs": [], "missing_metadata": [], "units_without_animations": [], "summary": {}}

    print(f"🔍 Scanning assets directory: {base_path}")
    print("=" * 50)

    # Scan main categories
    for category in ["units", "tiles", "effects", "ui"]:
        category_path = base_dir / category
        category_info = check_directory_contents(category_path)

        print(f"\n📁 {category.upper()}:")
        if category_info["exists"]:
            print(f"  📊 Files: {category_info['files']}, Directories: {category_info['dirs']}")

            if category_info["empty"]:
                results["empty_dirs"].append(str(category_path))
                print(f"  ⚠️  EMPTY DIRECTORY")
            else:
                print(f"  ✅ Has content")

                # Special handling for units
                if category == "units":
                    scan_units_directory(category_path, results)
        else:
            print(f"  ❌ Directory not found")
            results["empty_dirs"].append(str(category_path))

    return results


def scan_units_directory(units_path: Path, results: Dict) -> None:
    """Scan the units directory for animation metadata and content."""

    print(f"\n  🎬 Scanning units...")

    for unit_dir in units_path.iterdir():
        if not unit_dir.is_dir():
            continue

        unit_name = unit_dir.name
        unit_info = check_directory_contents(unit_dir)

        if unit_info["empty"]:
            results["empty_dirs"].append(str(unit_dir))
            print(f"    ⚠️  {unit_name}: EMPTY")
            continue

        # Check for animation metadata
        metadata_file = unit_dir / "animation_metadata.json"
        if not metadata_file.exists():
            results["missing_metadata"].append(unit_name)
            print(f"    ⚠️  {unit_name}: No animation metadata")
        else:
            print(f"    ✅ {unit_name}: Has metadata")

        # Check for animation directories
        animation_dirs = ["idle", "walk", "attack"]
        missing_anims = []

        for anim_dir in animation_dirs:
            anim_path = unit_dir / anim_dir
            if anim_path.exists():
                anim_info = check_directory_contents(anim_path)
                if anim_info["empty"]:
                    missing_anims.append(anim_dir)
            else:
                missing_anims.append(anim_dir)

        if missing_anims:
            results["units_without_animations"].append({"unit": unit_name, "missing": missing_anims})
            print(f"    ⚠️  {unit_name}: Missing animations: {missing_anims}")
        else:
            print(f"    ✅ {unit_name}: Complete animations")


def print_summary(results: Dict) -> None:
    """Print a summary of the findings."""

    print("\n" + "=" * 50)
    print("📋 ASSETS SCAN SUMMARY")
    print("=" * 50)

    # Empty directories
    if results["empty_dirs"]:
        print(f"\n⚠️  EMPTY DIRECTORIES ({len(results['empty_dirs'])}):")
        for empty_dir in results["empty_dirs"]:
            print(f"  - {empty_dir}")
    else:
        print(f"\n✅ No empty directories found")

    # Missing metadata
    if results["missing_metadata"]:
        print(f"\n⚠️  UNITS WITHOUT METADATA ({len(results['missing_metadata'])}):")
        for unit in results["missing_metadata"]:
            print(f"  - {unit}")
    else:
        print(f"\n✅ All units have metadata")

    # Units without animations
    if results["units_without_animations"]:
        print(f"\n⚠️  UNITS WITH INCOMPLETE ANIMATIONS ({len(results['units_without_animations'])}):")
        for unit_info in results["units_without_animations"]:
            print(f"  - {unit_info['unit']}: Missing {unit_info['missing']}")
    else:
        print(f"\n✅ All units have complete animations")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")

    if results["empty_dirs"] or results["missing_metadata"] or results["units_without_animations"]:
        print(f"  1. Run 'make setup-animations' to standardize animation structure")
        print(f"  2. Run 'make integrate-sprite-sheet' to add new sprite sheets")
        print(f"  3. Run 'make test-animations' to validate all animations")
    else:
        print(f"  🎉 All assets are properly organized!")
        print(f"  Ready for Phase 4 development!")


def main():
    """Main function."""

    print("🔍 Assets Directory Scanner")
    print("=" * 30)

    results = scan_assets_directory()
    print_summary(results)

    # Return appropriate exit code
    total_issues = (
        len(results["empty_dirs"]) + len(results["missing_metadata"]) + len(results["units_without_animations"])
    )

    if total_issues > 0:
        print(f"\n⚠️  Found {total_issues} issues that need attention")
        return 1
    else:
        print(f"\n✅ All assets are properly organized!")
        return 0


if __name__ == "__main__":
    exit(main())
