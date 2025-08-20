"""
MVP Demo Scene - combines terrain, units, animations with visual QA.
Provides comprehensive testing of art assets in actual gameplay context.
"""

import pygame
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from game.terrain_validator import TerrainValidator, validate_terrain
from game.sprite_validator import SpriteValidator, validate_sprites
from game.animation_manager import AnimationManager, get_animation_manager
from game.asset_validator import AssetValidator

# @api
# @refactor
class MVPDemoScene:
    """MVP demo scene for comprehensive asset testing and visual QA."""
    
    def __init__(self, screen_size: Tuple[int, int] = (800, 600)):
        self.screen_size = screen_size
        self.tile_size = 32
        self.grid_width = screen_size[0] // self.tile_size
        self.grid_height = screen_size[1] // self.tile_size
        
        # Asset validators
        self.terrain_validator = TerrainValidator()
        self.sprite_validator = SpriteValidator()
        self.asset_validator = AssetValidator()
        self.animation_manager = get_animation_manager()
        
        # Demo state
        self.current_terrain_type = "grass"
        self.current_unit_type = "knight"
        self.current_animation = "idle"
        self.show_grid = True
        self.show_qa_info = True
        self.auto_cycle = False
        self.cycle_timer = 0
        
        # Loaded assets
        self.terrain_tiles = {}
        self.unit_sprites = {}
        self.animations = {}
        
        # QA tracking
        self.qa_issues = []
        self.screenshot_count = 0
        
    def initialize(self) -> bool:
        """Initialize the demo scene with asset loading and validation."""
        print("🎮 Initializing MVP Demo Scene...")
        
        # Run comprehensive asset validation
        print("🔍 Running asset validation...")
        terrain_results = self.terrain_validator.validate_all_terrain()
        sprite_results = self.sprite_validator.validate_all_sprites()
        asset_results = self.asset_validator.validate_all_assets()
        
        # Load valid assets
        self._load_terrain_tiles()
        self._load_unit_sprites()
        self._load_animations()
        
        # Generate QA report
        self._generate_qa_report(terrain_results, sprite_results, asset_results)
        
        print("✅ MVP Demo Scene initialized successfully!")
        return True
    
    def _load_terrain_tiles(self):
        """Load valid terrain tiles."""
        terrain_dir = Path("assets/terrain")
        if not terrain_dir.exists():
            print("⚠️  Terrain directory not found")
            return
        
        for terrain_type in ["grass", "stone", "water", "forest", "mountain", "desert", "dungeon", "castle"]:
            type_dir = terrain_dir / terrain_type
            if type_dir.exists():
                main_tile = type_dir / f"{terrain_type}.png"
                if main_tile.exists():
                    try:
                        tile_surface = pygame.image.load(str(main_tile))
                        self.terrain_tiles[terrain_type] = tile_surface
                        print(f"✅ Loaded terrain: {terrain_type}")
                    except Exception as e:
                        print(f"❌ Failed to load terrain {terrain_type}: {e}")
                        self.qa_issues.append(f"Terrain load error: {terrain_type} - {e}")
    
    def _load_unit_sprites(self):
        """Load valid unit sprites."""
        units_dir = Path("assets/units")
        if not units_dir.exists():
            print("⚠️  Units directory not found")
            return
        
        for unit_type in ["knight", "mage", "archer", "goblin", "orc"]:
            unit_dir = units_dir / unit_type
            if unit_dir.exists():
                idle_sheet = unit_dir / "idle.png"
                if idle_sheet.exists():
                    try:
                        sprite_surface = pygame.image.load(str(idle_sheet))
                        self.unit_sprites[unit_type] = sprite_surface
                        print(f"✅ Loaded unit: {unit_type}")
                    except Exception as e:
                        print(f"❌ Failed to load unit {unit_type}: {e}")
                        self.qa_issues.append(f"Unit load error: {unit_type} - {e}")
    
    def _load_animations(self):
        """Load and validate animations."""
        units_dir = Path("assets/units")
        if not units_dir.exists():
            return
        
        for unit_type in ["knight", "mage", "archer"]:
            unit_dir = units_dir / unit_type
            if unit_dir.exists():
                # Load all animations for this unit
                for anim_file in unit_dir.glob("*.png"):
                    anim_name = f"{unit_type}_{anim_file.stem}"
                    success = self.animation_manager.load_animation(anim_name, anim_file)
                    if success:
                        print(f"✅ Loaded animation: {anim_name}")
                    else:
                        print(f"❌ Failed to load animation: {anim_name}")
                        self.qa_issues.append(f"Animation load error: {anim_name}")
    
    def _generate_qa_report(self, terrain_results, sprite_results, asset_results):
        """Generate comprehensive QA report."""
        print("\n" + "="*60)
        print("📊 MVP DEMO QA REPORT")
        print("="*60)
        
        # Terrain summary
        terrain_summary = self.terrain_validator.get_validation_summary()
        print(f"🌍 Terrain Assets:")
        print(f"  📁 Types: {terrain_summary.get('terrain_types', 0)}")
        print(f"  ✅ Valid: {terrain_summary.get('valid_files', 0)}")
        print(f"  📈 Success: {terrain_summary.get('success_rate', 0):.1f}%")
        
        # Sprite summary
        sprite_summary = self.sprite_validator.get_validation_summary()
        print(f"🎭 Sprite Assets:")
        print(f"  📁 Units: {sprite_summary.get('unit_types', 0)}")
        print(f"  ✅ Valid: {sprite_summary.get('valid_sheets', 0)}")
        print(f"  📈 Success: {sprite_summary.get('success_rate', 0):.1f}%")
        
        # Animation summary
        anim_qa = self.animation_manager.get_qa_report()
        print(f"🎬 Animation Assets:")
        print(f"  📁 Total: {anim_qa['summary'].get('total_animations', 0)}")
        print(f"  ✅ Valid: {anim_qa['summary'].get('valid_animations', 0)}")
        print(f"  📈 Success: {anim_qa['summary'].get('success_rate', 0):.1f}%")
        
        # Overall assessment
        total_assets = (terrain_summary.get('total_files', 0) + 
                       sprite_summary.get('total_sheets', 0) + 
                       anim_qa['summary'].get('total_animations', 0))
        
        valid_assets = (terrain_summary.get('valid_files', 0) + 
                       sprite_summary.get('valid_sheets', 0) + 
                       anim_qa['summary'].get('valid_animations', 0))
        
        overall_success = (valid_assets / total_assets * 100) if total_assets > 0 else 0
        
        print(f"\n📊 Overall Assessment:")
        print(f"  📁 Total Assets: {total_assets}")
        print(f"  ✅ Valid Assets: {valid_assets}")
        print(f"  📈 Success Rate: {overall_success:.1f}%")
        
        if self.qa_issues:
            print(f"\n⚠️  QA Issues Found:")
            for issue in self.qa_issues[:5]:  # Show first 5 issues
                print(f"  - {issue}")
            if len(self.qa_issues) > 5:
                print(f"  ... and {len(self.qa_issues) - 5} more issues")
        
        print("="*60)
    
    def run_demo(self):
        """Run the MVP demo scene."""
        pygame.init()
        screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Starter Town Tactics - MVP Demo Scene")
        clock = pygame.time.Clock()
        
        # Initialize demo
        if not self.initialize():
            print("❌ Failed to initialize MVP demo scene")
            return
        
        print("\n🎮 MVP Demo Scene Controls:")
        print("  - Arrow Keys: Navigate terrain/unit selection")
        print("  - Space: Toggle auto-cycle")
        print("  - G: Toggle grid")
        print("  - Q: Toggle QA info")
        print("  - S: Take screenshot")
        print("  - ESC: Exit")
        
        running = True
        while running:
            dt = clock.tick(60)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event.key)
            
            # Update
            self._update(dt)
            
            # Render
            self._render(screen)
            
            pygame.display.flip()
        
        pygame.quit()
    
    def _handle_keydown(self, key):
        """Handle keyboard input."""
        if key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif key == pygame.K_SPACE:
            self.auto_cycle = not self.auto_cycle
            print(f"🔄 Auto-cycle: {'ON' if self.auto_cycle else 'OFF'}")
        elif key == pygame.K_g:
            self.show_grid = not self.show_grid
            print(f"📐 Grid: {'ON' if self.show_grid else 'OFF'}")
        elif key == pygame.K_q:
            self.show_qa_info = not self.show_qa_info
            print(f"📊 QA Info: {'ON' if self.show_qa_info else 'OFF'}")
        elif key == pygame.K_s:
            self._take_screenshot()
        elif key == pygame.K_UP:
            self._cycle_terrain(1)
        elif key == pygame.K_DOWN:
            self._cycle_terrain(-1)
        elif key == pygame.K_LEFT:
            self._cycle_unit(-1)
        elif key == pygame.K_RIGHT:
            self._cycle_unit(1)
    
    def _cycle_terrain(self, direction: int):
        """Cycle through terrain types."""
        terrain_types = list(self.terrain_tiles.keys())
        if terrain_types:
            current_index = terrain_types.index(self.current_terrain_type)
            new_index = (current_index + direction) % len(terrain_types)
            self.current_terrain_type = terrain_types[new_index]
            print(f"🌍 Terrain: {self.current_terrain_type}")
    
    def _cycle_unit(self, direction: int):
        """Cycle through unit types."""
        unit_types = list(self.unit_sprites.keys())
        if unit_types:
            current_index = unit_types.index(self.current_unit_type)
            new_index = (current_index + direction) % len(unit_types)
            self.current_unit_type = unit_types[new_index]
            print(f"🎭 Unit: {self.current_unit_type}")
    
    def _update(self, dt: int):
        """Update demo state."""
        # Update animations
        self.animation_manager.update_animations(dt)
        
        # Auto-cycle
        if self.auto_cycle:
            self.cycle_timer += dt
            if self.cycle_timer > 2000:  # 2 seconds
                self.cycle_timer = 0
                self._cycle_unit(1)
    
    def _render(self, screen: pygame.Surface):
        """Render the demo scene."""
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Render terrain grid
        self._render_terrain_grid(screen)
        
        # Render units
        self._render_units(screen)
        
        # Render grid overlay
        if self.show_grid:
            self._render_grid_overlay(screen)
        
        # Render QA info
        if self.show_qa_info:
            self._render_qa_info(screen)
    
    def _render_terrain_grid(self, screen: pygame.Surface):
        """Render terrain tiles in a grid."""
        if self.current_terrain_type not in self.terrain_tiles:
            return
        
        tile_surface = self.terrain_tiles[self.current_terrain_type]
        
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                pos = (x * self.tile_size, y * self.tile_size)
                screen.blit(tile_surface, pos)
    
    def _render_units(self, screen: pygame.Surface):
        """Render units with animations."""
        # Render a few units in different positions
        unit_positions = [
            (2, 2), (5, 3), (8, 4), (3, 6), (7, 7)
        ]
        
        for i, (grid_x, grid_y) in enumerate(unit_positions):
            if i < len(self.unit_sprites):
                unit_type = list(self.unit_sprites.keys())[i]
                sprite_surface = self.unit_sprites[unit_type]
                
                # Calculate screen position
                screen_x = grid_x * self.tile_size
                screen_y = grid_y * self.tile_size
                
                # Render unit sprite
                screen.blit(sprite_surface, (screen_x, screen_y))
                
                # Try to render animation if available
                anim_name = f"{unit_type}_idle"
                if self.animation_manager.get_animation(anim_name):
                    self.animation_manager.render_animation(screen, anim_name, (screen_x, screen_y))
    
    def _render_grid_overlay(self, screen: pygame.Surface):
        """Render grid overlay."""
        for x in range(0, self.screen_size[0], self.tile_size):
            pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, self.screen_size[1]))
        
        for y in range(0, self.screen_size[1], self.tile_size):
            pygame.draw.line(screen, (100, 100, 100), (0, y), (self.screen_size[0], y))
    
    def _render_qa_info(self, screen: pygame.Surface):
        """Render QA information overlay."""
        font = pygame.font.Font(None, 24)
        
        # Current assets
        info_lines = [
            f"Terrain: {self.current_terrain_type}",
            f"Unit: {self.current_unit_type}",
            f"Animation: {self.current_animation}",
            f"Grid: {'ON' if self.show_grid else 'OFF'}",
            f"Auto-cycle: {'ON' if self.auto_cycle else 'OFF'}",
            f"QA Issues: {len(self.qa_issues)}"
        ]
        
        y_offset = 10
        for line in info_lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        # Asset counts
        asset_info = [
            f"Terrain Tiles: {len(self.terrain_tiles)}",
            f"Unit Sprites: {len(self.unit_sprites)}",
            f"Animations: {len(self.animation_manager.animations)}"
        ]
        
        y_offset = 160
        for line in asset_info:
            text_surface = font.render(line, True, (200, 200, 200))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 20
    
    def _take_screenshot(self):
        """Take a screenshot for QA purposes."""
        try:
            screenshot_dir = Path("qa_reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            self.screenshot_count += 1
            filename = f"mvp_demo_{self.screenshot_count:03d}.png"
            filepath = screenshot_dir / filename
            
            # Take screenshot
            pygame.image.save(pygame.display.get_surface(), str(filepath))
            print(f"📸 Screenshot saved: {filepath}")
            
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")

def run_mvp_demo():
    """Run the MVP demo scene."""
    demo = MVPDemoScene()
    demo.run_demo()

if __name__ == "__main__":
    run_mvp_demo()
