# @api
"""
KeyboardController
------------------
Interprets raw keyboard input (from InputState) and triggers high-level actions.
Current responsibilities:
- Toggle tactical overlays via number keys (1–4)
- Provide concise CLI/debug printout of overlay visibility after any toggle

This module intentionally avoids UI/pygame dependencies to keep it highly testable
and stable across refactors. Integrations (drawing, game loop) should query the
OverlayManager for visibility, not read controller internals.

Contracts:
- InputState must expose `keys_pressed: Set[str]` containing keys pressed *this frame*.
- OverlayManager must provide: toggle(name), is_visible(name), get_all_overlays().

Example:
    overlay = OverlayManager()
    kc = KeyboardController(overlay_manager=overlay, debug=True)
    kc.update(input_state)  # may print overlay snapshot if toggles occurred
"""

from __future__ import annotations

from typing import Dict, Optional, Set

try:
    # Local imports (kept light to reduce coupling)
    from game.input_state import InputState  # type: ignore
except Exception:  # pragma: no cover - allows import in isolation tests

    class InputStateStub:  # fallback stub for isolated tests
        keys_pressed: Set[str] = set()


try:
    from game.overlay_manager import OverlayManager  # type: ignore
except Exception:  # pragma: no cover

    class OverlayManagerStub:  # fallback stub for isolated tests
        def __init__(self) -> None:
            self._m = {
                "movement": True,
                "threat": True,
                "terrain": False,
                "attack": True,
            }

        def toggle(self, name: str) -> None:
            if name in self._m:
                self._m[name] = not self._m[name]

        def is_visible(self, name: str) -> bool:
            return self._m.get(name, False)

        def get_all_overlays(self) -> Dict[str, bool]:
            return dict(self._m)


DEFAULT_OVERLAY_KEY_MAP: Dict[str, str] = {
    "1": "movement",
    "2": "threat",
    "3": "terrain",
    "4": "attack",
}


class KeyboardController:
    """
    Translate raw key presses into game intents.

    Args:
        overlay_manager: Optional OverlayManager for toggles. If None, overlay keys are ignored.
        overlay_manager: Optional OverlayManager for toggles. If None, overlay keys are ignored.

    Public API:
        - update(input_state): process keys for this frame
        - bind_overlay_key(key, overlay_name): remap a key to an overlay
        - set_debug(flag): enable/disable CLI debug printouts
        - get_overlay_state_snapshot(): returns a dict copy of current overlay states
    """

    def __init__(
        self,
        overlay_manager: Optional[OverlayManager] = None,
        *,
        debug: bool = False,
    ) -> None:
        self.overlay_manager = overlay_manager
        # Copy the default map so callers can safely mutate this instance's mapping
        self.overlay_key_map: Dict[str, str] = dict(DEFAULT_OVERLAY_KEY_MAP)
        self.debug = debug

    # -------- Public API --------

    def update(self, input_state: InputState) -> None:
        """
        Process one frame of input. This should be called from the main loop.

        Contract: `input_state.keys_pressed` is a *per-frame* set of raw key strings.
        We defensively lowercase them to avoid casing drift (e.g., '1' vs '!' is caller's responsibility).
        """
        keys_pressed = {k.lower() for k in getattr(input_state, "keys_pressed", set())}

        toggled_any = self._handle_overlay_toggles(keys_pressed)

        # Only print when something changed to keep logs clean.
        if self.debug and toggled_any and self.overlay_manager:
            self._print_overlay_snapshot()

        # Placeholder: other actions (end turn, confirm, cancel) should be handled here.
        # Keep those as explicit, testable branches; avoid mixing game logic and rendering.

    def bind_overlay_key(self, key: str, overlay_name: str) -> None:
        """Bind/override a key (e.g., '5') to an overlay (e.g., 'fog')."""
        self.overlay_key_map[key.lower()] = overlay_name

    def set_debug(self, flag: bool) -> None:
        """Enable or disable CLI debug printouts."""
        self.debug = flag

    def get_overlay_state_snapshot(self) -> Dict[str, bool]:
        """Return a copy of current overlay visibility; empty dict if no manager is present."""
        if not self.overlay_manager:
            return {}
        return self.overlay_manager.get_all_overlays()

    # -------- Internals --------

    def _handle_overlay_toggles(self, keys_pressed: Set[str]) -> bool:
        """
        Toggle overlays for any matching number keys. Returns True if any toggle occurred.
        """
        if not self.overlay_manager or not keys_pressed:
            return False

        toggled = False
        for key, overlay_name in self.overlay_key_map.items():
            if key in keys_pressed:
                self.overlay_manager.toggle(overlay_name)
                toggled = True
        return toggled

    def _print_overlay_snapshot(self) -> None:
        """
        Print a concise, one-shot snapshot of overlay states; called only after a toggle.
        """
        assert self.overlay_manager is not None  # for type checkers
        snapshot = self.overlay_manager.get_all_overlays()
        print("[KeyboardController] Current Overlays:")
        for name, visible in snapshot.items():
            status = "✅" if visible else "❌"
            print(f"  - {name}: {status}")

    # -------- Dunder helpers --------

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return (
            f"KeyboardController(debug={self.debug}, "
            f"overlays={bool(self.overlay_manager)})"
        )
