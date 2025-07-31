from game.overlay_manager import OverlayManager


def test_toggle_and_query():
    om = OverlayManager()
    assert om.is_visible("movement") is True
    om.toggle("movement")
    assert om.is_visible("movement") is False
    om.toggle("movement")
    assert om.is_visible("movement") is True


def test_enable_disable_individual():
    om = OverlayManager()
    om.disable("attack")
    assert om.is_visible("attack") is False
    om.enable("attack")
    assert om.is_visible("attack") is True


def test_get_active_and_all():
    om = OverlayManager()
    om.disable("movement")
    active = om.get_active_overlays()
    assert "movement" not in active
    all_ = om.get_all_overlays()
    assert "movement" in all_
    assert isinstance(all_, dict)


def test_reset_all():
    om = OverlayManager()
    om.reset()
    all_ = om.get_all_overlays()
    assert all(value is False for value in all_.values())
