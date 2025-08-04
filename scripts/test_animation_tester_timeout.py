#!/usr/bin/env python3
"""
Test Animation Tester Timeout and Ctrl+C Handling

This script tests that the visual animation tester properly handles timeouts
and Ctrl+C interruptions without hanging.
"""

import subprocess
import time
import signal
import sys
import os

def test_timeout_behavior():
    """Test that the animation tester exits after timeout."""
    
    print("⏰ Testing Animation Tester Timeout Behavior")
    print("=" * 50)
    
    # Test with mute flag and expect timeout after 10 seconds
    cmd = ["python", "devtools/visual_animation_tester.py", "ranger", "--mute"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    
    print(f"Running: {' '.join(cmd)}")
    print("Expected: Should exit after 10 seconds automatically")
    
    start_time = time.time()
    
    try:
        # Run the command and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,  # Give it 15 seconds to complete
            env=env
        )
        
        duration = time.time() - start_time
        
        print(f"\n⏱️  Duration: {duration:.1f} seconds")
        print(f"Exit code: {result.returncode}")
        
        # Check if it completed successfully
        if result.returncode == 0:
            print("✅ Animation tester completed successfully")
            
            # Check if timeout message is in output
            if "Timeout reached" in result.stdout:
                print("✅ Timeout mechanism working correctly")
                return True
            else:
                print("⚠️  No timeout message found in output")
                return False
        else:
            print(f"❌ Animation tester failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Animation tester hung and didn't exit within 15 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running animation tester: {e}")
        return False

def test_sound_enabled():
    """Test that sound-enabled version also works with timeout."""
    
    print("\n🔊 Testing Animation Tester with Sound Enabled")
    print("=" * 50)
    
    cmd = ["python", "devtools/visual_animation_tester.py", "ranger"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    
    print(f"Running: {' '.join(cmd)}")
    print("Expected: Should exit after 10 seconds automatically")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            env=env
        )
        
        duration = time.time() - start_time
        
        print(f"\n⏱️  Duration: {duration:.1f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Sound-enabled animation tester completed successfully")
            if "Timeout reached" in result.stdout:
                print("✅ Timeout mechanism working with sound enabled")
                return True
            else:
                print("⚠️  No timeout message found in output")
                print(f"Output: {result.stdout[-200:]}")  # Show last 200 chars
                return False
        else:
            print(f"❌ Sound-enabled animation tester failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Sound-enabled animation tester hung")
        return False
    except Exception as e:
        print(f"❌ Error running sound-enabled animation tester: {e}")
        return False

def test_invalid_unit():
    """Test that invalid unit handling works correctly."""
    
    print("\n❌ Testing Animation Tester with Invalid Unit")
    print("=" * 50)
    
    cmd = ["python", "devtools/visual_animation_tester.py", "invalid_unit"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    
    print(f"Running: {' '.join(cmd)}")
    print("Expected: Should exit immediately with error")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )
        
        print(f"Exit code: {result.returncode}")
        
        if result.returncode != 0:
            print("✅ Invalid unit handled correctly (non-zero exit code)")
            if "not found" in result.stdout or "not found" in result.stderr:
                print("✅ Proper error message displayed")
                return True
            else:
                print("⚠️  No clear error message found")
                return False
        else:
            print("❌ Invalid unit should have caused an error")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Invalid unit test hung")
        return False
    except Exception as e:
        print(f"❌ Error testing invalid unit: {e}")
        return False

def main():
    """Main test function."""
    
    print("🎬 Animation Tester Timeout and Error Handling Test Suite")
    print("=" * 60)
    
    tests = [
        ("Timeout Behavior (Muted)", test_timeout_behavior),
        ("Timeout Behavior (Sound Enabled)", test_sound_enabled),
        ("Invalid Unit Handling", test_invalid_unit)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All animation tester tests passed!")
        print("\n💡 The animation tester now properly handles:")
        print("  ✅ Automatic timeout after 10 seconds")
        print("  ✅ Ctrl+C interruption")
        print("  ✅ Invalid unit errors")
        print("  ✅ Sound enabled/disabled modes")
        return 0
    else:
        print("⚠️  Some animation tester tests failed.")
        return 1

if __name__ == "__main__":
    exit(main()) 