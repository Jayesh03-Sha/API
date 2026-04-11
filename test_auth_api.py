"""
Test script for Authentication API endpoints
This script demonstrates how to test all the authentication endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:9000/api/auth"

def print_response(title, response):
    """Pretty print the response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_authentication_api():
    """Test all authentication endpoints"""
    
    # Test data
    test_user = {
        "username": "promise",
        "email": "promise@gmail.com",
        "password": "promise@123",
        "password2": "promise@123",
        "first_name": "Promise",
        "last_name": "insure"
    }
    
    print("\n" + "="*60)
    print("AUTHENTICATION API TEST SUITE")
    print("="*60)
    
    # 1. Register User
    print("\n[1/7] Testing User Registration...")
    response = requests.post(f"{BASE_URL}/register/", json=test_user)
    print_response("1. Register User", response)
    
    if response.status_code != 201:
        print("Registration failed! Testing login with existing user...")
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
    else:
        register_data = response.json()
        access_token = register_data.get('access')
        refresh_token = register_data.get('refresh')
        
        # 2. Get Profile
        print("\n[2/7] Testing Get User Profile...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print_response("2. Get User Profile", response)
        
        # 3. Update Profile
        print("\n[3/7] Testing Update User Profile...")
        update_data = {
            "phone_number": "+1234567890",
            "organization": "PROMISE INSURE"
        }
        response = requests.put(f"{BASE_URL}/profile/", json=update_data, headers=headers)
        print_response("3. Update User Profile", response)
        
        # 4. Change Password
        print("\n[4/7] Testing Change Password...")
        change_pwd_data = {
            "old_password": "promise@123",
            "new_password": "promise@456",
            "new_password2": "promise@456"
        }
        response = requests.post(f"{BASE_URL}/change-password/", json=change_pwd_data, headers=headers)
        print_response("4. Change Password", response)
        
        # 5. Refresh Token
        print("\n[5/7] Testing Token Refresh...")
        refresh_data = {"refresh": refresh_token}
        response = requests.post(f"{BASE_URL}/token/refresh/", json=refresh_data)
        print_response("5. Refresh Token", response)
        
        if response.status_code == 200:
            new_access_token = response.json().get('access')
            headers = {"Authorization": f"Bearer {new_access_token}"}
        
        # 6. Get Profile Again (with new token)
        print("\n[6/7] Testing Get User Profile (with new token)...")
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print_response("6. Get User Profile (new token)", response)
        
        # 7. Logout
        print("\n[7/7] Testing Logout...")
        logout_data = {"refresh": refresh_token}
        response = requests.post(f"{BASE_URL}/logout/", json=logout_data, headers=headers)
        print_response("7. Logout", response)
    
    # Login Test
    print("\n[Testing] Login with new credentials...")
    login_data = {
        "username": test_user["username"],
        "password": "promise@456"  # Changed password
    }
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    print_response("Login Test", response)
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)


if __name__ == "__main__":
    try:
        test_authentication_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print(f"Make sure the server is running at {BASE_URL}")
        print("\nTo start the server, run:")
        print("  cd api_test_server")
        print("  python manage.py runserver 127.0.0.1:9000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
