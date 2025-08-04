# tests/test_fx_manager.py

import pygame
import pytest
import time
from game.fx_manager import FXManager, FXType


@pytest.fixture(scope="module", autouse=True)
def pygame_setup():
    pygame.init()
    yield
    pygame.quit()


def test_trigger_and_update_flash_fx():
    fx_manager = FXManager()
    fx_manager.trigger_fx("flash", (100, 100), duration=0.5, intensity=1.0)

    assert len(fx_manager.effects) == 1
    assert fx_manager.effects[0].fx_type == FXType.FLASH

    # Update until it expires
    start_time = time.time()
    while time.time() - start_time < 1.0:  # Wait for effect to expire
        fx_manager.update()

    assert len(fx_manager.effects) == 0


def test_trigger_and_update_particle_fx():
    fx_manager = FXManager()
    fx_manager.trigger_fx("particle", (50, 50), duration=0.5, intensity=1.0)

    assert len(fx_manager.effects) == 1
    assert fx_manager.effects[0].fx_type == FXType.PARTICLE

    fx_manager.update()
    assert len(fx_manager.effects) == 1  # Still active


def test_screen_shake_offset_changes():
    fx_manager = FXManager()
    fx_manager.trigger_screen_shake(intensity=5.0, duration=0.5)
    
    # Check that screen shake is active
    assert fx_manager.is_effect_active("screen_shake")

    offsets = set()
    for _ in range(5):
        offset = fx_manager.get_shake_offset()
        assert isinstance(offset, tuple)
        assert len(offset) == 2
        offsets.add(offset)
        fx_manager.update()

    # Should have some non-zero offsets during shake
    assert any(o != (0, 0) for o in offsets)


def test_no_shake_offset_when_inactive():
    fx_manager = FXManager()
    offset = fx_manager.get_shake_offset()
    assert offset == (0, 0)

    fx_manager.update()
    assert fx_manager.get_shake_offset() == (0, 0)


def test_trigger_flash_method():
    fx_manager = FXManager()
    fx_manager.trigger_flash((100, 100), (255, 0, 0), 0.3, 1.0)
    
    assert len(fx_manager.effects) == 1
    assert fx_manager.effects[0].fx_type == FXType.FLASH
    assert fx_manager.effects[0].color == (255, 0, 0)


def test_trigger_screen_shake_method():
    fx_manager = FXManager()
    fx_manager.trigger_screen_shake(3.0, 0.5)
    
    assert len(fx_manager.effects) == 1
    assert fx_manager.effects[0].fx_type == FXType.SCREEN_SHAKE


def test_trigger_particle_method():
    fx_manager = FXManager()
    fx_manager.trigger_particle((100, 100), "sparkle", 5, 1.0)
    
    assert len(fx_manager.effects) == 5  # 5 particles created
    assert all(effect.fx_type == FXType.PARTICLE for effect in fx_manager.effects)


def test_clear_effects():
    fx_manager = FXManager()
    fx_manager.trigger_flash((100, 100))
    fx_manager.trigger_screen_shake(2.0, 0.3)
    
    assert len(fx_manager.effects) == 2
    
    fx_manager.clear_effects()
    assert len(fx_manager.effects) == 0
    assert fx_manager.get_shake_offset() == (0, 0)


def test_get_active_effects_count():
    fx_manager = FXManager()
    assert fx_manager.get_active_effects_count() == 0
    
    fx_manager.trigger_flash((100, 100))
    assert fx_manager.get_active_effects_count() == 1
    
    fx_manager.trigger_particle((100, 100), "sparkle", 3, 1.0)
    assert fx_manager.get_active_effects_count() == 4  # 1 flash + 3 particles
