#!/usr/bin/env python3
"""
Test script for media upload functionality (profile images and resumes)
"""
import requests
import json
from io import BytesIO
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def create_test_image():
    """Create a test image in memory"""
    # Create a simple test image
    img = Image.new('RGB', (300, 300), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def create_test_pdf():
    """Create a simple test PDF content"""
    # Simple PDF-like content (not a real PDF, but for testing)
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000125 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n209\n%%EOF"
    return BytesIO(pdf_content)

def test_media_uploads():
    print("🖼️ Testing Media Upload Functionality")
    print("=" * 50)
    
    # First, register and login a user
    print("\n1. Setting up test user...")
    user_data = {
        "username": "mediatest",
        "password": "testpass123",
        "full_name": "Media Test User"
    }
    
    # Register user
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    if response.status_code != 200:
        print(f"❌ User registration failed: {response.status_code}")
        return
    
    # Login user
    login_data = {
        "username": "mediatest",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ User login failed: {response.status_code}")
        return
    
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ User setup complete")
    
    # Test 2: Profile update with JSON data
    print("\n2. Testing Profile Update with JSON...")
    profile_data = {
        "bio": "I'm a test user for media uploads",
        "job_title": "Media Test Engineer",
        "skills": "Python, Django, Media Processing",
        "city": "Test City",
        "is_available_for_hire": True
    }
    
    response = requests.patch(f"{BASE_URL}/api/profiles/my_profile/", 
                            json=profile_data, headers=headers)
    if response.status_code == 200:
        print("✅ Profile updated successfully with JSON data")
    else:
        print(f"❌ Profile update failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 3: Upload profile image
    print("\n3. Testing Profile Image Upload...")
    
    # Get user profile first to get profile ID
    response = requests.get(f"{BASE_URL}/api/profiles/my_profile/", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get profile: {response.status_code}")
        return
    
    profile = response.json()
    profile_id = profile['id']
    
    # Create test image
    test_image = create_test_image()
    
    # Upload profile image
    files = {
        'profile_image': ('test_profile.jpg', test_image, 'image/jpeg')
    }
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/{profile_id}/upload_profile_image/",
        files=files,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Profile image uploaded successfully")
        print(f"   Image URL: {result.get('profile_image_url', 'N/A')}")
    else:
        print(f"❌ Profile image upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 4: Upload resume
    print("\n4. Testing Resume Upload...")
    
    # Create test PDF
    test_pdf = create_test_pdf()
    
    # Upload resume
    files = {
        'resume': ('test_resume.pdf', test_pdf, 'application/pdf')
    }
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/{profile_id}/upload_resume/",
        files=files,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Resume uploaded successfully")
        print(f"   Message: {result.get('message', 'N/A')}")
    else:
        print(f"❌ Resume upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 5: Verify uploads by getting profile
    print("\n5. Verifying Uploaded Files...")
    response = requests.get(f"{BASE_URL}/api/profiles/my_profile/", headers=headers)
    if response.status_code == 200:
        profile = response.json()
        
        profile_image_url = profile.get('profile_image_url')
        resume_url = profile.get('resume_url')
        
        print("✅ Profile retrieved successfully")
        print(f"   Profile Image: {'✅ Available' if profile_image_url else '❌ Not found'}")
        print(f"   Resume: {'✅ Available' if resume_url else '❌ Not found'}")
        
        if profile_image_url:
            print(f"   Profile Image URL: {profile_image_url}")
        if resume_url:
            print(f"   Resume URL: {resume_url}")
    else:
        print(f"❌ Failed to verify uploads: {response.status_code}")
    
    # Test 6: Test file validation (oversized file)
    print("\n6. Testing File Validation...")
    
    # Try to upload a very large image (this should fail)
    large_image = Image.new('RGB', (3000, 3000), color='blue')  # Large image
    large_img_byte_arr = BytesIO()
    large_image.save(large_img_byte_arr, format='JPEG', quality=100)
    large_img_byte_arr.seek(0)
    
    files = {
        'profile_image': ('large_test.jpg', large_img_byte_arr, 'image/jpeg')
    }
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/{profile_id}/upload_profile_image/",
        files=files,
        headers=headers
    )
    
    if response.status_code == 400:
        print("✅ File size validation working correctly")
        print(f"   Validation message: {response.json()}")
    else:
        print(f"⚠️  File size validation may not be working: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Media Upload Testing Complete!")
    print("\n💡 Key Features Tested:")
    print("   ✅ JSON profile updates")
    print("   ✅ Profile image upload")
    print("   ✅ Resume file upload")
    print("   ✅ File validation")
    print("   ✅ Media URL generation")

if __name__ == "__main__":
    try:
        test_media_uploads()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server.")
        print("💡 Make sure to run 'python manage.py runserver' first!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
