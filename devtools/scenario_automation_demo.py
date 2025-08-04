# devtools/scenario_animation_demo.py

import pygame
import time
import sys
import argparse
from devtools.scenario_loader import load_scenario
from game.sprite_manager import SpriteManager
from game.renderer import Renderer
from game.fx_manager import FXManager
from game.sound_manager import SoundManager
from game.game_state import GameState

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scenario Automation Demo')
    parser.add_argument('--scenario', type=str, help='Path to scenario YAML file')
    parser.add_argument('--auto', action='store_true', help='Run in auto mode')
    args = parser.parse_args()
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    sprite_manager = SpriteManager()
    fx_manager = FXManager()
    sound_manager = SoundManager()
    
    # Load scenario if specified, otherwise create a simple game state
    if args.scenario:
        try:
            print(f"🎬 Loading scenario: {args.scenario}")
            game_state = load_scenario(args.scenario, sprite_manager, fx_manager, sound_manager)
            print(f"✅ Scenario loaded: {game_state.name}")
        except Exception as e:
            print(f"❌ Failed to load scenario: {e}")
            game_state = GameState()
    else:
        game_state = GameState()
    
    renderer = Renderer(screen, sprite_manager)

    running = True
    tick = 0
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Play animations for all units (if any exist)
        if hasattr(game_state, 'units') and game_state.units:
            # Get units from the unit manager
            units_list = game_state.units.get_all_units()
            for unit_name, unit_data in units_list.items():
                # Create a simple unit object for animation
                class AnimationUnit:
                    def __init__(self, name, data):
                        self.name = name
                        self.x = data.get('x', 0)
                        self.y = data.get('y', 0)
                        self.current_animation = data.get('animation', 'idle')
                        self.animation_frame = 0
                        self.sprite_name = data.get('sprite', 'knight')
                        self.team = data.get('team', 'player')
                    
                    def update_animation(self):
                        # Simple animation update
                        self.animation_frame = (self.animation_frame + 1) % 4
                    
                    def get_current_sprite(self, sprite_manager):
                        """Get the current sprite for this unit."""
                        return sprite_manager.get_unit_sprite(self.sprite_name, self.current_animation, self.animation_frame)
                
                unit = AnimationUnit(unit_name, unit_data)
                unit.update_animation()
                
                # Render the unit
                try:
                    sprite = unit.get_current_sprite(sprite_manager)
                    if sprite:
                        # Convert position to screen coordinates (scale up for visibility)
                        screen_x = unit.x * 64 + 100  # 64 pixels per tile, offset by 100
                        screen_y = unit.y * 64 + 100
                        
                        # If sprite is a string path, load it
                        if isinstance(sprite, str):
                            try:
                                sprite_surface = pygame.image.load(sprite)
                                sprite_surface = pygame.transform.scale(sprite_surface, (64, 64))
                            except:
                                # Create a colored rectangle as fallback
                                sprite_surface = pygame.Surface((64, 64))
                                if unit.team == "player":
                                    sprite_surface.fill((0, 255, 0))  # Green for player
                                elif unit.team == "enemy":
                                    sprite_surface.fill((255, 0, 0))  # Red for enemy
                                else:
                                    sprite_surface.fill((128, 128, 128))  # Gray for neutral
                        else:
                            # Sprite is already a surface
                            sprite_surface = pygame.transform.scale(sprite, (64, 64))
                        
                        # Draw the unit
                        screen.blit(sprite_surface, (screen_x, screen_y))
                        
                        # Draw unit name
                        font = pygame.font.Font(None, 24)
                        name_text = font.render(unit.name, True, (255, 255, 255))
                        screen.blit(name_text, (screen_x, screen_y - 20))
                        
                        # Draw HP
                        hp_text = font.render(f"HP: {unit_data.get('hp', 10)}", True, (255, 255, 0))
                        screen.blit(hp_text, (screen_x, screen_y + 70))
                        
                except Exception as e:
                    print(f"⚠️  Error rendering unit {unit.name}: {e}")
                
                # Inside the unit animation loop
                if hasattr(unit, 'sprite_name') and hasattr(unit, 'current_animation'):
                    meta = sprite_manager.get_animation_metadata(unit.sprite_name).get(unit.current_animation, {})
                    frame = getattr(unit, 'animation_frame', 0)

                    if "fx_at" in meta and frame in meta["fx_at"]:
                        print(f"[FX] Triggered for {unit.name} at frame {frame}")
                        if unit.current_animation == "die":
                            fx_manager.trigger_fx("shake", (unit.x, unit.y))
                        elif unit.current_animation == "hurt":
                            fx_manager.trigger_fx("flash", (unit.x, unit.y))
                        else:
                            fx_manager.trigger_fx("spark", (unit.x, unit.y))

        # Draw UI information
        font = pygame.font.Font(None, 24)
        ui_lines = [
            f"Scenario: {game_state.name}",
            f"Description: {game_state.description}",
            f"Tick: {tick}",
            f"Units: {len(units_list) if 'units_list' in locals() else 0}",
            "",
            "Controls: ESC to quit"
        ]
        
        for i, line in enumerate(ui_lines):
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))

        fx_manager.update()
        fx_manager.draw_fx(screen)

        pygame.display.flip()
        clock.tick(12)
        tick += 1

    pygame.quit()


if __name__ == "__main__":
    main()
