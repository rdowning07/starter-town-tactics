# @api
from typing import Dict


class OverlayManager:
    """
    Central manager for all tactical overlays.
    Allows toggling, enabling, and querying overlay visibility.
    """

    def __init__(self) -> None:
        # Each overlay name maps to a visibility boolean
        self._overlays: Dict[str, bool] = {
            "movement": True,
            "threat": True,
            "terrain": False,
            "attack": True,
        }

    def toggle(self, overlay_name: str) -> None:
        if overlay_name in self._overlays:
            self._overlays[overlay_name] = not self._overlays[overlay_name]
            print(f"[OverlayManager] Toggled '{overlay_name}' → {self._overlays[overlay_name]}")
        else:
            print(f"[OverlayManager] Warning: Unknown overlay '{overlay_name}'")

    def enable(self, overlay_name: str) -> None:
        self._overlays[overlay_name] = True

    def disable(self, overlay_name: str) -> None:
        self._overlays[overlay_name] = False

    def is_visible(self, overlay_name: str) -> bool:
        return self._overlays.get(overlay_name, False)

    def get_active_overlays(self) -> Dict[str, bool]:
        return {name: vis for name, vis in self._overlays.items() if vis}

    def get_all_overlays(self) -> Dict[str, bool]:
        return dict(self._overlays)  # returns a copy for inspection

    def reset(self) -> None:
        for key in self._overlays:
            self._overlays[key] = False
