#!/usr/bin/env python3
"""
Integration test for remember me functionality
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def test_remember_me_functionality():
    print("🔒 Testing Remember Me Functionality")
    print("=" * 50)
    
    # Test 1: Register a test user
    print("\n1. Setting up test user...")
    user_data = {
        "username": "remembermetest",
        "password": "testpass123",
        "first_name": "Remember",
        "last_name": "Me",
        "full_name": "Remember Me User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    if response.status_code != 200:
        print(f"❌ User registration failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    print("✅ Test user registered successfully")
    
    # Test 2: Login without remember me (should get 1 hour token)
    print("\n2. Testing login without remember me...")
    login_data = {
        "username": "remembermetest",
        "password": "testpass123",
        "remember_me": False
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        data = response.json()
        print("✅ Login without remember me successful")
        print(f"   Token expires in: {data.get('expires_in', 'N/A')}")
        print(f"   Remember me: {data.get('remember_me', 'N/A')}")
        print(f"   Has refresh token: {'refresh' in data}")
        
        if data.get('expires_in') == '1 hour' and not data.get('remember_me'):
            print("✅ Correct token expiration for non-remember me login")
        else:
            print("❌ Incorrect token configuration for non-remember me login")
    else:
        print(f"❌ Login without remember me failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 3: Login with remember me (should get 15 days token)
    print("\n3. Testing login with remember me...")
    login_data_remember = {
        "username": "remembermetest",
        "password": "testpass123",
        "remember_me": True
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data_remember)
    if response.status_code == 200:
        data = response.json()
        print("✅ Login with remember me successful")
        print(f"   Token expires in: {data.get('expires_in', 'N/A')}")
        print(f"   Remember me: {data.get('remember_me', 'N/A')}")
        print(f"   Has refresh token: {'refresh' in data}")
        
        if data.get('expires_in') == '15 days' and data.get('remember_me'):
            print("✅ Correct token expiration for remember me login")
        else:
            print("❌ Incorrect token configuration for remember me login")
            
        # Store tokens for further testing
        access_token = data.get('access')
        refresh_token = data.get('refresh')
        
        # Test 4: Test authenticated request with remember me token
        print("\n4. Testing authenticated request with remember me token...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/api/profiles/my_profile/", headers=headers)
        
        if response.status_code == 200:
            print("✅ Authenticated request with remember me token successful")
        else:
            print(f"❌ Authenticated request failed: {response.status_code}")
        
        # Test 5: Test refresh token functionality (if available)
        if refresh_token:
            print("\n5. Testing refresh token functionality...")
            refresh_data = {"refresh": refresh_token}
            response = requests.post(f"{BASE_URL}/api/token/refresh/", json=refresh_data)
            
            if response.status_code == 200:
                new_data = response.json()
                print("✅ Token refresh successful")
                print(f"   New access token received: {'access' in new_data}")
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(f"   Error: {response.text}")
    else:
        print(f"❌ Login with remember me failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 6: Login with default (no remember_me field)
    print("\n6. Testing login with default remember me setting...")
    login_data_default = {
        "username": "remembermetest",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data_default)
    if response.status_code == 200:
        data = response.json()
        print("✅ Login with default settings successful")
        print(f"   Token expires in: {data.get('expires_in', 'N/A')}")
        print(f"   Remember me: {data.get('remember_me', 'N/A')}")
        print(f"   Has refresh token: {'refresh' in data}")
        
        if data.get('expires_in') == '1 hour' and not data.get('remember_me'):
            print("✅ Default remember me setting works correctly (False)")
        else:
            print("❌ Default remember me setting not working correctly")
    else:
        print(f"❌ Login with default settings failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 7: Test invalid login scenarios
    print("\n7. Testing invalid login scenarios...")
    
    # Invalid JSON
    response = requests.post(
        f"{BASE_URL}/auth/login/", 
        data='invalid json', 
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 400:
        print("✅ Invalid JSON handling works correctly")
    else:
        print(f"❌ Invalid JSON not handled properly: {response.status_code}")
    
    # Missing username
    response = requests.post(f"{BASE_URL}/auth/login/", json={"password": "testpass123"})
    if response.status_code == 400:
        print("✅ Missing username validation works correctly")
    else:
        print(f"❌ Missing username not validated properly: {response.status_code}")
    
    # Missing password
    response = requests.post(f"{BASE_URL}/auth/login/", json={"username": "remembermetest"})
    if response.status_code == 400:
        print("✅ Missing password validation works correctly")
    else:
        print(f"❌ Missing password not validated properly: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Remember Me Testing Complete!")
    print("\n💡 Key Features Tested:")
    print("   ✅ Login without remember me (1 hour expiration)")
    print("   ✅ Login with remember me (15 days expiration)")
    print("   ✅ Default remember me setting (False)")
    print("   ✅ Refresh token functionality")
    print("   ✅ Input validation")
    print("   ✅ Token authentication")

if __name__ == "__main__":
    try:
        test_remember_me_functionality()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server.")
        print("💡 Make sure to run 'python manage.py runserver' first!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
