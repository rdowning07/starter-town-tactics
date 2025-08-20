"""
Particle QA Scene - validates particle FX assets with full architecture integration.
Integrated with existing asset QA system and provides comprehensive particle validation.
"""

import pygame
import time
import os
from typing import Dict, List, Optional
from game.ui.asset_qa_scene import AssetQAScene

# @api
# @refactor
class ParticleQAScene:
    """Validates particle FX assets with comprehensive testing and reporting."""
    
    def __init__(self, screen: pygame.Surface, logger=None):
        self.screen = screen
        self.logger = logger
        self.missing_particles = []
        self.valid_particles = []
        self.particle_definitions = self._create_particle_definitions()
        
    def _create_particle_definitions(self) -> Dict[str, Dict]:
        """Define expected particle FX types and their properties."""
        return {
            "spark": {
                "frames": 8,
                "color": (255, 255, 0),
                "size": (4, 4),
                "description": "Spark particles for critical hits"
            },
            "fire": {
                "frames": 6,
                "color": (255, 100, 0),
                "size": (15, 15),
                "description": "Fire particles for fire spells"
            },
            "ice": {
                "frames": 5,
                "color": (100, 200, 255),
                "size": (12, 12),
                "description": "Ice particles for ice spells"
            },
            "combo": {
                "frames": 4,
                "color": (255, 255, 255),
                "size": (10, 10),
                "description": "Combo effect particles"
            },
            "explosion": {
                "frames": 8,
                "color": (255, 200, 0),
                "size": (20, 20),
                "description": "Explosion particles"
            },
            "magic": {
                "frames": 6,
                "color": (200, 100, 255),
                "size": (18, 18),
                "description": "Magic spell particles"
            },
            "damage": {
                "frames": 3,
                "color": (255, 0, 0),
                "size": (15, 15),
                "description": "Damage number particles"
            },
            "heal": {
                "frames": 3,
                "color": (0, 255, 0),
                "size": (15, 15),
                "description": "Heal number particles"
            },
            "critical": {
                "frames": 5,
                "color": (255, 255, 0),
                "size": (20, 20),
                "description": "Critical hit particles"
            }
        }
    
    def run_particle_qa(self, auto_cycle: bool = True, delay: float = 0.5):
        """Run comprehensive particle FX QA with visual feedback."""
        print("🔍 Starting Particle FX QA Scene...")
        
        # Test all particle types
        self._test_particle_assets()
        
        # Generate report
        self._generate_particle_qa_report()
        
        if auto_cycle:
            self._cycle_through_particles(delay)
        
        return {
            "missing": self.missing_particles,
            "valid": self.valid_particles,
            "total_expected": len(self.particle_definitions)
        }
    
    def _test_particle_assets(self):
        """Test all particle FX assets."""
        for particle_name, particle_info in self.particle_definitions.items():
            expected_frames = particle_info["frames"]
            missing_frames = []
            
            # Check each frame
            for frame_num in range(expected_frames):
                frame_path = f"assets/effects/particles/{particle_name}/frame_{frame_num:02d}.png"
                
                if os.path.exists(frame_path):
                    try:
                        # Test loading the image
                        img = pygame.image.load(frame_path)
                        expected_size = particle_info["size"]
                        
                        # Check if image size matches expected
                        if img.get_size() != expected_size:
                            missing_frames.append(f"frame_{frame_num:02d} (wrong size: {img.get_size()})")
                        else:
                            self.valid_particles.append(f"{particle_name}_frame_{frame_num:02d}")
                            
                            if self.logger:
                                self.logger.log_event("particle_frame_valid", {
                                    "particle": particle_name,
                                    "frame": frame_num,
                                    "path": frame_path,
                                    "size": img.get_size()
                                })
                    except Exception as e:
                        missing_frames.append(f"frame_{frame_num:02d} (load error: {e})")
                else:
                    missing_frames.append(f"frame_{frame_num:02d} (missing file)")
            
            # Record missing frames for this particle type
            if missing_frames:
                self.missing_particles.append({
                    "particle": particle_name,
                    "missing_frames": missing_frames,
                    "expected_frames": expected_frames,
                    "description": particle_info["description"]
                })
            else:
                if self.logger:
                    self.logger.log_event("particle_type_complete", {
                        "particle": particle_name,
                        "frames": expected_frames,
                        "description": particle_info["description"]
                    })
    
    def _generate_particle_qa_report(self):
        """Generate comprehensive particle QA report."""
        print("\n" + "="*60)
        print("🎆 PARTICLE FX QA REPORT")
        print("="*60)
        
        total_expected = len(self.particle_definitions)
        total_missing = len(self.missing_particles)
        total_valid = len(self.valid_particles)
        
        # Calculate coverage
        total_expected_frames = sum(info["frames"] for info in self.particle_definitions.values())
        coverage_percentage = (total_valid / total_expected_frames * 100) if total_expected_frames > 0 else 0
        
        print(f"📊 Summary:")
        print(f"  ✅ Valid Particle Frames: {total_valid}")
        print(f"  ❌ Missing Particle Types: {total_missing}")
        print(f"  🎯 Expected Particle Types: {total_expected}")
        print(f"  📈 Frame Coverage: {coverage_percentage:.1f}%")
        
        if self.missing_particles:
            print(f"\n❌ Missing Particle Assets:")
            for missing in self.missing_particles:
                print(f"  🎆 {missing['particle']}: {missing['description']}")
                print(f"     Expected {missing['expected_frames']} frames")
                print(f"     Missing: {', '.join(missing['missing_frames'][:3])}")
                if len(missing['missing_frames']) > 3:
                    print(f"     ... and {len(missing['missing_frames']) - 3} more")
                print()
        
        # Show complete particle types
        complete_particles = []
        for particle_name in self.particle_definitions.keys():
            if not any(missing['particle'] == particle_name for missing in self.missing_particles):
                complete_particles.append(particle_name)
        
        if complete_particles:
            print(f"✅ Complete Particle Types:")
            for particle in complete_particles:
                info = self.particle_definitions[particle]
                print(f"  🎆 {particle}: {info['description']} ({info['frames']} frames)")
        
        print("\n" + "="*60)
        
        # Log report
        if self.logger:
            self.logger.log_event("particle_qa_report", {
                "valid_frames": total_valid,
                "missing_types": total_missing,
                "expected_types": total_expected,
                "coverage_percentage": coverage_percentage,
                "missing_particles": self.missing_particles,
                "complete_particles": complete_particles
            })
    
    def _cycle_through_particles(self, delay: float):
        """Cycle through all valid particle assets for visual review."""
        print(f"\n🔄 Cycling through {len(self.valid_particles)} valid particle frames...")
        print("Press any key to stop cycling...")
        
        font = pygame.font.Font(None, 24)
        clock = pygame.time.Clock()
        
        for i, particle_frame in enumerate(self.valid_particles):
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Parse particle frame info
            parts = particle_frame.split('_')
            particle_name = parts[0]
            frame_num = int(parts[2])
            
            # Display particle info
            info = self.particle_definitions.get(particle_name, {})
            text_lines = [
                f"Particle {i+1}/{len(self.valid_particles)}: {particle_name}",
                f"Frame: {frame_num:02d}",
                f"Description: {info.get('description', 'Unknown')}",
                f"Expected Size: {info.get('size', 'Unknown')}",
                f"Color: {info.get('color', 'Unknown')}"
            ]
            
            y_offset = 10
            for line in text_lines:
                text_surf = font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surf, (10, y_offset))
                y_offset += 25
            
            # Try to display the particle frame
            try:
                frame_path = f"assets/effects/particles/{particle_name}/frame_{frame_num:02d}.png"
                if os.path.exists(frame_path):
                    img = pygame.image.load(frame_path)
                    
                    # Scale for display if needed
                    display_size = (100, 100)
                    if img.get_size() != display_size:
                        img = pygame.transform.scale(img, display_size)
                    
                    # Display in center
                    x = (self.screen.get_width() - display_size[0]) // 2
                    y = (self.screen.get_height() - display_size[1]) // 2
                    self.screen.blit(img, (x, y))
                    
                    # Draw border
                    pygame.draw.rect(self.screen, (255, 255, 255), 
                                   (x, y, display_size[0], display_size[1]), 2)
                else:
                    error_text = font.render("File not found", True, (255, 0, 0))
                    self.screen.blit(error_text, (300, 200))
            
            except Exception as e:
                error_text = font.render(f"Error loading: {e}", True, (255, 0, 0))
                self.screen.blit(error_text, (300, 200))
            
            pygame.display.flip()
            
            # Check for user input to stop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    return
            
            time.sleep(delay)
            clock.tick(60)
        
        print("✅ Particle cycling complete!")
        input("Press Enter to exit Particle QA Scene...")
    
    def get_particle_status(self) -> Dict:
        """Get comprehensive particle system status."""
        total_expected = len(self.particle_definitions)
        total_missing = len(self.missing_particles)
        total_valid = len(self.valid_particles)
        
        total_expected_frames = sum(info["frames"] for info in self.particle_definitions.values())
        coverage_percentage = (total_valid / total_expected_frames * 100) if total_expected_frames > 0 else 0
        
        return {
            "valid_frames": total_valid,
            "missing_types": total_missing,
            "expected_types": total_expected,
            "coverage_percentage": coverage_percentage,
            "missing_particles": self.missing_particles,
            "particle_definitions": self.particle_definitions
        }

def run_particle_qa_standalone(screen: pygame.Surface, auto_cycle: bool = True):
    """Standalone function to run particle QA (for backward compatibility)."""
    qa_scene = ParticleQAScene(screen)
    return qa_scene.run_particle_qa(auto_cycle)
