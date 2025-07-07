// DOM elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const uploadBtn = document.getElementById('uploadBtn');
const uploadForm = document.getElementById('uploadForm');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

let selectedFile = null;
let maxFileSize = 0; // Will be loaded from server

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showFileInfo(file) {
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    // Check file size limit
    if (maxFileSize > 0 && file.size > maxFileSize) {
        fileName.style.color = '#ef4444';
        fileSize.style.color = '#ef4444';
        uploadBtn.disabled = true;

        // Show error message
        const errorMsg = document.createElement('div');
        errorMsg.className = 'file-error';
        errorMsg.innerHTML = `⚠️ File too large! Maximum size is ${formatFileSize(maxFileSize)}`;
        fileInfo.appendChild(errorMsg);
    } else {
        fileName.style.color = '';
        fileSize.style.color = '';
        uploadBtn.disabled = false;

        // Remove any existing error message
        const existingError = fileInfo.querySelector('.file-error');
        if (existingError) {
            existingError.remove();
        }
    }

    fileInfo.style.display = 'flex';

    // Hide drop zone content and show file info
    dropZone.style.padding = '20px';
    dropZone.querySelector('.drop-zone-content').style.display = 'none';
}

function hideFileInfo() {
    selectedFile = null;
    fileInfo.style.display = 'none';
    uploadBtn.disabled = true;
    fileInput.value = '';
    
    // Show drop zone content
    dropZone.style.padding = '60px 20px';
    dropZone.querySelector('.drop-zone-content').style.display = 'block';
}

function showProgress() {
    progressContainer.style.display = 'block';
    uploadBtn.querySelector('.btn-text').style.display = 'none';
    uploadBtn.querySelector('.spinner').style.display = 'block';
    uploadBtn.disabled = true;
}

function hideProgress() {
    progressContainer.style.display = 'none';
    uploadBtn.querySelector('.btn-text').style.display = 'block';
    uploadBtn.querySelector('.spinner').style.display = 'none';
    uploadBtn.disabled = false;
}

// Event listeners
dropZone.addEventListener('click', () => {
    if (!selectedFile) {
        fileInput.click();
    }
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        showFileInfo(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        showFileInfo(e.target.files[0]);
    }
});

removeFile.addEventListener('click', () => {
    hideFileInfo();
});

// Form submission with progress
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }
    
    showProgress();
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const xhr = new XMLHttpRequest();
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressFill.style.width = percentComplete + '%';
                progressText.textContent = `Uploading... ${Math.round(percentComplete)}%`;
            }
        });
        
        // Handle completion
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                // Redirect to success page
                document.body.innerHTML = xhr.responseText;
            } else {
                throw new Error('Upload failed');
            }
        });
        
        // Handle errors
        xhr.addEventListener('error', () => {
            throw new Error('Network error');
        });
        
        // Start upload
        xhr.open('POST', '/upload');
        xhr.send(formData);
        
    } catch (error) {
        console.error('Upload error:', error);
        alert('Upload failed. Please try again.');
        hideProgress();
    }
});

// Prevent default drag behaviors on the document
document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
});

// Auto-focus on file input for better accessibility
document.addEventListener('DOMContentLoaded', () => {
    // Add keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.target === dropZone) {
            fileInput.click();
        }
    });
    
    // Make drop zone focusable
    dropZone.setAttribute('tabindex', '0');
    dropZone.setAttribute('role', 'button');
    dropZone.setAttribute('aria-label', 'Click to select file or drag and drop');

    // Password functionality
    const passwordInput = document.getElementById('filePassword');
    const togglePassword = document.getElementById('togglePassword');
    const passwordStrength = document.getElementById('passwordStrength');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');

    // Toggle password visibility
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            togglePassword.textContent = type === 'password' ? '👁️' : '🙈';
        });
    }

    // Password strength checker
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            if (password.length === 0) {
                passwordStrength.style.display = 'none';
                return;
            }

            passwordStrength.style.display = 'block';
            const strength = calculatePasswordStrength(password);
            updatePasswordStrength(strength);
        });
    }

    function calculatePasswordStrength(password) {
        let score = 0;
        let feedback = '';

        if (password.length >= 8) score += 25;
        if (password.length >= 12) score += 25;
        if (/[a-z]/.test(password)) score += 10;
        if (/[A-Z]/.test(password)) score += 10;
        if (/[0-9]/.test(password)) score += 10;
        if (/[^A-Za-z0-9]/.test(password)) score += 20;

        if (score < 30) {
            feedback = 'Weak';
        } else if (score < 60) {
            feedback = 'Fair';
        } else if (score < 80) {
            feedback = 'Good';
        } else {
            feedback = 'Strong';
        }

        return { score, feedback };
    }

    function updatePasswordStrength(strength) {
        const colors = {
            'Weak': '#ef4444',
            'Fair': '#f59e0b',
            'Good': '#10b981',
            'Strong': '#059669'
        };

        strengthFill.style.width = Math.min(strength.score, 100) + '%';
        strengthFill.style.backgroundColor = colors[strength.feedback];
        strengthText.textContent = strength.feedback;
        strengthText.style.color = colors[strength.feedback];
    }

    // Load server limits
    async function loadServerLimits() {
        try {
            const response = await fetch('/status');
            if (response.ok) {
                const data = await response.json();
                maxFileSize = data.file_limits.max_file_size_bytes;

                // Update the UI
                const maxFileSizeElement = document.getElementById('maxFileSize');
                if (maxFileSizeElement) {
                    maxFileSizeElement.textContent = data.file_limits.max_file_size_formatted;
                }
            }
        } catch (error) {
            console.error('Failed to load server limits:', error);
        }
    }

    // Load limits when page loads
    loadServerLimits();
});
