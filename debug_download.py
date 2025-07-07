#!/usr/bin/env python3
"""
Debug tool to check download link behavior
"""

import requests
import sys

def debug_download_link(download_url):
    """Debug a specific download link"""
    print(f"🔍 Debugging download link: {download_url}")
    print("=" * 60)
    
    # Extract token from URL
    if "/download/" in download_url:
        token = download_url.split("/download/")[-1].split("?")[0]
        base_url = download_url.split("/download/")[0]
        print(f"📋 Token: {token}")
        print(f"🌐 Base URL: {base_url}")
    else:
        print("❌ Invalid download URL format")
        return
    
    # Test 1: Try download without password
    print(f"\n🔓 Test 1: Download without password")
    try:
        response = requests.get(f"{base_url}/download/{token}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: File downloaded without password")
            print(f"   📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   📏 Content-Length: {response.headers.get('content-length', 'unknown')} bytes")
            return True
        elif response.status_code == 401:
            print("   🔐 PASSWORD REQUIRED: File needs password")
            try:
                error_detail = response.json().get('detail', 'No detail')
                print(f"   💬 Message: {error_detail}")
            except:
                print(f"   💬 Message: {response.text}")
        elif response.status_code == 404:
            print("   ❌ NOT FOUND: File expired or doesn't exist")
            try:
                error_detail = response.json().get('detail', 'No detail')
                print(f"   💬 Message: {error_detail}")
            except:
                print(f"   💬 Message: {response.text}")
        else:
            print(f"   ❌ UNEXPECTED ERROR: {response.status_code}")
            print(f"   💬 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ CONNECTION ERROR: Cannot connect to server")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    # Test 2: If password required, try with common passwords
    if response.status_code == 401:
        print(f"\n🔐 Test 2: Trying with common passwords")
        common_passwords = ["test", "test123", "password", "123456", "admin"]
        
        for pwd in common_passwords:
            try:
                test_response = requests.get(f"{base_url}/download/{token}?password={pwd}")
                if test_response.status_code == 200:
                    print(f"   ✅ SUCCESS with password: '{pwd}'")
                    return True
                else:
                    print(f"   ❌ Failed with password: '{pwd}' (Status: {test_response.status_code})")
            except Exception as e:
                print(f"   ❌ Error testing password '{pwd}': {e}")
        
        print(f"\n💡 To download this file, you need to:")
        print(f"   1. Get the correct password from the person who uploaded it")
        print(f"   2. Add it to the URL: {base_url}/download/{token}?password=CORRECT_PASSWORD")
    
    return False

def check_server_status(base_url):
    """Check if server is running and get status"""
    print(f"🏥 Checking server status...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server is running")
            print(f"   📊 Active files: {data['active_files']}")
            print(f"   💾 Memory usage: {data['memory_usage']['current_formatted']}")
            return True
        else:
            print(f"   ❌ Server error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to server at {base_url}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_download.py <download_url>")
        print("Example: python debug_download.py http://localhost:8000/download/abc123")
        return
    
    download_url = sys.argv[1]
    
    # Extract base URL for server status check
    if "/download/" in download_url:
        base_url = download_url.split("/download/")[0]
        
        # Check server status first
        if not check_server_status(base_url):
            print("\n❌ Server is not accessible. Make sure it's running.")
            return
        
        print()  # Empty line for readability
        
        # Debug the download link
        success = debug_download_link(download_url)
        
        print(f"\n{'='*60}")
        if success:
            print("🎉 RESULT: Download link is working correctly!")
        else:
            print("❌ RESULT: Download link has issues - see details above")
    else:
        print("❌ Invalid URL format. Expected: http://server/download/token")

if __name__ == "__main__":
    main()
