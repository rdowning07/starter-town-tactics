"""
Pygame adapters for Starter Town Tactics.
Provides thin adapters for rendering and input handling.
"""
from .renderer import Renderer
from .input import InputController

__all__ = ['Renderer', 'InputController']
