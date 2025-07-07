# 🌐 Secure File Share

A secure, fast, and easy-to-use file sharing application. Share files locally or over the internet with per-file password protection!

## ✨ Features

- 🔐 **Per-File Password Protection** - Each file can have its own password for maximum security
- 🌐 **Internet Ready** - Deploy locally or on the internet with proper security
- ⚡ **Fast Transfer** - Direct file sharing with minimal overhead
- 📱 **Cross-Platform** - Works on phones, tablets, computers - any device with a web browser
- 🎯 **Simple to Use** - Just drag & drop or click to select files
- 📊 **QR Code Sharing** - Generate QR codes for easy mobile sharing
- ⏰ **Auto-Expiry** - Files automatically expire after 1 hour for security
- 🎨 **Modern UI** - Clean, responsive design optimized for all devices
- 🛡️ **Security First** - Built with internet deployment and security in mind

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- All devices must be on the same Wi-Fi network

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd fileshare
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   python main.py
   ```

4. **Access the application**
   - The server will display the local IP address (e.g., `http://192.168.1.100:8000`)
   - Open this URL in any web browser on your network
   - Share this URL with other devices on the same network

## 📖 How to Use

1. **Upload a file**
   - Open the web interface in your browser
   - Drag & drop a file or click to browse and select
   - **Set a password** (recommended for internet sharing)
   - Click "Share File" to upload

2. **Share the download link**
   - Copy the generated download link
   - **Share the password separately** for better security
   - Or show the QR code for others to scan
   - Share via message, email, or any communication app

3. **Download on other devices**
   - Open the shared link in any web browser
   - **Add the password** to the URL: `?password=YOUR_PASSWORD`
   - Or scan the QR code with a phone camera
   - The file will download directly

## 🔧 Configuration

### Change Port
Edit `main.py` and modify the port in the last line:
```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # Change 8000 to 8080
```

### Change File Expiry Time
Edit `main.py` and modify the expiry time in the upload function:
```python
"expires_at": datetime.now(timezone.utc) + timedelta(hours=2)  # Change from 1 to 2 hours
```

## 🛡️ Security Features

- **Per-file password protection** - Each file can have its own unique password
- **Token-based access** - Each file gets a unique, random download token
- **Automatic expiry** - Files are automatically deleted after 1 hour
- **Internet ready** - Secure deployment options for internet access
- **Memory storage** - Files are stored in RAM, not saved to disk
- **IP tracking** - Server tracks which IP uploaded each file
- **Password strength indicator** - Real-time feedback on password security

## 🌐 Network Requirements

### Local Network Usage
- All devices must be connected to the same Wi-Fi network
- The server device must allow incoming connections on port 8000
- Firewall may need to be configured to allow the connection

### Internet Deployment
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed internet deployment instructions
- Supports cloud servers, VPS, home servers with port forwarding
- HTTPS strongly recommended for internet deployment
- Use strong passwords for all files when deploying to internet

## 📱 Mobile Usage

The application is optimized for mobile devices:
- Responsive design that works on all screen sizes
- Touch-friendly interface
- QR code generation for easy sharing
- Camera integration for QR code scanning

## 🔍 API Endpoints

- `GET /` - Main upload interface
- `POST /upload` - Upload a file and get download link
- `GET /download/{token}` - Download a file by token
- `GET /status` - Server status and statistics

## 🐛 Troubleshooting

### Can't access from other devices
- Make sure all devices are on the same Wi-Fi network
- Check if firewall is blocking the connection
- Try accessing using the exact IP address shown by the server

### Upload fails
- Check file size (very large files may cause memory issues)
- Ensure stable network connection
- Try refreshing the page and uploading again

### QR code not working
- Make sure the camera app supports QR code scanning
- Try copying the link manually instead
- Ensure the receiving device is on the same network

## 📏 File Size Limits

- **Maximum file size**: 100 MB per file (configurable)
- **Total memory limit**: 500 MB for all files (configurable)
- **File expiry**: 1 hour automatic cleanup
- **Configurable via environment variables**: `MAX_FILE_SIZE` and `MAX_TOTAL_MEMORY`

See [FILE_LIMITS.md](FILE_LIMITS.md) for detailed information and configuration options.

## 🚧 Limitations

- Files are stored in memory (RAM) for security and speed
- File size limits prevent memory exhaustion
- Files expire after 1 hour for security
- Server must stay running for downloads to work

## 🔮 Future Enhancements

- [ ] Multiple file upload support
- [ ] Password protection for files
- [ ] Custom expiry times
- [ ] File preview capabilities
- [ ] Upload progress for large files
- [ ] Docker containerization
- [ ] Standalone executable builds

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Made with ❤️ for easy local file sharing**
