# 🌐 Internet Deployment Guide

This guide will help you deploy your Secure File Share application to the internet so you can access it from anywhere.

## 🚀 Quick Internet Deployment Options

### Option 1: Cloud Server (Recommended)

#### Using a VPS (DigitalOcean, Linode, AWS EC2, etc.)

1. **Create a cloud server**
   ```bash
   # Example for Ubuntu 20.04+
   sudo apt update
   sudo apt install python3 python3-pip git nginx certbot python3-certbot-nginx
   ```

2. **Clone and setup your application**
   ```bash
   git clone <your-repo-url>
   cd fileshare
   pip3 install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   export PORT=8000
   # Optional: Set custom admin password (if you re-enable admin auth)
   # export ADMIN_PASSWORD="your-secure-password"
   ```

4. **Run with production server**
   ```bash
   # Install gunicorn for production
   pip3 install gunicorn
   
   # Run the application
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

5. **Setup HTTPS with Nginx (Highly Recommended)**
   ```nginx
   # /etc/nginx/sites-available/fileshare
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   
   ```bash
   # Enable the site
   sudo ln -s /etc/nginx/sites-available/fileshare /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   
   # Get SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

### Option 2: Home Server with Port Forwarding

1. **Configure your router**
   - Access your router's admin panel (usually 192.168.1.1 or 192.168.0.1)
   - Find "Port Forwarding" or "Virtual Server" settings
   - Forward external port 8000 to your computer's local IP:8000

2. **Find your public IP**
   ```bash
   curl ifconfig.me
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Access from internet**
   - Your app will be available at: `http://YOUR_PUBLIC_IP:8000`

### Option 3: Tunneling Services (Quick Testing)

#### Using ngrok (Free tier available)
```bash
# Install ngrok from https://ngrok.com/
# Run your app locally
python main.py

# In another terminal
ngrok http 8000
```

#### Using Cloudflare Tunnel (Free)
```bash
# Install cloudflared
# Follow: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# Run your app locally
python main.py

# Create tunnel
cloudflared tunnel --url http://localhost:8000
```

## 🔒 Security Best Practices for Internet Deployment

### 1. Always Use HTTPS in Production
- **Why**: Protects file uploads and passwords from being intercepted
- **How**: Use Let's Encrypt with Nginx/Apache or Cloudflare

### 2. Strong File Passwords
- Use the password feature for all sensitive files
- Share passwords through different channels than the download link
- Use strong passwords (8+ characters, mixed case, numbers, symbols)

### 3. Environment Variables
```bash
# Set these in production
export PORT=8000
export PYTHONPATH=/path/to/your/app
```

### 4. Firewall Configuration
```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 5. Process Management
```bash
# Install supervisor for process management
sudo apt install supervisor

# Create config file: /etc/supervisor/conf.d/fileshare.conf
[program:fileshare]
command=gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000
directory=/path/to/your/fileshare
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/fileshare.log
```

## 🛡️ Security Considerations

### File Password Protection
- **Per-file passwords**: Each file can have its own password
- **URL format**: `https://yourdomain.com/download/TOKEN?password=PASSWORD`
- **Best practice**: Share link and password separately

### Rate Limiting (Optional)
Consider adding rate limiting for production:
```python
# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add to upload endpoint
@limiter.limit("10/minute")
@app.post("/upload")
async def upload_file(request: Request, ...):
```

## 📊 Monitoring and Logs

### Basic Logging
```python
# Add to main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fileshare.log'),
        logging.StreamHandler()
    ]
)
```

### Health Check Endpoint
The `/status` endpoint provides server health information.

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find what's using the port
   sudo lsof -i :8000
   # Kill the process or use a different port
   ```

2. **Permission denied**
   ```bash
   # Make sure your user has permission to bind to the port
   # For ports < 1024, you need root privileges
   ```

3. **Files not accessible from internet**
   - Check firewall settings
   - Verify port forwarding configuration
   - Ensure the app binds to 0.0.0.0, not 127.0.0.1

4. **HTTPS certificate issues**
   ```bash
   # Renew Let's Encrypt certificates
   sudo certbot renew
   ```

## 📱 Mobile Access

The application is fully responsive and works great on mobile devices:
- Touch-friendly interface
- QR code generation for easy sharing
- Camera integration for QR scanning

## 🎯 Production Checklist

- [ ] HTTPS enabled
- [ ] Strong passwords for sensitive files
- [ ] Firewall configured
- [ ] Process manager setup (supervisor/systemd)
- [ ] Regular backups of configuration
- [ ] Monitoring and logging enabled
- [ ] Rate limiting configured (optional)
- [ ] Domain name configured
- [ ] SSL certificate auto-renewal setup

---

**⚠️ Important**: This application stores files in memory. For production use with large files or high traffic, consider implementing disk storage or cloud storage backends.
