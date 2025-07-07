# 📏 File Size Limits and Memory Management

This document explains the file size limits and memory management features of the Secure File Share application.

## 🎯 Default Limits

### File Size Limits
- **Maximum file size**: 100 MB per file
- **Total memory limit**: 500 MB for all files combined
- **File expiry**: 1 hour (automatic cleanup)

### Why These Limits?
- **Memory storage**: Files are stored in RAM for security and speed
- **Server stability**: Prevents memory exhaustion and crashes
- **Performance**: Ensures responsive uploads and downloads
- **Multi-user support**: Allows multiple users to share files simultaneously

## ⚙️ Configuring Limits

You can customize the limits using environment variables:

```bash
# Set maximum file size to 200MB
export MAX_FILE_SIZE=209715200

# Set total memory limit to 1GB
export MAX_TOTAL_MEMORY=1073741824

# Run the application
python main.py
```

### Common Size Values
```bash
# 50MB
export MAX_FILE_SIZE=52428800

# 100MB (default)
export MAX_FILE_SIZE=104857600

# 200MB
export MAX_FILE_SIZE=209715200

# 500MB
export MAX_FILE_SIZE=524288000

# 1GB
export MAX_FILE_SIZE=1073741824
```

## 🔍 Monitoring Usage

### Status Endpoint
Visit `/status` to see current memory usage:
```json
{
  "status": "running",
  "active_files": 3,
  "memory_usage": {
    "current_bytes": 157286400,
    "current_formatted": "150.0 MB",
    "max_bytes": 524288000,
    "max_formatted": "500.0 MB",
    "usage_percentage": 30.0
  },
  "file_limits": {
    "max_file_size_bytes": 104857600,
    "max_file_size_formatted": "100.0 MB"
  }
}
```

### Server Logs
The server displays limits on startup:
```
🚀 Secure File Share Server Starting...
==================================================
Local Network: http://192.168.101.176:8000
Security: Per-file password protection available
File Limits: Max 100.0 MB per file, 500.0 MB total
==================================================
```

## 🚨 Error Handling

### File Too Large (413)
When a file exceeds the maximum size:
```json
{
  "detail": "File too large. Maximum file size is 100.0 MB"
}
```

### Memory Full (507)
When total memory limit is reached:
```json
{
  "detail": "Server memory full. Total memory limit is 500.0 MB. Current usage: 450.0 MB"
}
```

### Frontend Validation
The web interface shows:
- Maximum file size in the upload area
- Real-time validation when selecting files
- Error messages for oversized files

## 🧪 Testing File Limits

Run the comprehensive test suite:
```bash
python test_file_limits.py
```

This tests:
- ✅ Small file uploads (should succeed)
- ✅ Large file uploads (should be rejected)
- ✅ Memory limit enforcement
- ✅ Password protection
- ✅ Concurrent uploads
- ✅ File expiry functionality

## 📊 Performance Considerations

### Memory Usage
- Files are stored in RAM for security
- Memory is freed when files expire
- Background cleanup runs every minute

### Recommended Limits by Use Case

#### Personal Use (1-2 users)
```bash
export MAX_FILE_SIZE=104857600    # 100MB
export MAX_TOTAL_MEMORY=524288000 # 500MB
```

#### Small Team (3-5 users)
```bash
export MAX_FILE_SIZE=209715200     # 200MB
export MAX_TOTAL_MEMORY=1073741824 # 1GB
```

#### Large Team (5+ users)
```bash
export MAX_FILE_SIZE=524288000     # 500MB
export MAX_TOTAL_MEMORY=2147483648 # 2GB
```

### Server Requirements
- **RAM**: At least 2x the total memory limit
- **CPU**: Minimal impact, mostly I/O bound
- **Storage**: No persistent storage needed

## 🔧 Production Deployment

### Cloud Servers
For production deployment, consider:
- **Memory**: Choose instances with sufficient RAM
- **Monitoring**: Set up alerts for memory usage
- **Scaling**: Use load balancers for high traffic

### Docker Configuration
```dockerfile
ENV MAX_FILE_SIZE=209715200
ENV MAX_TOTAL_MEMORY=1073741824
```

### Kubernetes
```yaml
env:
- name: MAX_FILE_SIZE
  value: "209715200"
- name: MAX_TOTAL_MEMORY
  value: "1073741824"
resources:
  limits:
    memory: "2Gi"
  requests:
    memory: "1Gi"
```

## 🛡️ Security Implications

### Memory Attacks
- File size limits prevent memory exhaustion attacks
- Total memory limit prevents resource hogging
- Automatic expiry prevents long-term memory leaks

### Best Practices
1. **Set conservative limits** for internet-facing deployments
2. **Monitor memory usage** regularly
3. **Use HTTPS** for production deployments
4. **Enable file passwords** for sensitive content

## 🔮 Future Enhancements

Potential improvements for handling larger files:
- **Streaming uploads**: Process files without loading into memory
- **Disk storage**: Option to store files on disk instead of RAM
- **Cloud storage**: Integration with S3, Google Cloud, etc.
- **Compression**: Automatic file compression for storage
- **Chunked uploads**: Support for resumable uploads

## 📞 Troubleshooting

### Common Issues

**Q: Upload fails with "File too large" error**
A: Increase `MAX_FILE_SIZE` or compress your file

**Q: Server runs out of memory**
A: Increase `MAX_TOTAL_MEMORY` or wait for files to expire

**Q: Files disappear after 1 hour**
A: This is by design for security. Re-upload if needed

**Q: Multiple users can't upload simultaneously**
A: Increase `MAX_TOTAL_MEMORY` to accommodate more files

### Getting Help
- Check server logs for detailed error messages
- Use `/status` endpoint to monitor memory usage
- Run `test_file_limits.py` to verify functionality

---

**💡 Tip**: Start with default limits and adjust based on your actual usage patterns and server capacity.
