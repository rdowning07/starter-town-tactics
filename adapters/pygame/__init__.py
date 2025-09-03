"""
Pygame adapters for Starter Town Tactics.
Provides thin adapters for rendering and input handling.
"""
from .input import InputController
from .renderer import Renderer

__all__ = ["Renderer", "InputController"]
