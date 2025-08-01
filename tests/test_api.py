#!/usr/bin/env python3
"""
Simple API test script to verify job board functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("🚀 Testing Job Board API")
    print("=" * 50)
    
    # Test 1: Get all categories (public endpoint)
    print("\n1. Testing Categories API...")
    response = requests.get(f"{BASE_URL}/api/categories/")
    if response.status_code == 200:
        categories = response.json()['results']
        print(f"✅ Found {len(categories)} categories")
        for cat in categories[:3]:
            print(f"   - {cat['name']}: {cat['job_count']} jobs")
    else:
        print(f"❌ Categories API failed: {response.status_code}")
    
    # Test 2: Get all jobs (public endpoint)
    print("\n2. Testing Jobs API...")
    response = requests.get(f"{BASE_URL}/api/jobs/")
    if response.status_code == 200:
        jobs = response.json()['results']
        print(f"✅ Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"   - {job['title']} at {job['company_name']} ({job['location']})")
    else:
        print(f"❌ Jobs API failed: {response.status_code}")
    
    # Test 3: Test job filtering
    print("\n3. Testing Job Filtering...")
    response = requests.get(f"{BASE_URL}/api/jobs/?employment_type=full_time")
    if response.status_code == 200:
        jobs = response.json()['results']
        print(f"✅ Found {len(jobs)} full-time jobs")
    else:
        print(f"❌ Job filtering failed: {response.status_code}")
    
    # Test 4: Test job search
    print("\n4. Testing Job Search...")
    response = requests.get(f"{BASE_URL}/api/jobs/?search=engineer")
    if response.status_code == 200:
        jobs = response.json()['results']
        print(f"✅ Found {len(jobs)} jobs matching 'engineer'")
    else:
        print(f"❌ Job search failed: {response.status_code}")
    
    # Test 5: User Registration
    print("\n5. Testing User Registration...")
    user_data = {
        "username": "testuser",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    if response.status_code == 200:
        print("✅ User registration successful")
    else:
        print(f"❌ User registration failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 6: User Login
    print("\n6. Testing User Login...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        token = response.json()['access']
        print("✅ User login successful")
        
        # Test 7: Authenticated request
        print("\n7. Testing Authenticated Request...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/applications/my_applications/", headers=headers)
        if response.status_code == 200:
            applications = response.json()
            print(f"✅ Found {len(applications)} applications for authenticated user")
        else:
            print(f"❌ Authenticated request failed: {response.status_code}")
            
    else:
        print(f"❌ User login failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 8: Profile Management
    print("\n8. Testing User Profile Management...")
    if response.status_code == 200 and token:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user profile
        response = requests.get(f"{BASE_URL}/api/profiles/my_profile/", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print("✅ Retrieved user profile successfully")
            
            # Update profile
            profile_data = {
                "bio": "I am a passionate software developer with expertise in Python and Django.",
                "job_title": "Senior Backend Developer",
                "skills": "Python, Django, REST API, PostgreSQL",
                "city": "New York",
                "is_available_for_hire": True
            }
            response = requests.patch(f"{BASE_URL}/api/profiles/my_profile/", 
                                    json=profile_data, headers=headers)
            if response.status_code == 200:
                print("✅ Updated user profile successfully")
            else:
                print(f"❌ Profile update failed: {response.status_code}")
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
    
    # Test 9: Public Profiles
    print("\n9. Testing Public Profiles...")
    response = requests.get(f"{BASE_URL}/api/profiles/")
    if response.status_code == 200:
        profiles = response.json()['results']
        print(f"✅ Found {len(profiles)} public profiles")
        for profile in profiles[:2]:
            user = profile.get('user', {})
            print(f"   - {user.get('username', 'Unknown')}: {profile.get('job_title', 'No title')}")
    else:
        print(f"❌ Public profiles failed: {response.status_code}")
    
    # Test 10: Available Candidates
    print("\n10. Testing Available Candidates...")
    response = requests.get(f"{BASE_URL}/api/profiles/available_candidates/")
    if response.status_code == 200:
        candidates = response.json()['results']
        print(f"✅ Found {len(candidates)} available candidates")
    else:
        print(f"❌ Available candidates failed: {response.status_code}")
    
    # Test 11: API Documentation
    print("\n11. Testing API Documentation...")
    response = requests.get(f"{BASE_URL}/swagger/")
    if response.status_code == 200:
        print("✅ Swagger documentation accessible")
    else:
        print(f"❌ Swagger documentation failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print(f"📋 Visit {BASE_URL}/swagger/ for interactive API documentation")
    print(f"👑 Admin panel: {BASE_URL}/admin/ (admin/admin123)")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server.")
        print("💡 Make sure to run 'python manage.py runserver' first!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
