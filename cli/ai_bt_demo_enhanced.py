# Standard library imports
import time
from typing import Optional

# Local imports
from core.ai.bt import make_basic_combat_tree
from core.ai.bt_profiler import profile_bt
from game.ai_bt_adapter import BTAdapter
from game.game_state import GameState

def print_bt_tree():
    """Display the Behavior Tree structure visually."""
    print("🤖 Behavior Tree Structure:")
    print("Selector (Choose best action):")
    print("  ├─ Sequence (Attack if possible):")
    print("  │   ├─ enemy_in_attack_range")
    print("  │   ├─ can_attack")
    print("  │   └─ step_attack")
    print("  └─ Sequence (Move toward target):")
    print("      ├─ can_move")
    print("      └─ step_move_toward")
    print()

def measure_bt_performance(bt, ctx, iterations=1000):
    """Measure BT decision-making performance."""
    print("⚡ Performance Testing...")
    start_time = time.time()
    for _ in range(iterations):
        bt.tick(ctx)
    elapsed = time.time() - start_time
    decisions_per_second = iterations / elapsed
    print(f"   Performance: {decisions_per_second:.0f} decisions/second")
    print(f"   Latency: {elapsed/iterations*1000:.2f}ms per decision")
    print()

def main() -> None:
    """Enhanced demo showing BT system capabilities."""
    print("🎯 Enhanced Behavior Tree AI Demo")
    print("=" * 50)
    
    # Show BT structure
    print_bt_tree()
    
    # Create enhanced game state with multiple units
    gs = GameState()
    
    # Create units in a more dramatic formation
    gs.add_unit("hero", "player", ap=8, hp=15)
    gs.units.update_unit_position("hero", 5, 5)
    
    gs.add_unit("enemy1", "ai", ap=6, hp=12)
    gs.units.update_unit_position("enemy1", 1, 1)
    
    gs.add_unit("enemy2", "ai", ap=4, hp=10)
    gs.units.update_unit_position("enemy2", 8, 1)
    
    gs.add_unit("enemy3", "ai", ap=3, hp=8)
    gs.units.update_unit_position("enemy3", 1, 8)
    
    # Display initial setup
    print("📊 Initial Battle Formation:")
    print("   Hero (Player): Position (5,5), HP: 15, AP: 8")
    print("   Enemy 1 (AI):  Position (1,1), HP: 12, AP: 6")
    print("   Enemy 2 (AI):  Position (8,1), HP: 10, AP: 4")
    print("   Enemy 3 (AI):  Position (1,8), HP: 8,  AP: 3")
    print()
    
    # Performance test
    bt = make_basic_combat_tree()
    ctx = BTAdapter(gs, "enemy1", "hero")
    measure_bt_performance(bt, ctx)
    
    print("🤖 AI Behavior Tree Decision Making:")
    print("-" * 50)
    
    # Simulate AI turns with enhanced feedback
    for step in range(10):
        print(f"\n📊 Step {step + 1}:")
        
        # Get current unit data safely
        hero_unit = gs.units.get("hero")
        enemy1_unit = gs.units.get("enemy1")
        enemy2_unit = gs.units.get("enemy2")
        enemy3_unit = gs.units.get("enemy3")
        
        if not all([hero_unit, enemy1_unit, enemy2_unit, enemy3_unit]):
            print("  ❌ Unit data missing!")
            break
            
        # Show all unit statuses
        if hero_unit:
            print(f"  Hero: ({hero_unit['x']},{hero_unit['y']}) HP:{hero_unit['hp']} AP:{gs.ap_manager.get_ap('hero')}")
        if enemy1_unit:
            print(f"  E1:   ({enemy1_unit['x']},{enemy1_unit['y']}) HP:{enemy1_unit['hp']} AP:{gs.ap_manager.get_ap('enemy1')}")
        if enemy2_unit:
            print(f"  E2:   ({enemy2_unit['x']},{enemy2_unit['y']}) HP:{enemy2_unit['hp']} AP:{gs.ap_manager.get_ap('enemy2')}")
        if enemy3_unit:
            print(f"  E3:   ({enemy3_unit['x']},{enemy2_unit['y']}) HP:{enemy3_unit['hp']} AP:{gs.ap_manager.get_ap('enemy3')}")
        
                # Run BT for each enemy
        enemies = [("enemy1", "hero"), ("enemy2", "hero"), ("enemy3", "hero")]
        
        for enemy_id, target_id in enemies:
            if gs.ap_manager.get_ap(enemy_id) > 0:
                ctx = BTAdapter(gs, enemy_id, target_id)
                status = bt.tick(ctx)
                
                # Show what happened
                if status == "SUCCESS":
                    new_enemy = gs.units.get(enemy_id)
                    old_enemy = enemy1_unit if enemy_id == "enemy1" else enemy2_unit if enemy_id == "enemy2" else enemy3_unit
                    
                    if new_enemy and old_enemy and (new_enemy['x'] != old_enemy['x'] or new_enemy['y'] != old_enemy['y']):
                        print(f"  ➡️  {enemy_id} moved toward hero")
                    
                    target_unit = gs.units.get(target_id)
                    if target_unit and hero_unit and target_unit['hp'] < hero_unit['hp']:
                        print(f"  ⚔️  {enemy_id} attacked hero!")
                elif status == "FAILURE":
                    print(f"  ❌ {enemy_id} BT failed - no actions possible")
                elif status == "RUNNING":
                    print(f"  🔄 {enemy_id} BT still running")
        
        # Check if game should end
        if hero_unit['hp'] <= 0:
            print("\n💀 Hero defeated! Game over.")
            break
        
        # Check if enemies reached hero
        enemies_reached = 0
        for enemy_id in ["enemy1", "enemy2", "enemy3"]:
            enemy = gs.units.get(enemy_id)
            if enemy and enemy['x'] == hero_unit['x'] and enemy['y'] == hero_unit['y']:
                enemies_reached += 1
        
        if enemies_reached >= 2:
            print(f"\n🎯 {enemies_reached} enemies engaged hero! Close combat!")
            break
        
        # Small delay for readability
        time.sleep(0.3)
    
    print("\n🏁 Demo completed!")
    
    # Final status
    final_hero = gs.units.get("hero")
    if final_hero:
        print(f"Final Hero: ({final_hero['x']}, {final_hero['y']}), HP: {final_hero['hp']}")
    
    for enemy_id in ["enemy1", "enemy2", "enemy3"]:
        final_enemy = gs.units.get(enemy_id)
        if final_enemy:
            print(f"Final {enemy_id}: ({final_enemy['x']}, {final_enemy['y']}), AP: {gs.ap_manager.get_ap(enemy_id)}")

if __name__ == "__main__":
    main()
