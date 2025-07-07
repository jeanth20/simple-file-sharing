import asyncio
import os
import socket
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Dict, Any, Optional

import qrcode
from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# In-memory storage for files
files: Dict[str, Dict[str, Any]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup: Start background cleanup task
    async def cleaner():
        while True:
            try:
                now = datetime.now(timezone.utc)
                expired_tokens = [
                    token for token, file_data in files.items()
                    if file_data["expires_at"] < now
                ]
                for token in expired_tokens:
                    del files[token]
                    print(f"Cleaned up expired file: {token}")
            except Exception as e:
                print(f"Error in cleanup task: {e}")

            await asyncio.sleep(60)  # Check every minute

    cleanup_task = asyncio.create_task(cleaner())

    yield  # Application runs here

    # Shutdown: Cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Secure File Share",
    description="Share files securely with password protection",
    lifespan=lifespan
)

# Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 100 * 1024 * 1024))  # 100MB default
MAX_TOTAL_MEMORY = int(os.getenv("MAX_TOTAL_MEMORY", 500 * 1024 * 1024))  # 500MB default

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def get_total_memory_usage() -> int:
    """Calculate total memory usage of stored files"""
    return sum(file_data["size"] for file_data in files.values())

def check_memory_limits(new_file_size: int) -> None:
    """Check if adding a new file would exceed memory limits"""
    current_memory = get_total_memory_usage()

    if new_file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum file size is {format_file_size(MAX_FILE_SIZE)}"
        )

    if current_memory + new_file_size > MAX_TOTAL_MEMORY:
        raise HTTPException(
            status_code=507,
            detail=f"Server memory full. Total memory limit is {format_file_size(MAX_TOTAL_MEMORY)}. "
                   f"Current usage: {format_file_size(current_memory)}"
        )

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def get_server_url(request: Request) -> str:
    """Get the server URL (handles both local and internet access)"""
    # Check if we're being accessed via a public domain/IP
    host = request.headers.get("host", "")
    if "localhost" in host or "127.0.0.1" in host:
        # Local access - use local IP
        local_ip = get_local_ip()
        return f"http://{local_ip}:8000"
    else:
        # Internet access - use the host from the request
        scheme = "https" if request.headers.get("x-forwarded-proto") == "https" else "http"
        return f"{scheme}://{host}"

def generate_qr_code(url: str) -> str:
    """Generate QR code for the given URL and return as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    import base64
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with file upload form"""
    server_url = get_server_url(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "server_url": server_url,
        "password_protected": False  # No page-level protection, only per-file
    })

@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    file_password: Optional[str] = Form(None)
):
    """Upload a file and return download link"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    # Debug: Log the received password
    print(f"DEBUG: Received file_password: '{file_password}' (type: {type(file_password)})")

    # Read file content first to check size
    content = await file.read()
    file_size = len(content)

    # Check file size and memory limits
    check_memory_limits(file_size)

    # Generate unique token
    token = str(uuid.uuid4())

    # Store file in memory with metadata
    files[token] = {
        "owner_ip": request.client.host,
        "filename": file.filename,
        "content": content,
        "content_type": file.content_type or "application/octet-stream",
        "size": file_size,
        "uploaded_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),  # Expire in 1 hour
        "file_password": file_password  # Optional password for this specific file
    }

    # Generate download URL and QR code
    server_url = get_server_url(request)
    download_url = f"{server_url}/download/{token}"
    qr_code = generate_qr_code(download_url)

    return templates.TemplateResponse("success.html", {
        "request": request,
        "filename": file.filename,
        "download_url": download_url,
        "qr_code": qr_code,
        "file_size": file_size,
        "expires_at": files[token]["expires_at"].strftime("%Y-%m-%d %H:%M:%S UTC"),
        "has_file_password": bool(file_password),
        "server_url": server_url
    })

@app.get("/download/{token}")
async def download_file(token: str, password: Optional[str] = None):
    """Download a file by token"""
    if token not in files:
        raise HTTPException(status_code=404, detail="File not found or expired")

    file_data = files[token]

    # Check if file has expired
    if file_data["expires_at"] < datetime.now(timezone.utc):
        del files[token]
        raise HTTPException(status_code=404, detail="File has expired")

    # Check file-specific password if set
    if file_data.get("file_password") and password != file_data["file_password"]:
        raise HTTPException(
            status_code=401,
            detail="File password required. Add ?password=YOUR_PASSWORD to the URL"
        )

    # Create streaming response
    def generate():
        yield file_data["content"]

    return StreamingResponse(
        generate(),
        media_type=file_data["content_type"],
        headers={
            "Content-Disposition": f"attachment; filename={file_data['filename']}",
            "Content-Length": str(file_data["size"])
        }
    )

@app.get("/status")
async def get_status(request: Request):
    """Get server status and active files count"""
    active_files = len(files)
    server_url = get_server_url(request)
    memory_usage = get_total_memory_usage()

    return {
        "status": "running",
        "server_url": server_url,
        "active_files": active_files,
        "memory_usage": {
            "current_bytes": memory_usage,
            "current_formatted": format_file_size(memory_usage),
            "max_bytes": MAX_TOTAL_MEMORY,
            "max_formatted": format_file_size(MAX_TOTAL_MEMORY),
            "usage_percentage": round((memory_usage / MAX_TOTAL_MEMORY) * 100, 1)
        },
        "file_limits": {
            "max_file_size_bytes": MAX_FILE_SIZE,
            "max_file_size_formatted": format_file_size(MAX_FILE_SIZE)
        },
        "server_time": datetime.now(timezone.utc).isoformat(),
        "password_protected": False  # No page-level protection
    }

if __name__ == "__main__":
    import uvicorn
    local_ip = get_local_ip()
    port = int(os.getenv("PORT", 8000))

    print("🚀 Secure File Share Server Starting...")
    print("=" * 50)
    print(f"Local Network: http://{local_ip}:{port}")
    print("Security: Per-file password protection available")
    print(f"File Limits: Max {format_file_size(MAX_FILE_SIZE)} per file, {format_file_size(MAX_TOTAL_MEMORY)} total")
    print("=" * 50)
    print("For internet access:")
    print("1. Configure your router/firewall to forward port", port)
    print("2. Use your public IP or domain name")
    print("3. Consider using HTTPS in production (recommended)")
    print("4. Set strong passwords for sensitive files")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=port)
