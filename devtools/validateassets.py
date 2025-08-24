
# @api
import json
import os
import sys
from pathlib import Path
from typing import Dict

import pygame
import yaml

def load_asset_manifest(path: str) -> dict:
    """Load asset manifest from YAML file."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def validate_image_asset(file_path: str) -> Dict:
    """Validate image asset and return metadata."""
    result: Dict = {
        "path": file_path,
        "exists": False,
        "is_stub": False,
        "width": 0,
        "height": 0,
        "format": "unknown",
        "size_bytes": 0,
        "errors": []
    }

    if not os.path.exists(file_path):
        result["errors"].append("File does not exist")
        return result

    result["exists"] = True
    result["size_bytes"] = os.path.getsize(file_path)

    # Check if it's a stub (very small file)
    if result["size_bytes"] < 100:
        result["is_stub"] = True
        result["errors"].append("File is too small (likely a stub)")
        return result

    # Try to load with pygame to validate
    try:
        pygame.init()
        img = pygame.image.load(file_path)
        result["width"] = img.get_width()
        result["height"] = img.get_height()
        result["format"] = "valid_image"

        # Additional validation
        if result["width"] == 0 or result["height"] == 0:
            result["errors"].append("Image has zero dimensions")
        if result["width"] > 2048 or result["height"] > 2048:
            result["errors"].append("Image dimensions too large")

    except (pygame.error, OSError, ValueError) as e:
        result["errors"].append(f"Failed to load image: {e}")
        result["format"] = "invalid"

    return result

def validate_audio_asset(file_path: str) -> Dict:
    """Validate audio asset and return metadata."""
    result: Dict = {
        "path": file_path,
        "exists": False,
        "is_stub": False,
        "duration": 0.0,
        "format": "unknown",
        "size_bytes": 0,
        "errors": []
    }

    if not os.path.exists(file_path):
        result["errors"].append("File does not exist")
        return result

    result["exists"] = True
    result["size_bytes"] = os.path.getsize(file_path)

    # Check if it's a stub (very small file)
    if result["size_bytes"] < 100:
        result["is_stub"] = True
        result["errors"].append("File is too small (likely a stub)")
        return result

    # Check WAV header
    try:
        with open(file_path, 'rb') as f:
            header = f.read(44)  # WAV header size

            if len(header) < 44:
                result["errors"].append("File too short for WAV header")
                return result

            # Check RIFF header
            if header[:4] != b'RIFF':
                result["errors"].append("Not a valid WAV file (missing RIFF)")
                return result

            if header[8:12] != b'WAVE':
                result["errors"].append("Not a valid WAV file (missing WAVE)")
                return result

            # Check data section
            data_size = int.from_bytes(header[40:44], 'little')
            if data_size == 0:
                result["is_stub"] = True
                result["errors"].append("WAV file has no audio data (silent stub)")

            result["format"] = "wav"
            result["duration"] = data_size / 44100.0  # Assuming 44.1kHz

    except (OSError, ValueError) as e:
        result["errors"].append(f"Failed to validate audio: {e}")
        result["format"] = "invalid"

    return result

def scan_assets_directory(root_dir: str = "assets") -> Dict:
    """Scan assets directory and create comprehensive manifest."""
    asset_manifest: Dict = {
        "ui": {},
        "sfx": {},
        "unit_sprites": {},
        "terrain": {},
        "effects": {},
        "validation": {
            "total_files": 0,
            "stubs": 0,
            "valid": 0,
            "errors": 0
        }
    }

    root_path = Path(root_dir)
    if not root_path.exists():
        return asset_manifest

    # Scan for images
    for img_path in root_path.rglob("*.png"):
        rel_path = str(img_path.relative_to(root_path))

        # Categorize based on path
        path_mapping = {
            "ui": ("ui", img_path.stem),
            "units": ("unit_sprites", f"{img_path.parent.name}_{img_path.stem}"),
            "tiles": ("terrain", f"{img_path.parent.name}_{img_path.stem}"),
            "effects": ("effects", f"{img_path.parent.name}_{img_path.stem}")
        }

        category, name = "ui", img_path.stem  # Default
        for path_key, (cat, name_val) in path_mapping.items():
            if path_key in rel_path:
                category, name = cat, name_val
                break

        # Validate image
        validation = validate_image_asset(str(img_path))
        asset_manifest[category][name] = {
            "path": rel_path,
            "placeholder": validation["is_stub"],
            "validation": validation
        }

        asset_manifest["validation"]["total_files"] += 1
        if validation["is_stub"]:
            asset_manifest["validation"]["stubs"] += 1
        elif validation["errors"]:
            asset_manifest["validation"]["errors"] += 1
        else:
            asset_manifest["validation"]["valid"] += 1

    # Scan for audio
    for audio_path in root_path.rglob("*.wav"):
        rel_path = str(audio_path.relative_to(root_path))
        name = audio_path.stem

        validation = validate_audio_asset(str(audio_path))
        asset_manifest["sfx"][name] = {
            "path": rel_path,
            "placeholder": validation["is_stub"],
            "validation": validation
        }

        asset_manifest["validation"]["total_files"] += 1
        if validation["is_stub"]:
            asset_manifest["validation"]["stubs"] += 1
        elif validation["errors"]:
            asset_manifest["validation"]["errors"] += 1
        else:
            asset_manifest["validation"]["valid"] += 1

    return asset_manifest

def generate_asset_report(asset_manifest: Dict) -> str:
    """Generate a human-readable asset report."""
    report = []
    report.append("=== ASSET VALIDATION REPORT ===")
    report.append(f"Total files: {asset_manifest['validation']['total_files']}")
    report.append(f"Valid assets: {asset_manifest['validation']['valid']}")
    report.append(f"Stubs/placeholders: {asset_manifest['validation']['stubs']}")
    report.append(f"Errors: {asset_manifest['validation']['errors']}")
    report.append("")

    for category in ["ui", "sfx", "unit_sprites", "terrain", "effects"]:
        if asset_manifest[category]:
            report.append(f"--- {category.upper()} ---")
            for name, data in asset_manifest[category].items():
                status = "✅" if not data["placeholder"] else "⚠️"
                report.append(f"{status} {name}: {data['path']}")
                if data["placeholder"]:
                    report.append("    └─ Placeholder (needs replacement)")
                elif data["validation"]["errors"]:
                    report.append(f"    └─ Errors: {', '.join(data['validation']['errors'])}")
            report.append("")

    return "\n".join(report)

def save_manifest(asset_manifest: Dict, output_path: str = "assets/asset_manifest.json"):
    """Save manifest to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(asset_manifest, f, indent=2)
    print(f"Manifest saved to: {output_path}")

if __name__ == "__main__":
    print("🔍 Scanning assets directory...")
    manifest = scan_assets_directory("assets")

    print("\n" + generate_asset_report(manifest))

    # Save manifest
    save_manifest(manifest)

    # Exit with error code if there are issues
    if manifest["validation"]["errors"] > 0:
        print(f"\n❌ Validation failed with {manifest['validation']['errors']} errors")
        sys.exit(1)
    elif manifest["validation"]["stubs"] > 0:
        print(f"\n⚠️  Found {manifest['validation']['stubs']} placeholder assets")
        print("   Consider replacing with real assets for production")
    else:
        print("\n✅ All assets validated successfully!")
