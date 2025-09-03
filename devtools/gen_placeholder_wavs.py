#!/usr/bin/env python3
"""
Generate Placeholder Sound Effects

This script creates simple WAV files for testing the sound system.
"""

import os
import wave


def generate_simple_wav(filename, duration=0.3, freq=440, volume=0.5, sample_rate=44100):
    """Generate a simple sine wave without numpy dependency."""

    try:
        import numpy as np

        amplitude = int(volume * 32767)
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        data = (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.int16)

        with wave.open(filename, "w") as f:
            f.setnchannels(1)  # mono
            f.setsampwidth(2)  # bytes per sample
            f.setframerate(sample_rate)
            f.writeframes(data.tobytes())

        return True

    except ImportError:
        print(f"⚠️  numpy not available, creating silent WAV: {filename}")
        # Create a silent WAV file as fallback
        with wave.open(filename, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            # Create silent data
            silent_data = b"\x00\x00" * int(sample_rate * duration)
            f.writeframes(silent_data)
        return False


def generate_fallback_wav(filename, duration=0.3, sample_rate=44100):
    """Generate a fallback WAV file without numpy."""

    with wave.open(filename, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        # Create silent data
        silent_data = b"\x00\x00" * int(sample_rate * duration)
        f.writeframes(silent_data)


def main():
    """Main function to generate placeholder sounds."""

    print("🎵 Generating Placeholder Sound Effects")
    print("=" * 40)

    output_dir = "assets/sfx"
    os.makedirs(output_dir, exist_ok=True)

    # Create simple tones for different effects
    sounds = {
        "slash.wav": {"freq": 880, "duration": 0.2, "desc": "Sword slash"},
        "death.wav": {"freq": 220, "duration": 0.5, "desc": "Unit death"},
        "fireball.wav": {"freq": 660, "duration": 0.3, "desc": "Magic attack"},
        "heal.wav": {"freq": 330, "duration": 0.4, "desc": "Healing spell"},
        "block.wav": {"freq": 110, "duration": 0.2, "desc": "Shield block"},
        "move.wav": {"freq": 440, "duration": 0.1, "desc": "Unit movement"},
        "select.wav": {"freq": 550, "duration": 0.1, "desc": "Unit selection"},
        "menu.wav": {"freq": 770, "duration": 0.15, "desc": "Menu navigation"},
    }

    numpy_available = True

    for name, config in sounds.items():
        path = os.path.join(output_dir, name)

        try:
            success = generate_simple_wav(path, freq=config["freq"], duration=config["duration"])

            if success:
                print(f"✅ Generated {name} ({config['desc']})")
            else:
                print(f"⚠️  Created silent {name} ({config['desc']})")
                numpy_available = False

        except (OSError, wave.Error) as e:
            print(f"❌ Failed to generate {name}: {e}")
            # Create fallback
            generate_fallback_wav(path, duration=config["duration"])
            print(f"⚠️  Created fallback {name}")

    if not numpy_available:
        print("\n💡 Install numpy for better sound generation:")
        print("   pip install numpy")

    print(f"\n🎉 Sound effects ready in: {output_dir}")
    print(f"📁 Total files: {len(sounds)}")


if __name__ == "__main__":
    main()
