// Global variables
let videoStream = null;
let isFaceLoginActive = false;
let recognitionInProgress = false;

// DOM elements
const loginForm = document.getElementById('loginForm');
const faceModal = document.getElementById('faceModal');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const statusMessage = document.getElementById('statusMessage');
const progress = document.getElementById('progress');
const captureBtn = document.getElementById('captureBtn');
const messageContainer = document.getElementById('messageContainer');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkCameraPermissions();
});

// Event Listeners
function initializeEventListeners() {
    // Form submission
    loginForm.addEventListener('submit', handleFormSubmit);
    
    // Input validation
    const inputs = document.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
        input.addEventListener('input', clearInputError);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Close modal on outside click
    faceModal.addEventListener('click', function(e) {
        if (e.target === faceModal) {
            closeFaceModal();
        }
    });
}

// Form submission handler
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(loginForm);
    const loginData = {
        studentId: formData.get('studentId'),
        password: formData.get('password'),
        rememberMe: formData.get('rememberMe') === 'on'
    };
    
    // Validate form
    if (!validateForm(loginData)) {
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    
    try {
        const response = await authenticateStudent(loginData);
        
        if (response.success) {
            showMessage('Login successful! Redirecting...', 'success');
            
            // Store session data
            if (loginData.rememberMe) {
                localStorage.setItem('studentSession', JSON.stringify({
                    studentId: loginData.studentId,
                    timestamp: Date.now()
                }));
            }
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showMessage(response.message || 'Login failed. Please check your credentials.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('Network error. Please try again.', 'error');
    } finally {
        setLoadingState(false);
    }
}

// Face login functionality
async function initiateFaceLogin() {
    try {
        isFaceLoginActive = true;
        faceModal.style.display = 'block';
        
        // Request camera access
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });
        
        video.srcObject = videoStream;
        updateStatus('Camera ready. Position your face in the frame.', 'info');
        captureBtn.disabled = false;
        
        // Auto-capture after 3 seconds
        setTimeout(() => {
            if (isFaceLoginActive && !recognitionInProgress) {
                captureAndRecognize();
            }
        }, 3000);
        
    } catch (error) {
        console.error('Camera access error:', error);
        updateStatus('Camera access denied. Please allow camera permissions.', 'error');
        showMessage('Camera access is required for face login.', 'error');
    }
}

// Capture and recognize face
async function captureAndRecognize() {
    if (recognitionInProgress) return;
    
    recognitionInProgress = true;
    captureBtn.disabled = true;
    
    try {
        updateStatus('Capturing image...', 'info');
        updateProgress(20);
        
        // Capture frame
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        
        updateStatus('Processing face detection...', 'info');
        updateProgress(40);
        
        // Simulate face detection delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateStatus('Running anti-spoofing check...', 'info');
        updateProgress(60);
        
        // Simulate anti-spoofing delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateStatus('Generating face embeddings...', 'info');
        updateProgress(80);
        
        // Simulate face recognition delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateStatus('Matching with database...', 'info');
        updateProgress(100);
        
        // Perform face recognition
        const recognitionResult = await performFaceRecognition(imageData);
        
        if (recognitionResult.success) {
            updateStatus('Face recognized successfully!', 'success');
            showMessage(`Welcome, ${recognitionResult.studentName}!`, 'success');
            
            // Store session
            localStorage.setItem('studentSession', JSON.stringify({
                studentId: recognitionResult.studentId,
                studentName: recognitionResult.studentName,
                loginMethod: 'face',
                timestamp: Date.now()
            }));
            
            // Redirect after delay
            setTimeout(() => {
                closeFaceModal();
                window.location.href = 'dashboard.html';
            }, 2000);
        } else {
            updateStatus(recognitionResult.message || 'Face not recognized. Please try again.', 'error');
            showMessage('Face recognition failed. Please try again or use regular login.', 'error');
            
            // Reset for retry
            setTimeout(() => {
                recognitionInProgress = false;
                captureBtn.disabled = false;
                updateProgress(0);
                updateStatus('Ready to capture. Position your face in the frame.', 'info');
            }, 3000);
        }
        
    } catch (error) {
        console.error('Face recognition error:', error);
        updateStatus('Recognition failed. Please try again.', 'error');
        showMessage('Face recognition error. Please try again.', 'error');
        
        setTimeout(() => {
            recognitionInProgress = false;
            captureBtn.disabled = false;
            updateProgress(0);
        }, 2000);
    }
}

// Close face modal
function closeFaceModal() {
    isFaceLoginActive = false;
    recognitionInProgress = false;
    
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    
    faceModal.style.display = 'none';
    video.srcObject = null;
    updateProgress(0);
    captureBtn.disabled = true;
}

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        toggleIcon.className = 'fas fa-eye';
    }
}

// Form validation
function validateForm(data) {
    let isValid = true;
    
    // Student ID validation
    if (!data.studentId || data.studentId.trim().length < 3) {
        showInputError('studentId', 'Please enter a valid Student ID');
        isValid = false;
    }
    
    // Password validation
    if (!data.password || data.password.length < 6) {
        showInputError('password', 'Password must be at least 6 characters');
        isValid = false;
    }
    
    return isValid;
}

// Input validation
function validateInput(e) {
    const input = e.target;
    const value = input.value.trim();
    
    switch (input.id) {
        case 'studentId':
            if (value.length < 3) {
                showInputError(input.id, 'Student ID must be at least 3 characters');
            } else {
                clearInputError(input.id);
            }
            break;
            
        case 'password':
            if (value.length < 6) {
                showInputError(input.id, 'Password must be at least 6 characters');
            } else {
                clearInputError(input.id);
            }
            break;
    }
}

// Show input error
function showInputError(inputId, message) {
    const input = document.getElementById(inputId);
    const inputWrapper = input.closest('.input-wrapper');
    
    input.style.borderColor = '#dc3545';
    inputWrapper.style.position = 'relative';
    
    // Remove existing error message
    const existingError = inputWrapper.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        color: #dc3545;
        font-size: 12px;
        margin-top: 5px;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
    `;
    errorDiv.textContent = message;
    inputWrapper.appendChild(errorDiv);
}

// Clear input error
function clearInputError(inputId) {
    const input = document.getElementById(inputId);
    const inputWrapper = input.closest('.input-wrapper');
    const errorMessage = inputWrapper.querySelector('.error-message');
    
    input.style.borderColor = '#e1e5e9';
    if (errorMessage) {
        errorMessage.remove();
    }
}

// Set loading state
function setLoadingState(loading) {
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const spinner = loginBtn.querySelector('.spinner');
    
    if (loading) {
        loginBtn.classList.add('loading');
        loginBtn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'block';
    } else {
        loginBtn.classList.remove('loading');
        loginBtn.disabled = false;
        btnText.style.display = 'block';
        spinner.style.display = 'none';
    }
}

// Update status message
function updateStatus(message, type = 'info') {
    const icon = statusMessage.querySelector('i');
    const text = statusMessage.querySelector('span');
    
    // Update icon based on type
    switch (type) {
        case 'success':
            icon.className = 'fas fa-check-circle';
            statusMessage.style.color = '#28a745';
            break;
        case 'error':
            icon.className = 'fas fa-exclamation-circle';
            statusMessage.style.color = '#dc3545';
            break;
        case 'info':
        default:
            icon.className = 'fas fa-info-circle';
            statusMessage.style.color = '#17a2b8';
            break;
    }
    
    text.textContent = message;
}

// Update progress bar
function updateProgress(percentage) {
    progress.style.width = `${percentage}%`;
}

// Show message notification
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const icon = document.createElement('i');
    switch (type) {
        case 'success':
            icon.className = 'fas fa-check-circle';
            break;
        case 'error':
            icon.className = 'fas fa-exclamation-circle';
            break;
        case 'info':
        default:
            icon.className = 'fas fa-info-circle';
            break;
    }
    
    const text = document.createElement('span');
    text.textContent = message;
    
    messageDiv.appendChild(icon);
    messageDiv.appendChild(text);
    
    messageContainer.appendChild(messageDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 5000);
}

// Keyboard shortcuts
function handleKeyboardShortcuts(e) {
    // Enter key on form
    if (e.key === 'Enter' && !e.shiftKey) {
        if (faceModal.style.display === 'block') {
            e.preventDefault();
            if (!recognitionInProgress && captureBtn.disabled === false) {
                captureAndRecognize();
            }
        }
    }
    
    // Escape key to close modal
    if (e.key === 'Escape' && faceModal.style.display === 'block') {
        closeFaceModal();
    }
}

// Check camera permissions
async function checkCameraPermissions() {
    try {
        const permissions = await navigator.permissions.query({ name: 'camera' });
        if (permissions.state === 'denied') {
            console.warn('Camera permission denied');
        }
    } catch (error) {
        console.warn('Could not check camera permissions:', error);
    }
}

// API Functions (Mock implementations - replace with actual API calls)

// Authenticate student with credentials
async function authenticateStudent(loginData) {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock authentication - replace with actual API call
    const mockStudents = {
        'STU001': { password: 'password123', name: 'John Doe' },
        'STU002': { password: 'password123', name: 'Jane Smith' },
        'STU003': { password: 'password123', name: 'Mike Johnson' }
    };
    
    const student = mockStudents[loginData.studentId];
    
    if (student && student.password === loginData.password) {
        return {
            success: true,
            studentId: loginData.studentId,
            studentName: student.name
        };
    } else {
        return {
            success: false,
            message: 'Invalid Student ID or Password'
        };
    }
}

// Perform face recognition
async function performFaceRecognition(imageData) {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock face recognition - replace with actual API call
    // In real implementation, this would:
    // 1. Send image to face detection API
    // 2. Run anti-spoofing checks
    // 3. Generate face embeddings
    // 4. Compare with stored student faces
    // 5. Return recognition result
    
    const mockRecognitionResults = [
        { success: true, studentId: 'STU001', studentName: 'John Doe', confidence: 0.95 },
        { success: false, message: 'Face not recognized' },
        { success: true, studentId: 'STU002', studentName: 'Jane Smith', confidence: 0.92 }
    ];
    
    // Randomly return a result for demo purposes
    const randomResult = mockRecognitionResults[Math.floor(Math.random() * mockRecognitionResults.length)];
    
    return randomResult;
}

// Utility Functions

// Format date for display
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Check if user is already logged in
function checkExistingSession() {
    const session = localStorage.getItem('studentSession');
    if (session) {
        const sessionData = JSON.parse(session);
        const sessionAge = Date.now() - sessionData.timestamp;
        const maxAge = 24 * 60 * 60 * 1000; // 24 hours
        
        if (sessionAge < maxAge) {
            // Redirect to dashboard if session is still valid
            window.location.href = 'dashboard.html';
        } else {
            // Clear expired session
            localStorage.removeItem('studentSession');
        }
    }
}

// Initialize session check on page load
document.addEventListener('DOMContentLoaded', checkExistingSession);

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateForm,
        authenticateStudent,
        performFaceRecognition,
        formatDate,
        generateSessionId
    };
}
