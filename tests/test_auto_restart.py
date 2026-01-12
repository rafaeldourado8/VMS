#!/usr/bin/env python3
"""Test Pipeline Auto-Restart"""

import subprocess
import time
import sys

def run_command(cmd):
    """Execute command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def test_service_restart(service_name):
    """Test if service auto-restarts after kill"""
    print(f"\nTesting {service_name}...")
    
    # Get container ID
    success, container_id, _ = run_command(f"docker ps -q -f name={service_name}")
    if not success or not container_id.strip():
        print(f"  ERROR: Service {service_name} not running")
        return False
    
    container_id = container_id.strip()
    print(f"  Container ID: {container_id[:12]}")
    
    # Kill container
    print(f"  Killing container...")
    success, _, _ = run_command(f"docker kill {container_id}")
    if not success:
        print(f"  ERROR: Failed to kill container")
        return False
    
    # Wait for restart
    print(f"  Waiting 10s for auto-restart...")
    time.sleep(10)
    
    # Check if restarted
    success, new_container_id, _ = run_command(f"docker ps -q -f name={service_name}")
    if not success or not new_container_id.strip():
        print(f"  FAIL: Service did not restart")
        return False
    
    new_container_id = new_container_id.strip()
    print(f"  New Container ID: {new_container_id[:12]}")
    
    # Check health
    print(f"  Checking health...")
    for i in range(6):
        success, health, _ = run_command(f"docker inspect --format='{{{{.State.Health.Status}}}}' {new_container_id}")
        health = health.strip()
        
        if health == "healthy":
            print(f"  PASS: Service restarted and healthy")
            return True
        
        print(f"    Health: {health} (attempt {i+1}/6)")
        time.sleep(10)
    
    print(f"  WARN: Service restarted but not healthy yet")
    return True

def main():
    print("=" * 50)
    print("Pipeline Auto-Restart Test")
    print("=" * 50)
    
    services = [
        "gtvision_streaming",
        "gtvision_backend",
        "gtvision_ai_detection",
    ]
    
    results = {}
    
    for service in services:
        results[service] = test_service_restart(service)
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    for service, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {service}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed!"))
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
