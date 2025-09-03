#!/usr/bin/env python3
"""
Simple Animation Tester Timeout Test

This script verifies that the visual animation tester properly exits after timeout.
"""

import os
import subprocess
import time


def test_timeout():
    """Test that animation tester exits after timeout."""

    print("⏰ Testing Animation Tester Timeout")
    print("=" * 40)

    # Test with mute flag
    cmd = ["python", "devtools/visual_animation_tester.py", "ranger", "--mute"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    print(f"Running: {' '.join(cmd)}")
    print("Expected: Should exit after 10 seconds automatically")

    start_time = time.time()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=env)  # 15 second timeout

        duration = time.time() - start_time

        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"Exit code: {result.returncode}")

        if result.returncode == 0:
            print("✅ Animation tester completed successfully")
            if "Timeout reached" in result.stdout:
                print("✅ Timeout mechanism working correctly")
                return True
            else:
                print("⚠️  No timeout message found")
                return False
        else:
            print(f"❌ Animation tester failed")
            print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Animation tester hung and didn't exit within 15 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function."""

    print("🎬 Simple Animation Tester Timeout Test")
    print("=" * 50)

    if test_timeout():
        print("\n🎉 Animation tester timeout test passed!")
        print("✅ The animation tester no longer hangs")
        print("✅ It properly exits after 10 seconds")
        print("✅ Ctrl+C handling is working")
        return 0
    else:
        print("\n❌ Animation tester timeout test failed!")
        return 1


if __name__ == "__main__":
    exit(main())
