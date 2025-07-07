#!/usr/bin/env python3
"""
Test script for the Local File Share application
"""

import requests
import json
import os
import tempfile

def test_server_status():
    """Test if the server is running"""
    try:
        response = requests.get("http://localhost:8000/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"   Local IP: {data['local_ip']}")
            print(f"   Active files: {data['active_files']}")
            print(f"   Server time: {data['server_time']}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def test_file_upload_download():
    """Test file upload and download functionality"""
    try:
        # Create a test file
        test_content = "Hello, this is a test file for Local File Share!"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file_path = f.name
        
        try:
            # Upload the file
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                response = requests.post("http://localhost:8000/upload", files=files)
            
            if response.status_code == 200:
                print("✅ File uploaded successfully!")
                
                # Extract download URL from the response HTML (simple approach)
                response_text = response.text
                if 'download/' in response_text:
                    # Find the download token in the response
                    import re
                    token_match = re.search(r'/download/([a-f0-9-]+)', response_text)
                    if token_match:
                        token = token_match.group(1)
                        download_url = f"http://localhost:8000/download/{token}"
                        print(f"   Download URL: {download_url}")
                        
                        # Test download
                        download_response = requests.get(download_url)
                        if download_response.status_code == 200:
                            downloaded_content = download_response.text
                            if downloaded_content == test_content:
                                print("✅ File downloaded successfully and content matches!")
                                return True
                            else:
                                print("❌ Downloaded content doesn't match original")
                                return False
                        else:
                            print(f"❌ Download failed with status: {download_response.status_code}")
                            return False
                    else:
                        print("❌ Could not extract download token from response")
                        return False
                else:
                    print("❌ No download URL found in response")
                    return False
            else:
                print(f"❌ Upload failed with status: {response.status_code}")
                return False
                
        finally:
            # Clean up test file
            os.unlink(test_file_path)
            
    except Exception as e:
        print(f"❌ Error testing file upload/download: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Local File Share Application")
    print("=" * 50)
    
    # Test server status
    print("\n1. Testing server status...")
    server_ok = test_server_status()
    
    if server_ok:
        # Test file upload/download
        print("\n2. Testing file upload and download...")
        upload_ok = test_file_upload_download()
        
        print("\n" + "=" * 50)
        if upload_ok:
            print("🎉 All tests passed! The application is working correctly.")
            print("\n📋 Next steps:")
            print("   1. Share the server URL with devices on your network")
            print("   2. Upload files through the web interface")
            print("   3. Share download links or QR codes with others")
        else:
            print("⚠️  Some tests failed. Check the server logs for details.")
    else:
        print("\n❌ Server is not responding. Please start the server first:")
        print("   python main.py")

if __name__ == "__main__":
    main()
