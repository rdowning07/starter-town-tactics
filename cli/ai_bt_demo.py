# Standard library imports
import time
from typing import Optional

# Local imports
from core.ai.bt import make_basic_combat_tree
from game.ai_bt_adapter import BTAdapter
from game.game_state import GameState

# Third-party imports
# (none)


def main() -> None:
    """Demonstrate the Behavior Tree AI system in action."""
    print("🎯 Behavior Tree AI Demo")
    print("=" * 40)

    # Create game state
    gs = GameState()

    # Create units with positions
    gs.add_unit("hero", "player", ap=6, hp=10)
    gs.units.update_unit_position("hero", 5, 5)

    gs.add_unit("enemy1", "ai", ap=6, hp=10)
    gs.units.update_unit_position("enemy1", 1, 1)

    hero_unit = gs.units.get("hero")
    enemy_unit = gs.units.get("enemy1")

    if not hero_unit or not enemy_unit:
        print("❌ Failed to create units!")
        return

    print(f"Player unit 'hero' at ({hero_unit['x']}, {hero_unit['y']})")
    print(f"AI unit 'enemy1' at ({enemy_unit['x']}, {enemy_unit['y']})")
    print()

    # Create Behavior Tree
    bt = make_basic_combat_tree()
    ctx = BTAdapter(gs, "enemy1", "hero")

    print("🤖 AI Behavior Tree Decision Making:")
    print("-" * 40)

    # Simulate AI turns
    for step in range(8):
        print(f"\n📊 Step {step + 1}:")
        print(f"  Enemy AP: {gs.ap_manager.get_ap('enemy1')}")

        # Get current unit data safely
        hero_unit = gs.units.get("hero")
        enemy_unit = gs.units.get("enemy1")

        if not hero_unit or not enemy_unit:
            print("  ❌ Unit data missing!")
            break

        print(f"  Enemy position: ({enemy_unit['x']}, {enemy_unit['y']})")
        print(f"  Hero HP: {hero_unit['hp']}")

        # Check conditions
        in_range = ctx.enemy_in_attack_range()
        can_move = ctx.can_move()
        can_attack = ctx.can_attack()

        print(f"  Conditions: in_range={in_range}, can_move={can_move}, can_attack={can_attack}")

        # Run Behavior Tree
        status = bt.tick(ctx)
        print(f"  BT Status: {status}")

        # Show what happened
        if status == "SUCCESS":
            # Check if enemy moved
            new_enemy_unit = gs.units.get("enemy1")
            if new_enemy_unit and (new_enemy_unit["x"] != enemy_unit["x"] or new_enemy_unit["y"] != enemy_unit["y"]):
                print("  ➡️  Enemy moved toward hero")
            # Check if hero was attacked
            new_hero_unit = gs.units.get("hero")
            if new_hero_unit and new_hero_unit["hp"] < hero_unit["hp"]:
                print("  ⚔️  Enemy attacked hero!")
        elif status == "FAILURE":
            print("  ❌ BT failed - no actions possible")
        elif status == "RUNNING":
            print("  🔄 BT still running")

        # Small delay for readability
        time.sleep(0.5)

        # Check if game should end
        new_hero_unit = gs.units.get("hero")
        new_enemy_unit = gs.units.get("enemy1")

        if new_hero_unit and new_hero_unit["hp"] <= 0:
            print("\n💀 Hero defeated! Game over.")
            break
        if (
            new_hero_unit
            and new_enemy_unit
            and new_enemy_unit["x"] == new_hero_unit["x"]
            and new_enemy_unit["y"] == new_hero_unit["y"]
        ):
            print("\n🎯 Enemy reached hero! Close combat engaged.")
            break

    print("\n🏁 Demo completed!")

    # Final status
    final_hero = gs.units.get("hero")
    final_enemy = gs.units.get("enemy1")

    if final_hero:
        print(f"Final positions - Hero: ({final_hero['x']}, {final_hero['y']}), HP: {final_hero['hp']}")
    if final_enemy:
        print(
            f"Final positions - Enemy: ({final_enemy['x']}, {final_enemy['y']}), AP: {gs.ap_manager.get_ap('enemy1')}"
        )


if __name__ == "__main__":
    main()
