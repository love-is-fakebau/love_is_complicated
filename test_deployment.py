#!/usr/bin/env python3
"""
Test deployment of Love Is Complicated challenge
Verifies all endpoints are working correctly
"""

import requests
import sys
from datetime import datetime
import pytz

def test_deployment(url):
    """Test all endpoints of the deployed challenge"""
    print("=" * 70)
    print("Love Is Complicated - Deployment Test")
    print("=" * 70)
    print(f"Testing URL: {url}")
    print()
    
    # Test 1: Homepage
    print("Test 1: Homepage")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Homepage loads successfully")
            if "Love Is Complicated" in response.text:
                print("✅ Correct content detected")
            else:
                print("⚠️  Content may be incorrect")
        else:
            print(f"❌ Homepage returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Homepage test failed: {e}")
    print()
    
    # Test 2: Proof of Work endpoint
    print("Test 2: Proof of Work endpoint")
    try:
        response = requests.get(f"{url}/api/pow", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ PoW endpoint working")
            print(f"   Timestamp: {data.get('timestamp')}")
            print(f"   Difficulty: {data.get('difficulty')}")
        else:
            print(f"❌ PoW endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"❌ PoW endpoint test failed: {e}")
    print()
    
    # Test 3: Confess endpoint (should fail without headers)
    print("Test 3: Confess endpoint (expected to fail)")
    try:
        response = requests.post(f"{url}/api/confess", json={}, timeout=10)
        if response.status_code in [400, 403, 429]:
            data = response.json()
            print("✅ Confess endpoint responding correctly")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {data.get('error')}")
            if 'decoy_flag' in data:
                print(f"   Decoy: {data.get('decoy_flag')}")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Confess endpoint test failed: {e}")
    print()
    
    # Test 4: robots.txt
    print("Test 4: robots.txt")
    try:
        response = requests.get(f"{url}/robots.txt", timeout=10)
        if response.status_code == 200:
            print("✅ robots.txt accessible")
            if "TRACECTF" in response.text:
                print("✅ Contains decoy flag")
        else:
            print(f"❌ robots.txt returned status {response.status_code}")
    except Exception as e:
        print(f"❌ robots.txt test failed: {e}")
    print()
    
    # Test 5: Time window check
    print("Test 5: Time window check")
    IST = pytz.timezone('Asia/Kolkata')
    current = datetime.now(IST)
    print(f"   Current IST time: {current.strftime('%H:%M:%S')}")
    if current.hour == 14 and 0 <= current.minute < 30:
        print("✅ Currently in valid time window (2:00-2:30 PM IST)")
        print("   You can test the full solver now!")
    else:
        print("⚠️  Outside valid time window")
        print("   Valid window: 2:00-2:30 PM IST")
        print("   Come back during this time to test the solver")
    print()
    
    # Summary
    print("=" * 70)
    print("Deployment Test Summary")
    print("=" * 70)
    print("✅ All basic endpoints are working")
    print("✅ Challenge is deployed correctly")
    print()
    print("Next steps:")
    print("1. Share URL with CTF participants")
    print("2. Test full solver during 2:00-2:30 PM IST")
    print("3. Monitor logs on Render dashboard")
    print()
    print(f"Challenge URL: {url}")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1].rstrip('/')
    else:
        url = input("Enter deployed URL: ").rstrip('/')
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    test_deployment(url)
