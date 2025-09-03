"""
Enhanced UI Demo - demonstrates UI system with Week 6 features.
Shows proper architecture integration with Enemy AI, Scenario Management, and Asset Validation.
"""

from pathlib import Path

import pygame

from game.ai.enemy_ai import AIBehaviorType, EnemyAI
from game.asset_validator import AssetValidator, validate_assets
from game.audio.sound_manager import get_sound_manager, play_game_event_sound
from game.combo_system import ComboManager
from game.event_triggers import EventManager
from game.fx_manager import FXManager
from game.game_state import GameState
from game.game_win_loss import GameWinLoss
from game.scenario_manager import ScenarioManager
from game.status_effects import StatusEffectManager
from game.ui.asset_qa_scene import AssetQAScene, run_asset_qa_standalone
from game.ui.game_actions import GameActions
from game.ui.health_ui import HealthUI
from game.ui.input_handler import handle_keyboard_input, handle_mouse_input
from game.ui.particle_qa_scene import ParticleQAScene, run_particle_qa_standalone
from game.ui.status_ui import StatusUI
from game.ui.turn_ui import TurnUI
from game.ui.ui_renderer import UIRenderer
from game.ui.ui_state import UIState


def create_demo_game_state():
    """Create a demo game state with some units for testing."""
    game_state = GameState()
    game_state.name = "Week 6 UI Demo"
    game_state.description = "Demo for Week 6 UI system with enemy AI, scenario management, and asset validation"

    # Add some demo units with max_hp for health bars
    game_state.units.register_unit("player_1", "player", hp=20)
    game_state.units.register_unit("player_2", "player", hp=15)
    game_state.units.register_unit("enemy_1", "enemy", hp=18)
    game_state.units.register_unit("enemy_2", "enemy", hp=12)

    # Add units to turn controller
    game_state.turn_controller.add_unit("player_1")
    game_state.turn_controller.add_unit("player_2")
    game_state.turn_controller.add_unit("enemy_1")
    game_state.turn_controller.add_unit("enemy_2")

    return game_state


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Starter Town Tactics - Week 6 Enhanced UI Demo")
    clock = pygame.time.Clock()
    tile_size = 32

    # Run asset validation before starting demo
    print("🎨 Running Asset Validation...")
    asset_validator = AssetValidator(Path("assets"))
    validation_results = asset_validator.validate_all_assets()

    # Create enhanced UI components
    ui_state = UIState()
    ui_renderer = UIRenderer(screen, tile_size)
    game_actions = GameActions()
    turn_ui = TurnUI()
    health_ui = HealthUI()
    status_ui = StatusUI()
    win_loss = GameWinLoss()
    sound_manager = get_sound_manager()
    status_manager = StatusEffectManager()
    fx_manager = FXManager()
    combo_manager = ComboManager(status_manager, fx_manager)
    event_manager = EventManager(fx_manager)

    # Week 6 additions
    scenario_manager = ScenarioManager("assets/scenarios/demo.yaml", event_manager)
    enemy_ais = {}

    # Create demo game state
    game_state = create_demo_game_state()

    # Initialize scenario
    scenario_manager.start_scenario(game_state)

    # Create AI for existing enemies
    for unit_id, unit_data in game_state.units.units.items():
        if unit_data.get("team") == "enemy" and unit_data.get("alive", True):
            ai_behavior = AIBehaviorType.AGGRESSIVE
            enemy_ais[unit_id] = EnemyAI(unit_id, ai_behavior)

    print("🎮 Week 6 Enhanced UI Demo")
    print("Controls:")
    print("  - Click units to select")
    print("  - Click action menu buttons to show ranges")
    print("  - Click in range to move/attack")
    print("  - Press 'A' for Asset QA Scene")
    print("  - Press 'V' for Asset Validation Report")
    print("  - Press 'P' for Particle QA Scene")
    print("  - Press 'S' for Sound Report")
    print("  - Press 'H' for Health Summary")
    print("  - Press 'I' to add AI enemy")
    print("  - Press 'N' to advance scenario step")
    print("  - Press 'R' to add Heal status")
    print("  - Press 'B' to add Shield status")
    print("  - Press 'F' to trigger FX test")
    print("  - Press 'C' to add Combo to selected unit")
    print("  - Press 'E' to execute Combo")
    print("  - Press 'T' to add Trap event")
    print("  - Press 'ESC' or 'Q' to exit")
    print("  - Press 'SPACE' to end turn")

    # Add timeout functionality
    import time

    start_time = time.time()
    timeout_seconds = 60  # 1 minute timeout

    running = True
    while running:
        # Check timeout
        if time.time() - start_time > timeout_seconds:
            print(f"⏰ Demo timeout reached ({timeout_seconds}s)")
            break

        screen.fill((50, 50, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_a:
                    # Trigger Asset QA Scene
                    print("\n🔍 Launching Asset QA Scene...")
                    run_asset_qa_standalone(screen, auto_cycle=True)
                    print("✅ Asset QA Scene completed")
                elif event.key == pygame.K_s:
                    # Show sound report
                    print("\n" + sound_manager.create_sound_report())
                elif event.key == pygame.K_h:
                    # Show health summary
                    print("\n💚 Health Summary:")
                    health_ui.draw_health_summary(screen, game_state, ui_state)
                elif event.key == pygame.K_p:
                    # Add poison to selected unit or first player unit
                    target_unit = ui_state.selected_unit or "player_1"
                    status_manager.add_effect(target_unit, "poison", duration=5, stacks=2)
                    unit_data = game_state.units.units.get(target_unit, {})
                    fx_manager.trigger_status_apply_fx(
                        (
                            unit_data.get("x", 0) * tile_size,
                            unit_data.get("y", 0) * tile_size,
                        ),
                        "debuff",
                    )
                    print(f"🧪 Added poison to {target_unit}")
                elif event.key == pygame.K_r:
                    # Add heal over time to selected unit or first player unit
                    target_unit = ui_state.selected_unit or "player_1"
                    status_manager.add_effect(target_unit, "heal_over_time", duration=3, stacks=3)
                    unit_data = game_state.units.units.get(target_unit, {})
                    fx_manager.trigger_status_apply_fx(
                        (
                            unit_data.get("x", 0) * tile_size,
                            unit_data.get("y", 0) * tile_size,
                        ),
                        "buff",
                    )
                    print(f"💚 Added heal over time to {target_unit}")
                elif event.key == pygame.K_b:
                    # Add shield to selected unit or first player unit
                    target_unit = ui_state.selected_unit or "player_1"
                    status_manager.add_effect(target_unit, "shield", duration=4, stacks=1)
                    unit_data = game_state.units.units.get(target_unit, {})
                    fx_manager.trigger_status_apply_fx(
                        (
                            unit_data.get("x", 0) * tile_size,
                            unit_data.get("y", 0) * tile_size,
                        ),
                        "buff",
                    )
                    print(f"🛡️ Added shield to {target_unit}")
                elif event.key == pygame.K_f:
                    # Trigger FX test
                    fx_manager.trigger_damage_fx((400, 300), 15)
                    fx_manager.trigger_heal_fx((450, 300), 8)
                    fx_manager.trigger_critical_fx((500, 300))
                    print("✨ Triggered FX test sequence")
                elif event.key == pygame.K_c:
                    # Add combo to selected unit or first player unit
                    target_unit = ui_state.selected_unit or "player_1"
                    combo_name = "basic_attack_chain"
                    if combo_manager.add_combo(target_unit, combo_name):
                        print(f"⚔️ Added {combo_name} combo to {target_unit}")
                    else:
                        print(f"❌ Failed to add combo to {target_unit}")
                elif event.key == pygame.K_e:
                    # Execute combo for selected unit
                    target_unit = ui_state.selected_unit or "player_1"
                    result = combo_manager.execute_combo(target_unit, game_state)
                    if result["success"]:
                        print(f"⚔️ Executed combo for {target_unit}: {result['executed_steps']}")
                    else:
                        print(f"❌ Combo execution failed: {result['reason']}")
                elif event.key == pygame.K_t:
                    # Add trap event
                    trap_event = event_manager.create_event("trap_activation", position=(5, 5), damage=15)
                    if trap_event:
                        event_manager.add_event(trap_event)
                        print("💣 Added trap at position (5, 5)")
                    else:
                        print("❌ Failed to create trap event")
                elif event.key == pygame.K_p and event.mod & pygame.KMOD_CTRL:
                    # Particle QA Scene (Ctrl+P)
                    print("\n🎆 Launching Particle QA Scene...")
                    run_particle_qa_standalone(screen, auto_cycle=True)
                    print("✅ Particle QA Scene completed")
                elif event.key == pygame.K_v:
                    # Asset Validation Report
                    print("\n🎨 Asset Validation Summary:")
                    summary = asset_validator.get_validation_summary()
                    print(f"  Total Assets: {summary.get('total_assets', 0)}")
                    print(f"  Valid Assets: {summary.get('valid_assets', 0)}")
                    print(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")
                elif event.key == pygame.K_i:
                    # Add AI enemy
                    enemy_count = len([u for u in game_state.units.units.keys() if u.startswith("ai_enemy")])
                    enemy_id = f"ai_enemy_{enemy_count + 1}"

                    # Add enemy unit
                    game_state.units.units[enemy_id] = {
                        "unit_id": enemy_id,
                        "x": 7 + enemy_count,
                        "y": 7,
                        "hp": 15,
                        "max_hp": 15,
                        "team": "enemy",
                        "alive": True,
                        "attack_range": 1,
                        "detection_range": 3,
                    }

                    # Create AI for new enemy
                    enemy_ais[enemy_id] = EnemyAI(enemy_id, AIBehaviorType.AGGRESSIVE)
                    print(f"🤖 Added AI enemy: {enemy_id}")
                elif event.key == pygame.K_n:
                    # Advance scenario step
                    if not scenario_manager.is_scenario_complete():
                        if scenario_manager.check_step_completion(game_state):
                            if scenario_manager.advance_step():
                                result = scenario_manager.run_step(game_state)
                                print(f"📜 Advanced to scenario step: {result.get('step_name', 'Unknown')}")
                            else:
                                print("📜 Scenario complete!")
                        else:
                            print("📜 Current step not yet complete")
                    else:
                        print("📜 Scenario already complete")
                elif event.key == pygame.K_SPACE:
                    # End turn manually
                    if hasattr(game_state, "sim_runner"):
                        game_state.sim_runner.run_turn()
                        print(f"🔄 Turn ended. Current unit: {game_state.turn_controller.get_current_unit()}")

            # Handle input with game state integration
            handle_mouse_input(event, ui_state, tile_size, game_state)
            handle_keyboard_input(event, ui_state, game_state)

            # Handle game actions (movement, attacks)
            game_actions.handle_mouse_click(event, game_state, ui_state, tile_size)

            # Handle action menu clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_actions.handle_action_menu_click(event.pos, game_state, ui_state)

        # Process status effects each frame
        effect_results = status_manager.tick_effects(game_state)

        # Process combo cooldowns
        combo_manager.tick_cooldowns()

        # Evaluate dynamic events
        triggered_events = event_manager.evaluate_events(game_state)
        if triggered_events:
            print(f"🎯 Events triggered: {triggered_events}")

        # Process AI turns for enemies
        for unit_id in list(enemy_ais.keys()):
            # Check if unit is still alive
            unit_data = game_state.units.units.get(unit_id)
            if not unit_data or not unit_data.get("alive", True):
                # Remove dead AI
                del enemy_ais[unit_id]
                continue

            # Get AI decision
            ai = enemy_ais[unit_id]
            action_result = ai.decide_action(game_state)

            # Execute AI action
            if action_result.get("action") == "move":
                target_pos = action_result.get("target_pos")
                if target_pos:
                    unit_data["x"] = target_pos[0]
                    unit_data["y"] = target_pos[1]
            elif action_result.get("action") == "attack":
                target = action_result.get("target")
                if target:
                    # Simple attack: reduce target HP
                    damage = 5
                    target["hp"] = max(0, target["hp"] - damage)
                    if target["hp"] <= 0:
                        target["alive"] = False
                        print(f"💀 {target.get('unit_id', 'Unknown')} was defeated by AI!")

        # Process scenario management
        if not scenario_manager.is_scenario_complete():
            if scenario_manager.check_step_completion(game_state):
                print("📜 Step completed! Press 'N' to advance to next step.")

        # Check win/loss conditions
        if win_loss.check_victory_conditions(game_state):
            game_status = win_loss.get_game_status()
            if game_status == "victory":
                play_game_event_sound("game_victory")
                print(f"🎉 {win_loss.get_victory_message()}")
            elif game_status == "defeat":
                play_game_event_sound("game_defeat")
                print(f"💀 {win_loss.get_defeat_message()}")
            running = False

        # Render UI with full architecture integration
        ui_renderer.render_ui(game_state, ui_state)

        # Draw turn UI
        turn_ui.draw_turn_indicator(screen, game_state, ui_state)
        turn_ui.draw_unit_turn_highlight(screen, game_state, ui_state, tile_size)
        turn_ui.draw_turn_progress(screen, game_state, ui_state)

        # Draw health bars
        health_ui.draw_all_health_bars(screen, game_state, ui_state, tile_size)
        health_ui.update_damage_indicators(screen)

        # Draw status effects
        status_ui.draw_all_status_icons(screen, game_state, status_manager, ui_state, tile_size)
        status_ui.draw_status_summary(screen, game_state, status_manager, ui_state)

        # Update and draw visual effects
        fx_manager.update()
        fx_manager.draw_fx(screen)

        # Draw some basic terrain for context
        for x in range(0, 800, tile_size):
            for y in range(0, 600, tile_size):
                pygame.draw.rect(screen, (100, 150, 100), (x, y, tile_size, tile_size), 1)

        # Draw units on the grid
        for unit_id, unit_data in game_state.units.units.items():
            if unit_data.get("alive", True):
                x, y = unit_data.get("x", 0), unit_data.get("y", 0)
                color = (0, 0, 255) if unit_data.get("team") == "player" else (255, 0, 0)
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                pygame.draw.rect(screen, color, rect)

                # Draw unit ID
                font = pygame.font.Font(None, 16)
                text = font.render(unit_id, True, (255, 255, 255))
                screen.blit(text, (x * tile_size + 2, y * tile_size + 2))

        # Draw game status
        font = pygame.font.Font(None, 24)
        game_summary = win_loss.get_game_summary(game_state)
        status_text = f"Status: {game_summary.get('status', 'playing').upper()}"
        text_surf = font.render(status_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 570))

        pygame.display.flip()
        clock.tick(60)

    # Cleanup
    sound_manager.cleanup()
    pygame.quit()


if __name__ == "__main__":
    main()
