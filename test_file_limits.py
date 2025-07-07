#!/usr/bin/env python3
"""
Comprehensive test suite for file size limits and functionality
"""

import requests
import json
import os
import tempfile
import time
import threading
from io import BytesIO

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_PASSWORD = "test123"

def create_test_file(size_bytes: int, filename: str = "test_file.bin") -> str:
    """Create a test file of specified size"""
    with tempfile.NamedTemporaryFile(mode='wb', suffix=f'_{size_bytes}b.bin', delete=False) as f:
        # Write data in chunks to avoid memory issues
        chunk_size = min(1024 * 1024, size_bytes)  # 1MB chunks or smaller
        remaining = size_bytes
        
        while remaining > 0:
            write_size = min(chunk_size, remaining)
            f.write(b'A' * write_size)
            remaining -= write_size
        
        return f.name

def format_size(bytes_size: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def test_server_status():
    """Test server status and get current limits"""
    print("📊 Testing server status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"   Active files: {data['active_files']}")
            print(f"   Memory usage: {data['memory_usage']['current_formatted']} / {data['memory_usage']['max_formatted']}")
            print(f"   Max file size: {data['file_limits']['max_file_size_formatted']}")
            return data
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return None

def test_small_file_upload():
    """Test uploading a small file (should succeed)"""
    print("\n📤 Testing small file upload...")
    
    # Create a 1KB test file
    test_file_path = create_test_file(1024, "small_test.txt")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('small_test.txt', f, 'text/plain')}
            data = {'file_password': TEST_PASSWORD}
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        
        if response.status_code == 200:
            print("✅ Small file uploaded successfully!")
            
            # Extract download token from response
            response_text = response.text
            import re
            token_match = re.search(r'/download/([a-f0-9-]+)', response_text)
            if token_match:
                token = token_match.group(1)
                print(f"   Download token: {token}")
                return token
            else:
                print("❌ Could not extract download token")
                return None
        else:
            print(f"❌ Upload failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading small file: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

def test_download_with_password(token: str):
    """Test downloading a file with password"""
    print(f"\n⬇️ Testing download with password...")
    
    try:
        # Test without password (should fail)
        response = requests.get(f"{BASE_URL}/download/{token}")
        if response.status_code == 401:
            print("✅ Download correctly rejected without password")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
        
        # Test with correct password (should succeed)
        response = requests.get(f"{BASE_URL}/download/{token}?password={TEST_PASSWORD}")
        if response.status_code == 200:
            print("✅ Download successful with correct password")
            print(f"   Downloaded {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Download failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing download: {e}")
        return False

def test_large_file_upload():
    """Test uploading a file that exceeds the size limit"""
    print(f"\n📤 Testing large file upload (should be rejected)...")
    
    # Create a 150MB test file (assuming 100MB limit)
    large_size = 150 * 1024 * 1024  # 150MB
    print(f"   Creating {format_size(large_size)} test file...")
    
    test_file_path = create_test_file(large_size, "large_test.bin")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('large_test.bin', f, 'application/octet-stream')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 413:
            print("✅ Large file correctly rejected (413 Payload Too Large)")
            print(f"   Response: {response.json().get('detail', 'No detail')}")
            return True
        else:
            print(f"❌ Expected 413, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing large file upload: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

def test_memory_limit():
    """Test uploading multiple files to test memory limit"""
    print(f"\n💾 Testing memory limit with multiple files...")
    
    # Upload multiple 50MB files to test memory limit
    file_size = 50 * 1024 * 1024  # 50MB each
    uploaded_tokens = []
    
    try:
        for i in range(12):  # Try to upload 12 x 50MB = 600MB (should exceed 500MB limit)
            print(f"   Uploading file {i+1}/12 ({format_size(file_size)})...")
            
            test_file_path = create_test_file(file_size, f"memory_test_{i}.bin")
            
            try:
                with open(test_file_path, 'rb') as f:
                    files = {'file': (f'memory_test_{i}.bin', f, 'application/octet-stream')}
                    response = requests.post(f"{BASE_URL}/upload", files=files)
                
                if response.status_code == 200:
                    # Extract token
                    import re
                    token_match = re.search(r'/download/([a-f0-9-]+)', response.text)
                    if token_match:
                        uploaded_tokens.append(token_match.group(1))
                        print(f"   ✅ File {i+1} uploaded successfully")
                elif response.status_code == 507:
                    print(f"   ✅ Memory limit reached at file {i+1} (507 Insufficient Storage)")
                    print(f"   Response: {response.json().get('detail', 'No detail')}")
                    return True
                else:
                    print(f"   ❌ Unexpected status code: {response.status_code}")
                    return False
                    
            finally:
                if os.path.exists(test_file_path):
                    os.unlink(test_file_path)
        
        print("❌ Memory limit was not reached (unexpected)")
        return False
        
    except Exception as e:
        print(f"❌ Error testing memory limit: {e}")
        return False

def test_file_expiry():
    """Test that files expire correctly (shortened for testing)"""
    print(f"\n⏰ Testing file expiry...")
    
    # Note: This test would normally take 1 hour, so we'll just verify the expiry time is set
    test_file_path = create_test_file(1024, "expiry_test.txt")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('expiry_test.txt', f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            # Check if expiry time is mentioned in response
            if "expires" in response.text.lower():
                print("✅ File expiry time is set and displayed")
                return True
            else:
                print("❌ No expiry information found in response")
                return False
        else:
            print(f"❌ Upload failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing file expiry: {e}")
        return False
    finally:
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

def test_concurrent_uploads():
    """Test multiple concurrent uploads"""
    print(f"\n🔄 Testing concurrent uploads...")
    
    def upload_file(file_id: int, results: list):
        """Upload a single file (for threading)"""
        test_file_path = create_test_file(1024 * 1024, f"concurrent_{file_id}.bin")  # 1MB
        
        try:
            with open(test_file_path, 'rb') as f:
                files = {'file': (f'concurrent_{file_id}.bin', f, 'application/octet-stream')}
                response = requests.post(f"{BASE_URL}/upload", files=files)
            
            results.append({
                'file_id': file_id,
                'status_code': response.status_code,
                'success': response.status_code == 200
            })
            
        except Exception as e:
            results.append({
                'file_id': file_id,
                'status_code': None,
                'success': False,
                'error': str(e)
            })
        finally:
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)
    
    # Start 5 concurrent uploads
    threads = []
    results = []
    
    for i in range(5):
        thread = threading.Thread(target=upload_file, args=(i, results))
        threads.append(thread)
        thread.start()
    
    # Wait for all uploads to complete
    for thread in threads:
        thread.join()
    
    # Check results
    successful_uploads = sum(1 for r in results if r['success'])
    print(f"   {successful_uploads}/5 concurrent uploads successful")
    
    if successful_uploads >= 4:  # Allow for some variance
        print("✅ Concurrent uploads working correctly")
        return True
    else:
        print("❌ Too many concurrent upload failures")
        for result in results:
            if not result['success']:
                print(f"   File {result['file_id']}: {result.get('error', f'Status {result['status_code']}')}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing File Size Limits and Functionality")
    print("=" * 60)
    
    # Test server status first
    server_data = test_server_status()
    if not server_data:
        print("\n❌ Server is not responding. Please start the server first:")
        print("   python main.py")
        return
    
    # Run all tests
    tests = [
        ("Small File Upload", test_small_file_upload),
        ("Large File Upload (Rejection)", test_large_file_upload),
        ("Memory Limit", test_memory_limit),
        ("File Expiry", test_file_expiry),
        ("Concurrent Uploads", test_concurrent_uploads),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "Small File Upload":
                # Special case: this returns a token for download test
                token = test_func()
                results[test_name] = token is not None
                if token:
                    print(f"\n{'='*20} Download with Password {'='*20}")
                    results["Download with Password"] = test_download_with_password(token)
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The file sharing application is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
