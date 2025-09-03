# Standard library imports
from __future__ import annotations

from typing import Dict, List, Optional, Protocol

# Third-party imports
# (none)

# Local imports
# (none)


class BTStatus:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


class BTContext(Protocol):
    """Narrow interface the BT needs from the game."""

    # required getters (you can adapt in the adapter below)
    def enemy_in_attack_range(self) -> bool:
        ...

    def can_move(self) -> bool:
        ...

    def can_attack(self) -> bool:
        ...

    def step_move_toward(self) -> bool:
        ...

    def step_attack(self) -> bool:
        ...


class BTNode(Protocol):
    def tick(self, ctx: BTContext) -> str:
        ...


class Condition:
    def __init__(self, pred_name: str):
        self.pred_name = pred_name

    def tick(self, ctx: BTContext) -> str:
        pred = getattr(ctx, self.pred_name, None)
        if pred is None or not callable(pred):
            return BTStatus.FAILURE
        return BTStatus.SUCCESS if bool(pred()) else BTStatus.FAILURE


class Action:
    def __init__(self, act_name: str):
        self.act_name = act_name

    def tick(self, ctx: BTContext) -> str:
        act = getattr(ctx, self.act_name, None)
        if act is None or not callable(act):
            return BTStatus.FAILURE
        ok = bool(act())
        return BTStatus.SUCCESS if ok else BTStatus.RUNNING


class Sequence:
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, ctx: BTContext) -> str:
        for ch in self.children:
            s = ch.tick(ctx)
            if s != BTStatus.SUCCESS:
                return s
        return BTStatus.SUCCESS


class Selector:
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, ctx: BTContext) -> str:
        for ch in self.children:
            s = ch.tick(ctx)
            if s == BTStatus.SUCCESS:
                return BTStatus.SUCCESS
        return BTStatus.FAILURE


def make_basic_combat_tree() -> BTNode:
    """
    Selector(
      Sequence(Condition(enemy_in_attack_range), Condition(can_attack), Action(step_attack)),
      Sequence(Condition(can_move), Action(step_move_toward))
    )
    """
    return Selector(
        [
            Sequence([Condition("enemy_in_attack_range"), Condition("can_attack"), Action("step_attack")]),
            Sequence([Condition("can_move"), Action("step_move_toward")]),
        ]
    )
