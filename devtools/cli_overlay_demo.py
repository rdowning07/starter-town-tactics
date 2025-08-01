import time

from game.overlay_manager import OverlayManager


def main():
    om = OverlayManager()
    overlays = list(om.get_all_overlays().keys())

    print("\nOverlay Toggle Demo (CLI Mode)")
    print("Press number key (1–4) to toggle overlay, 'r' to reset, 'q' to quit.\n")

    for i, name in enumerate(overlays):
        print(f"[{i + 1}] {name}")

    while True:
        visible = om.get_all_overlays()
        print("\nCurrent Overlay States:")
        for k, v in visible.items():
            print(f"  - {k}: {'✅' if v else '❌'}")
        print("Waiting for input: ", end="", flush=True)

        key = input().strip().lower()
        if key == "q":
            break
        elif key == "r":
            om.reset()
        elif key in {"1", "2", "3", "4"}:
            idx = int(key) - 1
            if 0 <= idx < len(overlays):
                om.toggle(overlays[idx])
        else:
            print("Invalid input.")

        time.sleep(0.2)


if __name__ == "__main__":
    main()
