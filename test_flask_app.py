"""
Quick test script to verify Flask app is working
"""

import requests
import time

BASE_URL = 'http://localhost:5000'

def test_app():
    print("\n" + "="*60)
    print("Testing Flask App")
    print("="*60)
    
    # Test 1: Check if app is running
    print("\n[TEST 1] Checking if app is running...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✓ App is running")
        else:
            print(f"✗ App returned status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to app. Is it running?")
        print("  Run: python simple_app.py")
        return
    
    # Test 2: Check video feed endpoint
    print("\n[TEST 2] Checking video feed endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/video_feed', stream=True, timeout=2)
        print(f"✓ Video feed endpoint accessible (status: {response.status_code})")
    except Exception as e:
        print(f"✗ Video feed error: {e}")
    
    # Test 3: Check metrics endpoint
    print("\n[TEST 3] Checking metrics endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/api/metrics')
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Metrics endpoint working")
            print(f"  Status: {data.get('status')}")
        else:
            print(f"✗ Metrics returned status: {response.status_code}")
    except Exception as e:
        print(f"✗ Metrics error: {e}")
    
    # Test 4: Check status endpoint
    print("\n[TEST 4] Checking status endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/api/status')
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status endpoint working")
            status_data = data.get('data', {})
            print(f"  Processing: {status_data.get('processing')}")
            print(f"  ADAS Initialized: {status_data.get('adas_initialized')}")
            print(f"  Source: {status_data.get('processing_stats', {}).get('source')}")
        else:
            print(f"✗ Status returned status: {response.status_code}")
    except Exception as e:
        print(f"✗ Status error: {e}")
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)
    print("\nIf all tests passed, open browser to:")
    print(f"  {BASE_URL}")
    print("\nThen:")
    print("  1. Click 'Start Webcam' to test webcam")
    print("  2. Click 'Upload Video' to test video upload")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_app()
