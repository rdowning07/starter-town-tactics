# @api: Combat calculation is deterministic and pure
from dataclasses import dataclass
from typing import Tuple

from ..state import GameState, UnitRef


@dataclass(frozen=True)
class DamageResult:
    amount: int
    killed: bool


FACING_MOD = {"FRONT": 0, "SIDE": 1, "BACK": 2}  # flat bonus for v1
HEIGHT_CLAMP = (-2, 2)  # damage delta from height diff


def calc_height_bonus(src_h: int, tgt_h: int) -> int:
    d = max(HEIGHT_CLAMP[0], min(HEIGHT_CLAMP[1], src_h - tgt_h))
    return d  # -2..+2


def calc_facing_bonus(attacker_facing: str, attacker_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> int:
    # v1 shortcut: infer target quadrant relative to attacker vs. facing (FRONT/SIDE/BACK)
    # TODO: Replace with proper vector dot test vs. unit.facing
    rel = (target_pos[0] - attacker_pos[0], target_pos[1] - attacker_pos[1])
    # crude: if behind-ish -> BACK; else SIDE; else FRONT
    if abs(rel[0]) + abs(rel[1]) <= 1:
        return FACING_MOD["FRONT"]
    return FACING_MOD["SIDE"]  # upgrade with proper facing when state exposes it


def apply_attack(s: GameState, atk: UnitRef, tgt: UnitRef) -> DamageResult:
    a = s.unit(atk)
    b = s.unit(tgt)
    base = max(0, a.stats.atk - b.stats.def_)
    height = calc_height_bonus(a.stats.h, b.stats.h)
    facing = calc_facing_bonus(a.facing, a.pos, b.pos)
    dmg = max(0, base + height + facing)
    new_hp = max(0, b.stats.hp - dmg)
    b.stats.hp = new_hp
    return DamageResult(amount=dmg, killed=(new_hp == 0))
