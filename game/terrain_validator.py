"""
Terrain Validator - validates terrain tiles with full architecture integration.
Integrated with existing AssetValidator and includes comprehensive validation and reporting.
"""

import pygame
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from game.asset_validator import AssetValidator, AssetValidationResult

# @api
# @refactor
class TerrainValidator:
    """Validates terrain tiles with comprehensive checking and reporting."""
    
    def __init__(self, asset_dir: Path = None, logger=None):
        self.asset_dir = asset_dir or Path("assets/terrain")
        self.logger = logger
        self.expected_tile_size = (32, 32)  # Standard terrain tile size
        self.validation_results = {}
        self.qa_report_dir = Path("qa_reports")
        self.qa_report_dir.mkdir(exist_ok=True)
        
        # Terrain type definitions
        self.terrain_types = {
            "grass": {"color": (34, 139, 34), "walkable": True, "defense": 0},
            "stone": {"color": (128, 128, 128), "walkable": True, "defense": 1},
            "water": {"color": (0, 191, 255), "walkable": False, "defense": 0},
            "forest": {"color": (34, 100, 34), "walkable": True, "defense": 2},
            "mountain": {"color": (139, 69, 19), "walkable": False, "defense": 3},
            "desert": {"color": (238, 203, 173), "walkable": True, "defense": 0},
            "dungeon": {"color": (64, 64, 64), "walkable": True, "defense": 1},
            "castle": {"color": (192, 192, 192), "walkable": True, "defense": 2}
        }
    
    def validate_all_terrain(self) -> Dict[str, List[AssetValidationResult]]:
        """Validate all terrain tiles in the asset directory."""
        results = {}
        
        if not self.asset_dir.exists():
            if self.logger:
                self.logger.log_event("terrain_validation_error", {
                    "error": f"Terrain directory not found: {self.asset_dir}"
                })
            return results
        
        # Validate each terrain type
        for terrain_type in self.terrain_types.keys():
            type_dir = self.asset_dir / terrain_type
            if type_dir.exists():
                type_results = self._validate_terrain_type(terrain_type, type_dir)
                results[terrain_type] = type_results
            else:
                # Missing terrain type directory
                result = AssetValidationResult(str(type_dir))
                result.add_error(f"Missing terrain type directory: {terrain_type}")
                results[terrain_type] = [result]
        
        # Generate comprehensive reports
        self._generate_terrain_report(results)
        self._generate_terrain_csv(results)
        
        return results
    
    def _validate_terrain_type(self, terrain_type: str, type_dir: Path) -> List[AssetValidationResult]:
        """Validate terrain tiles of a specific type."""
        results = []
        
        # Check for expected files
        expected_files = [
            f"{terrain_type}.png",
            f"{terrain_type}_edge.png",
            f"{terrain_type}_corner.png"
        ]
        
        for expected_file in expected_files:
            file_path = type_dir / expected_file
            result = AssetValidationResult(str(file_path))
            
            if file_path.exists():
                # Validate the file
                self._validate_terrain_file(file_path, terrain_type, result)
            else:
                result.add_warning(f"Expected terrain file missing: {expected_file}")
            
            results.append(result)
        
        # Check for additional files
        for file_path in type_dir.glob("*.png"):
            if file_path.name not in [f.name for f in type_dir.glob("*.png") if f.name in expected_files]:
                result = AssetValidationResult(str(file_path))
                result.add_warning(f"Unexpected terrain file: {file_path.name}")
                self._validate_terrain_file(file_path, terrain_type, result)
                results.append(result)
        
        return results
    
    def _validate_terrain_file(self, file_path: Path, terrain_type: str, result: AssetValidationResult):
        """Validate an individual terrain file."""
        try:
            # Load image
            img = pygame.image.load(str(file_path))
            width, height = img.get_size()
            result.metadata["resolution"] = (width, height)
            result.metadata["format"] = "PNG"
            result.metadata["terrain_type"] = terrain_type
            
            # Check size
            if (width, height) != self.expected_tile_size:
                result.add_error(f"Invalid tile size: {width}x{height}. Expected: {self.expected_tile_size[0]}x{self.expected_tile_size[1]}")
            
            # Check if image has transparency
            if img.get_alpha() is not None:
                result.metadata["has_transparency"] = True
            else:
                result.metadata["has_transparency"] = False
            
            # Analyze color distribution
            color_analysis = self._analyze_terrain_colors(img, terrain_type)
            result.metadata["color_analysis"] = color_analysis
            
            # Check for expected color characteristics
            expected_color = self.terrain_types[terrain_type]["color"]
            if not self._check_color_similarity(color_analysis["dominant_color"], expected_color):
                result.add_warning(f"Color doesn't match expected {terrain_type} color")
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 1.0:  # 1MB limit
                result.add_warning(f"Large file size: {file_size_mb:.2f}MB")
            
            result.metadata["file_size_mb"] = file_size_mb
            
        except Exception as e:
            result.add_error(f"Cannot load terrain file: {e}")
    
    def _analyze_terrain_colors(self, img: pygame.Surface, terrain_type: str) -> Dict[str, Any]:
        """Analyze color characteristics of terrain tile."""
        try:
            # Convert to array for analysis
            pixels = pygame.surfarray.array3d(img)
            
            # Calculate average color
            avg_color = pixels.mean(axis=(0, 1))
            
            # Find dominant color (simplified)
            dominant_color = tuple(int(c) for c in avg_color)
            
            # Calculate color variance
            color_variance = pixels.var(axis=(0, 1)).mean()
            
            return {
                "average_color": tuple(int(c) for c in avg_color),
                "dominant_color": dominant_color,
                "color_variance": float(color_variance),
                "expected_color": self.terrain_types[terrain_type]["color"]
            }
        except (NotImplementedError, ImportError):
            # Fallback: simple color analysis
            return {
                "average_color": (128, 128, 128),
                "dominant_color": (128, 128, 128),
                "color_variance": 0.0,
                "expected_color": self.terrain_types[terrain_type]["color"]
            }
    
    def _check_color_similarity(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], threshold: int = 50) -> bool:
        """Check if two colors are similar within threshold."""
        diff = sum(abs(c1 - c2) for c1, c2 in zip(color1, color2))
        return diff <= threshold * 3  # 3 channels
    
    def _generate_terrain_report(self, results: Dict[str, List[AssetValidationResult]]):
        """Generate comprehensive terrain validation report."""
        print("\n" + "="*60)
        print("🌍 TERRAIN VALIDATION REPORT")
        print("="*60)
        
        total_files = sum(len(type_results) for type_results in results.values())
        valid_files = sum(sum(1 for r in type_results if r.is_valid) for type_results in results.values())
        total_errors = sum(sum(len(r.errors) for r in type_results) for type_results in results.values())
        total_warnings = sum(sum(len(r.warnings) for r in type_results) for type_results in results.values())
        
        print(f"📊 Summary:")
        print(f"  🌍 Terrain Types: {len(results)}")
        print(f"  📁 Total Files: {total_files}")
        print(f"  ✅ Valid Files: {valid_files}")
        print(f"  ❌ Files with Errors: {total_files - valid_files}")
        print(f"  ⚠️  Total Warnings: {total_warnings}")
        print(f"  🚫 Total Errors: {total_errors}")
        
        if total_files > 0:
            success_rate = (valid_files / total_files) * 100
            print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        # Report by terrain type
        for terrain_type, type_results in results.items():
            if not type_results:
                continue
            
            type_errors = sum(len(r.errors) for r in type_results)
            type_warnings = sum(len(r.warnings) for r in type_results)
            type_valid = sum(1 for r in type_results if r.is_valid)
            
            print(f"\n🌍 {terrain_type.title()} Terrain:")
            print(f"  📁 Files: {len(type_results)}")
            print(f"  ✅ Valid: {type_valid}")
            print(f"  ❌ Errors: {type_errors}")
            print(f"  ⚠️  Warnings: {type_warnings}")
            
            # Show specific issues
            for result in type_results:
                if result.errors:
                    print(f"    ❌ {Path(result.asset_path).name}: {', '.join(result.errors)}")
                elif result.warnings:
                    print(f"    ⚠️  {Path(result.asset_path).name}: {', '.join(result.warnings)}")
        
        print("\n" + "="*60)
        
        # Log report
        if self.logger:
            self.logger.log_event("terrain_validation_complete", {
                "terrain_types": len(results),
                "total_files": total_files,
                "valid_files": valid_files,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "success_rate": (valid_files / total_files * 100) if total_files > 0 else 0
            })
    
    def _generate_terrain_csv(self, results: Dict[str, List[AssetValidationResult]]):
        """Generate CSV report for terrain validation."""
        csv_file = self.qa_report_dir / "terrain_report.csv"
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "terrain_type", "file_name", "file_path", "width", "height", 
                "valid", "has_transparency", "file_size_mb", "errors", "warnings"
            ])
            writer.writeheader()
            
            for terrain_type, type_results in results.items():
                for result in type_results:
                    file_path = Path(result.asset_path)
                    writer.writerow({
                        "terrain_type": terrain_type,
                        "file_name": file_path.name,
                        "file_path": str(file_path),
                        "width": result.metadata.get("resolution", (0, 0))[0],
                        "height": result.metadata.get("resolution", (0, 0))[1],
                        "valid": result.is_valid,
                        "has_transparency": result.metadata.get("has_transparency", False),
                        "file_size_mb": result.metadata.get("file_size_mb", 0),
                        "errors": "; ".join(result.errors),
                        "warnings": "; ".join(result.warnings)
                    })
        
        print(f"📊 CSV Report saved: {csv_file}")
    
    def get_terrain_manifest(self) -> Dict[str, Any]:
        """Generate terrain manifest for the game."""
        manifest = {
            "version": "1.0",
            "terrain_types": {},
            "total_tiles": 0,
            "validation_summary": {}
        }
        
        # Validate all terrain first
        validation_results = self.validate_all_terrain()
        
        for terrain_type, type_results in validation_results.items():
            type_manifest = {
                "count": len(type_results),
                "valid_count": sum(1 for r in type_results if r.is_valid),
                "tiles": []
            }
            
            for result in type_results:
                if result.is_valid:
                    tile_info = {
                        "file": Path(result.asset_path).name,
                        "path": result.asset_path,
                        "metadata": result.metadata
                    }
                    type_manifest["tiles"].append(tile_info)
            
            manifest["terrain_types"][terrain_type] = type_manifest
            manifest["total_tiles"] += len(type_results)
        
        # Save manifest
        manifest_file = self.qa_report_dir / "terrain_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"📋 Terrain manifest saved: {manifest_file}")
        return manifest
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of terrain validation."""
        if not self.validation_results:
            return {"status": "no_validation_run"}
        
        total_files = sum(len(results) for results in self.validation_results.values())
        valid_files = sum(sum(1 for r in results if r.is_valid) for results in self.validation_results.values())
        
        return {
            "terrain_types": len(self.validation_results),
            "total_files": total_files,
            "valid_files": valid_files,
            "success_rate": (valid_files / total_files * 100) if total_files > 0 else 0
        }

# Standalone validation function for backward compatibility
def validate_terrain(asset_dir: Path = None, logger=None) -> Dict[str, List[AssetValidationResult]]:
    """Standalone terrain validation function."""
    validator = TerrainValidator(asset_dir, logger)
    return validator.validate_all_terrain()

def generate_terrain_report(asset_dir: Path = None) -> bool:
    """Generate comprehensive terrain report."""
    try:
        validator = TerrainValidator(asset_dir)
        manifest = validator.get_terrain_manifest()
        return True
    except Exception as e:
        print(f"Error generating terrain report: {e}")
        return False
