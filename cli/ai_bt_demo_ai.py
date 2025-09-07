#!/usr/bin/env python3
"""
AI methods for BT Fighter Demo - Extracted from main demo file for better organization.
"""

from typing import List, Tuple

import pygame


class BTFighterDemoAI:
    """AI behavior methods for the BT Fighter Demo."""

    def __init__(self, demo):
        """Initialize with reference to the main demo instance."""
        self.demo = demo

    def update_mage_ai(self) -> None:
        """Update mage AI behavior - ranged attacks with fireball projectiles."""
        current_time = pygame.time.get_ticks()

        # AP regeneration for mage
        if current_time - self.demo.last_mage_ap_regen > 3000:  # Every 3 seconds
            self.demo.last_mage_ap_regen = current_time
            self.demo.mage_ap = min(5, self.demo.mage_ap + 1)  # Cap at 5 AP
            print(f"🔥 Mage AP regenerated! Mage AP: {self.demo.mage_ap}")

        # Run mage AI every 2.5 seconds (more dynamic)
        if current_time - self.demo.last_mage_decision > 2500:
            self.demo.last_mage_decision = current_time

            # Find the closest living bandit
            closest_bandit = None
            closest_distance = float("inf")
            for i, bandit_pos in enumerate(self.demo.bandit_positions):
                if self.demo.bandit_hp[i] > 0:  # Only consider living bandits
                    distance = abs(self.demo.mage_pos[0] - bandit_pos[0]) + abs(self.demo.mage_pos[1] - bandit_pos[1])
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_bandit = i

            if closest_bandit is not None:
                bandit_pos = self.demo.bandit_positions[closest_bandit]

                # Check if mage can attack bandit (ranged attack)
                if self.demo._mage_can_attack_bandit(closest_bandit) and self.demo.mage_ap > 0:
                    # Mage attacks bandit from range!
                    damage = 2  # Less damage than melee but from range
                    self.demo.bandit_hp[closest_bandit] = max(0, self.demo.bandit_hp[closest_bandit] - damage)
                    self.demo.mage_ap = max(0, self.demo.mage_ap - 1)

                    # Spawn flying fireball projectile from mage to bandit
                    self.demo._spawn_fireball_projectile(
                        self.demo.mage_pos[0],
                        self.demo.mage_pos[1],
                        bandit_pos[0],
                        bandit_pos[1],
                    )

                    # Screen effects for mage attack
                    self.demo.screen_effects.hit_impact(3.0)
                    print(f"🔥 Mage casts fireball! Bandit {closest_bandit+1} HP: {self.demo.bandit_hp[closest_bandit]}")

                    # Check if bandit is defeated
                    if self.demo.bandit_hp[closest_bandit] <= 0:
                        self.demo.screen_effects.unit_defeated(5.0)
                        print(f"💀 Bandit {closest_bandit+1} defeated by mage!")
                        self.demo.ai_decision_text = f"🔥 Mage defeats Bandit {closest_bandit+1}!"

                # If mage can't attack, move toward bandit
                elif self.demo.mage_ap > 0 and not self.demo._mage_can_attack_bandit(closest_bandit):
                    # Move mage toward bandit to get in range
                    dx = bandit_pos[0] - self.demo.mage_pos[0]
                    dy = bandit_pos[1] - self.demo.mage_pos[1]

                    if abs(dx) > abs(dy):
                        # Move horizontally
                        new_x = self.demo.mage_pos[0] + (1 if dx > 0 else -1)
                        new_pos = [new_x, self.demo.mage_pos[1]]
                        if (
                            not self.demo._position_overlaps_any_bandit(new_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.fighter_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.healer_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.ranger_pos)
                        ):
                            self.demo.mage_pos[0] = new_x
                            self.demo.mage_ap = max(0, self.demo.mage_ap - 1)
                            print(f"🔥 Mage moves toward bandit: ({self.demo.mage_pos[0]}, {self.demo.mage_pos[1]})")
                    else:
                        # Move vertically
                        new_y = self.demo.mage_pos[1] + (1 if dy > 0 else -1)
                        new_pos = [self.demo.mage_pos[0], new_y]
                        if (
                            not self.demo._position_overlaps_any_bandit(new_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.fighter_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.healer_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.ranger_pos)
                        ):
                            self.demo.mage_pos[1] = new_y
                            self.demo.mage_ap = max(0, self.demo.mage_ap - 1)
                            print(f"🔥 Mage moves toward bandit: ({self.demo.mage_pos[0]}, {self.demo.mage_pos[1]})")

    def update_healer_ai(self) -> None:
        """Update healer AI behavior - healing allies."""
        current_time = pygame.time.get_ticks()

        # AP regeneration for healer
        if current_time - self.demo.last_healer_ap_regen > 2500:
            self.demo.last_healer_ap_regen = current_time
            self.demo.healer_ap = min(5, self.demo.healer_ap + 1)  # Cap at 5 AP
            print(f"💚 Healer AP regenerated! Healer AP: {self.demo.healer_ap}")

        # Run healer AI every 2.5 seconds (more dynamic)
        if current_time - self.demo.last_healer_decision > 2500:  # Reusing last_mage_decision for healer
            self.demo.last_healer_decision = current_time  # Update last_mage_decision

            # Find the ally with the lowest HP
            allies = [
                ("fighter", self.demo.fighter_hp, self.demo.fighter_pos),
                ("mage", self.demo.mage_hp, self.demo.mage_pos),
                ("healer", self.demo.healer_hp, self.demo.healer_pos),
                ("ranger", self.demo.ranger_hp, self.demo.ranger_pos),
            ]

            # Sort by HP (lowest first)
            allies.sort(key=lambda x: x[1])
            target_name, target_hp, target_pos = allies[0]

            distance = abs(self.demo.healer_pos[0] - target_pos[0]) + abs(self.demo.healer_pos[1] - target_pos[1])

            # Check if healer can heal the lowest HP ally
            if self.demo._healer_can_heal_target(target_pos) and self.demo.healer_ap > 0:
                # Healer heals the target!
                heal_amount = 3  # Increased healing
                if target_name == "fighter":
                    self.demo.fighter_hp = min(self.demo.fighter_hp + heal_amount, 10)  # Max HP 10
                elif target_name == "mage":
                    self.demo.mage_hp = min(self.demo.mage_hp + heal_amount, 15)  # Max HP 15
                else:  # ranger
                    self.demo.ranger_hp = min(self.demo.ranger_hp + heal_amount, 14)  # Max HP 14

                self.demo.healer_ap = max(0, self.demo.healer_ap - 1)

                # Spawn healing effect at healer's position
                self.demo._spawn_effect("healing", self.demo.healer_pos[0], self.demo.healer_pos[1])

                # Spawn healing effect at target's position too
                self.demo._spawn_effect("healing", target_pos[0], target_pos[1])

                # Get current HP after healing
                current_hp = (
                    self.demo.fighter_hp
                    if target_name == "fighter"
                    else (self.demo.mage_hp if target_name == "mage" else self.demo.ranger_hp)
                )

                # Screen effects for healing
                self.demo.screen_effects.heal_effect()
                print(f"💚 Healer heals {target_name}! {target_name} HP: {current_hp}")
                self.demo.ai_decision_text = (
                    f"💚 Healer heals {target_name.title()}! {target_name.title()} HP: {current_hp}"
                )

                # Don't trigger victory on full heal - that's not a win condition!

            # If healer can't heal, move toward the target
            elif self.demo.healer_ap > 0 and not self.demo._healer_can_heal_target(target_pos):
                # Move healer toward the target to get in range
                dx = target_pos[0] - self.demo.healer_pos[0]
                dy = target_pos[1] - self.demo.healer_pos[1]

                if abs(dx) > abs(dy):
                    # Move horizontally
                    new_x = self.demo.healer_pos[0] + (1 if dx > 0 else -1)
                    new_pos = [new_x, self.demo.healer_pos[1]]
                    if (
                        not self.demo._position_overlaps_any_bandit(new_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.fighter_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.mage_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.ranger_pos)
                    ):
                        self.demo.healer_pos[0] = new_x
                        self.demo.healer_ap = max(0, self.demo.healer_ap - 1)
                        print(
                            f"🧙‍♂️ Healer moves toward {target_name}: ({self.demo.healer_pos[0]}, {self.demo.healer_pos[1]})"
                        )
                else:
                    # Move vertically
                    new_y = self.demo.healer_pos[1] + (1 if dy > 0 else -1)
                    new_pos = [self.demo.healer_pos[0], new_y]
                    if (
                        not self.demo._position_overlaps_any_bandit(new_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.fighter_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.mage_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.ranger_pos)
                    ):
                        self.demo.healer_pos[1] = new_y
                        self.demo.healer_ap = max(0, self.demo.healer_ap - 1)
                        print(
                            f"🧙‍♂️ Healer moves toward {target_name}: ({self.demo.healer_pos[0]}, {self.demo.healer_pos[1]})"
                        )

    def update_bandit_ai(self) -> None:
        """Update bandit AI behavior - pursue and attack fighter."""
        current_time = pygame.time.get_ticks()

        # Run bandit AI every 2 seconds (more dynamic)
        if current_time - self.demo.last_bandit_decision > 2000:
            self.demo.last_bandit_decision = current_time

            # Update each living bandit
            for i, bandit_pos in enumerate(self.demo.bandit_positions):
                if self.demo.bandit_hp[i] <= 0:  # Skip dead bandits
                    continue

                distance = abs(bandit_pos[0] - self.demo.fighter_pos[0]) + abs(bandit_pos[1] - self.demo.fighter_pos[1])

                # Check if bandit can attack fighter (melee attack)
                if self.demo._bandit_can_attack_fighter(i) and self.demo.bandit_ap[i] > 0:
                    # Bandit attacks fighter!
                    damage = 2  # Less damage than ranged but melee
                    self.demo.fighter_hp = max(0, self.demo.fighter_hp - damage)
                    self.demo.bandit_ap[i] = max(0, self.demo.bandit_ap[i] - 2)

                    # Spawn slash effect at fighter's position
                    self.demo._spawn_effect("slash", self.demo.fighter_pos[0], self.demo.fighter_pos[1])

                    # Screen effects for bandit attack
                    self.demo.screen_effects.hit_impact(2.0)
                    print(f"👹 Bandit {i+1} attacks fighter! Fighter HP: {self.demo.fighter_hp}")
                    self.demo.ai_decision_text = f"👹 Bandit {i+1} attacks fighter! Fighter HP: {self.demo.fighter_hp}"

                    # Check if fighter is defeated
                    if self.demo.fighter_hp <= 0:
                        self.demo.screen_effects.unit_defeated(5.0)
                        print("💀 Fighter defeated by bandit!")
                        self.demo.ai_decision_text = f"💀 Fighter defeated by Bandit {i+1}!"

                # If bandit can't attack, move toward fighter
                elif self.demo.bandit_ap[i] > 0 and not self.demo._bandit_can_attack_fighter(i):
                    # Move bandit toward fighter
                    dx = self.demo.fighter_pos[0] - bandit_pos[0]
                    dy = self.demo.fighter_pos[1] - bandit_pos[1]

                    if abs(dx) > abs(dy):
                        # Move horizontally
                        new_x = bandit_pos[0] + (1 if dx > 0 else -1)
                        new_pos = [new_x, bandit_pos[1]]
                        if not self.demo._position_overlaps_any_bandit(new_pos):
                            self.demo.bandit_positions[i][0] = new_x
                            self.demo.bandit_ap[i] = max(0, self.demo.bandit_ap[i] - 1)
                            print(f"👹 Bandit {i+1} moves toward fighter: ({new_x}, {bandit_pos[1]})")
                    else:
                        # Move vertically
                        new_y = bandit_pos[1] + (1 if dy > 0 else -1)
                        new_pos = [bandit_pos[0], new_y]
                        if not self.demo._position_overlaps_any_bandit(new_pos):
                            self.demo.bandit_positions[i][1] = new_y
                            self.demo.bandit_ap[i] = max(0, self.demo.bandit_ap[i] - 1)
                            print(f"👹 Bandit {i+1} moves toward fighter: ({bandit_pos[0]}, {new_y})")

    def update_ranger_ai(self) -> None:
        """Update ranger AI behavior - ranged attacks with AP regeneration."""
        current_time = pygame.time.get_ticks()

        # AP regeneration for ranger
        if current_time - self.demo.last_ranger_ap_regen > 2000:  # Every 2 seconds
            self.demo.last_ranger_ap_regen = current_time
            self.demo.ranger_ap = min(5, self.demo.ranger_ap + self.demo.ranger_ap_regen)  # Cap at 5 AP
            print(f"🏹 Ranger AP regenerated! Ranger AP: {self.demo.ranger_ap}")

        # Run ranger AI every 2 seconds (more dynamic)
        if current_time - self.demo.last_ranger_decision > 2000:
            self.demo.last_ranger_decision = current_time

            # Find the closest living bandit
            closest_bandit = None
            closest_distance = float("inf")
            for i, bandit_pos in enumerate(self.demo.bandit_positions):
                if self.demo.bandit_hp[i] > 0:  # Only consider living bandits
                    distance = abs(self.demo.ranger_pos[0] - bandit_pos[0]) + abs(
                        self.demo.ranger_pos[1] - bandit_pos[1]
                    )
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_bandit = i

            if closest_bandit is not None:
                bandit_pos = self.demo.bandit_positions[closest_bandit]

                # Check if ranger can attack bandit (ranged attack)
                if self.demo._ranger_can_attack_bandit(closest_bandit) and self.demo.ranger_ap > 0:
                    # Ranger attacks bandit!
                    damage = 2  # Medium damage between fighter (3) and mage (2)
                    self.demo.bandit_hp[closest_bandit] = max(0, self.demo.bandit_hp[closest_bandit] - damage)
                    self.demo.ranger_ap = max(0, self.demo.ranger_ap - 1)

                    # Spawn arrow projectile from ranger to bandit
                    self.demo._spawn_arrow_projectile(
                        self.demo.ranger_pos[0],
                        self.demo.ranger_pos[1],
                        bandit_pos[0],
                        bandit_pos[1],
                    )

                    print(
                        f"🏹 Ranger shoots bandit {closest_bandit+1}! Bandit HP: {self.demo.bandit_hp[closest_bandit]}"
                    )

                    # Check if bandit is defeated
                    if self.demo.bandit_hp[closest_bandit] <= 0:
                        self.demo.screen_effects.unit_defeated(5.0)
                        print(f"💀 Bandit {closest_bandit+1} defeated by ranger!")
                        self.demo.ai_decision_text = f"🏹 Ranger defeats Bandit {closest_bandit+1}!"

            # If ranger can't attack, move toward bandit
            if (
                self.demo.ranger_ap > 0
                and closest_bandit is not None
                and not self.demo._ranger_can_attack_bandit(closest_bandit)
            ):
                # Move ranger toward bandit to get in range
                dx = self.demo.bandit_positions[closest_bandit][0] - self.demo.ranger_pos[0]
                dy = self.demo.bandit_positions[closest_bandit][1] - self.demo.ranger_pos[1]

                if abs(dx) > abs(dy):
                    # Move horizontally
                    new_x = self.demo.ranger_pos[0] + (1 if dx > 0 else -1)
                    new_pos = [new_x, self.demo.ranger_pos[1]]
                    if (
                        not self.demo._position_overlaps_any_bandit(new_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.fighter_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.mage_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.healer_pos)
                    ):
                        self.demo.ranger_pos[0] = new_x
                        self.demo.ranger_ap = max(0, self.demo.ranger_ap - 1)
                        print(f"🏹 Ranger moves toward bandit: ({self.demo.ranger_pos[0]}, {self.demo.ranger_pos[1]})")
                else:
                    # Move vertically
                    new_y = self.demo.ranger_pos[1] + (1 if dy > 0 else -1)
                    new_pos = [self.demo.ranger_pos[0], new_y]
                    if (
                        not self.demo._position_overlaps_any_bandit(new_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.fighter_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.mage_pos)
                        and not self.demo._positions_overlap(new_pos, self.demo.healer_pos)
                    ):
                        self.demo.ranger_pos[1] = new_y
                        self.demo.ranger_ap = max(0, self.demo.ranger_ap - 1)
                        print(f"🏹 Ranger moves toward bandit: ({self.demo.ranger_pos[0]}, {self.demo.ranger_pos[1]})")

    def update_fighter_ai(self) -> None:
        """Update fighter AI behavior - pursue and attack bandits."""
        current_time = pygame.time.get_ticks()

        # Run fighter AI every 2.5 seconds (more dynamic)
        if current_time - self.demo.last_fighter_ai_decision > 2500:
            self.demo.last_fighter_ai_decision = current_time

            # Find closest bandit
            closest_bandit = None
            closest_distance = float("inf")
            for i, bandit_pos in enumerate(self.demo.bandit_positions):
                if self.demo.bandit_hp[i] > 0:  # Only consider living bandits
                    distance = abs(self.demo.fighter_pos[0] - bandit_pos[0]) + abs(
                        self.demo.fighter_pos[1] - bandit_pos[1]
                    )
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_bandit = i

            if closest_bandit is not None:
                bandit_pos = self.demo.bandit_positions[closest_bandit]

                # Check if fighter can attack bandit
                if self.demo._fighter_can_attack_bandit(closest_bandit) and self.demo.fighter_ap > 0:
                    # Fighter attacks bandit!
                    damage = 3
                    self.demo.bandit_hp[closest_bandit] = max(0, self.demo.bandit_hp[closest_bandit] - damage)
                    self.demo.fighter_ap = max(0, self.demo.fighter_ap - 2)

                    # Spawn slash effect at bandit's position
                    self.demo._spawn_effect("slash", bandit_pos[0], bandit_pos[1])

                    # Update AI decision text
                    self.demo.ai_decision_text = f"🤖 Fighter AI attacks Bandit {closest_bandit+1}! Bandit HP: {self.demo.bandit_hp[closest_bandit]}"
                    print(
                        f"🤖 Fighter AI attacks Bandit {closest_bandit+1}! Bandit HP: {self.demo.bandit_hp[closest_bandit]}"
                    )

                    # Check if bandit is defeated
                    if self.demo.bandit_hp[closest_bandit] <= 0:
                        self.demo.screen_effects.unit_defeated(5.0)
                        print(f"💀 Bandit {closest_bandit+1} defeated by fighter!")
                        self.demo.ai_decision_text = f"🤖 Fighter AI defeats Bandit {closest_bandit+1}!"

                elif self.demo.fighter_ap > 0:
                    # Move fighter toward bandit
                    dx = bandit_pos[0] - self.demo.fighter_pos[0]
                    dy = bandit_pos[1] - self.demo.fighter_pos[1]

                    if abs(dx) > abs(dy):
                        # Move horizontally
                        new_x = self.demo.fighter_pos[0] + (1 if dx > 0 else -1)
                        new_pos = [new_x, self.demo.fighter_pos[1]]
                        if (
                            not self.demo._position_overlaps_any_bandit(new_pos)
                            and not self.demo._position_overlaps_any_bandit(new_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.mage_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.healer_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.ranger_pos)
                        ):
                            self.demo.fighter_pos[0] = new_x
                            self.demo.fighter_ap = max(0, self.demo.fighter_ap - 1)
                            print(
                                f"🤖 Fighter AI moves toward bandit: ({self.demo.fighter_pos[0]}, {self.demo.fighter_pos[1]})"
                            )
                    else:
                        # Move vertically
                        new_y = self.demo.fighter_pos[1] + (1 if dy > 0 else -1)
                        new_pos = [self.demo.fighter_pos[0], new_y]
                        if (
                            not self.demo._position_overlaps_any_bandit(new_pos)
                            and not self.demo._position_overlaps_any_bandit(new_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.mage_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.healer_pos)
                            and not self.demo._positions_overlap(new_pos, self.demo.ranger_pos)
                        ):
                            self.demo.fighter_pos[1] = new_y
                            self.demo.fighter_ap = max(0, self.demo.fighter_ap - 1)
                            print(
                                f"🤖 Fighter AI moves toward bandit: ({self.demo.fighter_pos[0]}, {self.demo.fighter_pos[1]})"
                            )
