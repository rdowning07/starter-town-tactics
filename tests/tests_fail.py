"""Test case designed to fail to ensure test suite catches errors."""


def test_this_should_fail():
    """Intentionally failing test to verify test framework behavior."""
    assert 1 == 0  # This will fail
