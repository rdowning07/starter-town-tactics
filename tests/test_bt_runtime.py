# Standard library imports
from typing import Optional

# Local imports
from core.ai.bt import BTContext, BTStatus, make_basic_combat_tree

# Third-party imports
# (none)


class Dummy(BTContext):
    def __init__(self, in_range: bool, can_move: bool, can_attack: bool):
        self._in_range = in_range
        self._can_move = can_move
        self._can_attack = can_attack
        self.moved = False
        self.attacked = False

    def enemy_in_attack_range(self) -> bool:
        return self._in_range

    def can_move(self) -> bool:
        return self._can_move

    def can_attack(self) -> bool:
        return self._can_attack

    def step_move_toward(self) -> bool:
        self.moved = True
        return True

    def step_attack(self) -> bool:
        self.attacked = True
        return True


def test_bt_attacks_when_in_range():
    """Test that BT chooses attack when enemy is in range."""
    bt = make_basic_combat_tree()
    ctx = Dummy(in_range=True, can_move=True, can_attack=True)
    s = bt.tick(ctx)
    assert s == BTStatus.SUCCESS
    assert ctx.attacked is True
    assert ctx.moved is False


def test_bt_moves_when_not_in_range():
    """Test that BT chooses move when enemy is not in range."""
    bt = make_basic_combat_tree()
    ctx = Dummy(in_range=False, can_move=True, can_attack=True)
    s = bt.tick(ctx)
    assert s == BTStatus.SUCCESS
    assert ctx.moved is True
    assert ctx.attacked is False


def test_bt_fails_when_no_actions_possible():
    """Test that BT fails when no actions are possible."""
    bt = make_basic_combat_tree()
    ctx = Dummy(in_range=False, can_move=False, can_attack=False)
    s = bt.tick(ctx)
    assert s == BTStatus.FAILURE
    assert ctx.moved is False
    assert ctx.attacked is False


def test_bt_sequence_behavior():
    """Test that Sequence nodes work correctly."""
    from core.ai.bt import Action, Condition, Sequence

    # Test successful sequence
    seq = Sequence([Condition("can_attack"), Action("step_attack")])
    ctx = Dummy(in_range=True, can_move=True, can_attack=True)
    s = seq.tick(ctx)
    assert s == BTStatus.SUCCESS
    assert ctx.attacked is True

    # Test failed sequence
    seq = Sequence([Condition("can_attack"), Action("step_attack")])
    ctx = Dummy(in_range=True, can_move=True, can_attack=False)
    s = seq.tick(ctx)
    assert s == BTStatus.FAILURE
    assert ctx.attacked is False


def test_bt_selector_behavior():
    """Test that Selector nodes work correctly."""
    from core.ai.bt import Action, Condition, Selector

    # Test successful selector (first branch succeeds)
    sel = Selector([Condition("can_attack"), Condition("can_move")])
    ctx = Dummy(in_range=True, can_move=True, can_attack=True)
    s = sel.tick(ctx)
    assert s == BTStatus.SUCCESS

    # Test successful selector (second branch succeeds)
    sel = Selector([Condition("can_attack"), Condition("can_move")])
    ctx = Dummy(in_range=True, can_move=True, can_attack=False)
    s = sel.tick(ctx)
    assert s == BTStatus.SUCCESS

    # Test failed selector
    sel = Selector([Condition("can_attack"), Condition("can_move")])
    ctx = Dummy(in_range=True, can_move=False, can_attack=False)
    s = sel.tick(ctx)
    assert s == BTStatus.FAILURE


def test_bt_composite_pattern():
    """Test that the composite pattern works correctly with nested nodes."""
    from core.ai.bt import Selector, Sequence

    bt = make_basic_combat_tree()

    # Verify the tree structure
    assert isinstance(bt, Selector)
    assert len(bt.children) == 2

    # First child should be attack sequence
    attack_seq = bt.children[0]
    assert isinstance(attack_seq, Sequence)
    assert len(attack_seq.children) == 3

    # Second child should be move sequence
    move_seq = bt.children[1]
    assert isinstance(move_seq, Sequence)
    assert len(move_seq.children) == 2


if __name__ == "__main__":
    # Run tests
    test_bt_attacks_when_in_range()
    test_bt_moves_when_not_in_range()
    test_bt_fails_when_no_actions_possible()
    test_bt_sequence_behavior()
    test_bt_selector_behavior()
    test_bt_composite_pattern()
    print("All BT tests passed!")
