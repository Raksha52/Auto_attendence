// Global variables
let currentUser = null;
let videoStream = null;
let isRegistrationActive = false;
let registrationInProgress = false;

// DOM elements
const userName = document.getElementById('userName');
const userId = document.getElementById('userId');
const welcomeName = document.getElementById('welcomeName');
const totalAttendance = document.getElementById('totalAttendance');
const attendanceRate = document.getElementById('attendanceRate');
const sessionsGrid = document.getElementById('sessionsGrid');
const faceStatus = document.getElementById('faceStatus');
const registerFaceBtn = document.getElementById('registerFaceBtn');
const attendanceTableBody = document.getElementById('attendanceTableBody');
const faceRegistrationModal = document.getElementById('faceRegistrationModal');
const messageContainer = document.getElementById('messageContainer');

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
    initializeEventListeners();
});

// Event Listeners
function initializeEventListeners() {
    // Close modal on outside click
    faceRegistrationModal.addEventListener('click', function(e) {
        if (e.target === faceRegistrationModal) {
            closeFaceRegistration();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Authentication and Session Management
async function checkAuthentication() {
    const session = localStorage.getItem('studentSession');
    
    if (!session) {
        redirectToLogin();
        return;
    }
    
    try {
        const sessionData = JSON.parse(session);
        const sessionAge = Date.now() - sessionData.timestamp;
        const maxAge = 24 * 60 * 60 * 1000; // 24 hours
        
        if (sessionAge > maxAge) {
            localStorage.removeItem('studentSession');
            redirectToLogin();
            return;
        }
        
        // Verify session with server
        const response = await fetch(`${API_BASE_URL}/auth/verify-session`, {
            headers: {
                'Authorization': `Bearer ${sessionData.session_token || 'mock_token'}`
            }
        });
        
        if (!response.ok) {
            localStorage.removeItem('studentSession');
            redirectToLogin();
            return;
        }
        
        const data = await response.json();
        currentUser = data.student;
        
        // Update UI with user data
        updateUserInfo();
        loadDashboardData();
        
    } catch (error) {
        console.error('Authentication check failed:', error);
        redirectToLogin();
    }
}

function updateUserInfo() {
    if (currentUser) {
        userName.textContent = currentUser.name;
        userId.textContent = currentUser.student_id;
        welcomeName.textContent = currentUser.name;
    }
}

function redirectToLogin() {
    window.location.href = 'index.html';
}

// Dashboard Data Loading
async function loadDashboardData() {
    try {
        await Promise.all([
            loadAttendanceStats(),
            loadActiveSessions(),
            checkFaceRegistrationStatus(),
            loadRecentAttendance()
        ]);
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showMessage('Failed to load dashboard data', 'error');
    }
}

async function loadAttendanceStats() {
    try {
        // Mock data - replace with actual API call
        const mockStats = {
            totalAttendance: 45,
            attendanceRate: 92
        };
        
        totalAttendance.textContent = mockStats.totalAttendance;
        attendanceRate.textContent = `${mockStats.attendanceRate}%`;
        
    } catch (error) {
        console.error('Failed to load attendance stats:', error);
    }
}

async function loadActiveSessions() {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/sessions`);
        const data = await response.json();
        
        if (data.success) {
            displaySessions(data.sessions);
        } else {
            throw new Error(data.message);
        }
        
    } catch (error) {
        console.error('Failed to load sessions:', error);
        displaySessions([]);
    }
}

function displaySessions(sessions) {
    if (sessions.length === 0) {
        sessionsGrid.innerHTML = `
            <div class="no-sessions">
                <i class="fas fa-calendar-times"></i>
                <p>No active attendance sessions</p>
            </div>
        `;
        return;
    }
    
    sessionsGrid.innerHTML = sessions.map(session => `
        <div class="session-card">
            <div class="session-header">
                <span class="session-name">${session.session_name}</span>
                <span class="session-status ${session.is_active ? 'active' : 'inactive'}">
                    ${session.is_active ? 'Active' : 'Inactive'}
                </span>
            </div>
            <div class="session-time">
                <i class="fas fa-clock"></i>
                ${formatTimeRange(session.start_time, session.end_time)}
            </div>
            <button class="mark-attendance-btn" 
                    onclick="markAttendance(${session.id})"
                    ${!session.is_active ? 'disabled' : ''}>
                <i class="fas fa-check-circle"></i>
                Mark Attendance
            </button>
        </div>
    `).join('');
}

async function checkFaceRegistrationStatus() {
    try {
        // Mock check - replace with actual API call
        const isRegistered = Math.random() > 0.5; // Random for demo
        
        if (isRegistered) {
            faceStatus.innerHTML = `
                <i class="fas fa-check-circle"></i>
                Face registered
            `;
            faceStatus.className = 'status-indicator registered';
            registerFaceBtn.textContent = 'Update Face Registration';
        } else {
            faceStatus.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                Face not registered
            `;
            faceStatus.className = 'status-indicator not-registered';
            registerFaceBtn.textContent = 'Register Face';
        }
        
    } catch (error) {
        console.error('Failed to check face registration status:', error);
        faceStatus.innerHTML = `
            <i class="fas fa-question-circle"></i>
            Status unknown
        `;
        faceStatus.className = 'status-indicator checking';
    }
}

async function loadRecentAttendance() {
    try {
        // Mock data - replace with actual API call
        const mockAttendance = [
            {
                date: '2024-01-15',
                session: 'Morning Class',
                time: '09:00 AM',
                method: 'face',
                status: 'present'
            },
            {
                date: '2024-01-14',
                session: 'Afternoon Class',
                time: '02:00 PM',
                method: 'password',
                status: 'present'
            },
            {
                date: '2024-01-13',
                session: 'Morning Class',
                time: '09:15 AM',
                method: 'face',
                status: 'late'
            }
        ];
        
        displayRecentAttendance(mockAttendance);
        
    } catch (error) {
        console.error('Failed to load recent attendance:', error);
        attendanceTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="loading-row">
                    <i class="fas fa-exclamation-triangle"></i>
                    Failed to load attendance records
                </td>
            </tr>
        `;
    }
}

function displayRecentAttendance(attendanceRecords) {
    if (attendanceRecords.length === 0) {
        attendanceTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="loading-row">
                    <i class="fas fa-calendar-times"></i>
                    No attendance records found
                </td>
            </tr>
        `;
        return;
    }
    
    attendanceTableBody.innerHTML = attendanceRecords.map(record => `
        <tr>
            <td>${formatDate(record.date)}</td>
            <td>${record.session}</td>
            <td>${record.time}</td>
            <td>
                <span class="attendance-method ${record.method}">
                    <i class="fas fa-${record.method === 'face' ? 'camera' : 'key'}"></i>
                    ${record.method === 'face' ? 'Face' : 'Password'}
                </span>
            </td>
            <td>
                <span class="attendance-status ${record.status}">
                    ${record.status === 'present' ? 'Present' : 'Late'}
                </span>
            </td>
        </tr>
    `).join('');
}

// Attendance Marking
async function markAttendance(sessionId) {
    try {
        const session = localStorage.getItem('studentSession');
        const sessionData = JSON.parse(session);
        
        const response = await fetch(`${API_BASE_URL}/attendance/mark`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionData.session_token || 'mock_token'}`
            },
            body: JSON.stringify({
                sessionId: sessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Attendance marked successfully!', 'success');
            // Reload sessions to update UI
            loadActiveSessions();
        } else {
            showMessage(data.message || 'Failed to mark attendance', 'error');
        }
        
    } catch (error) {
        console.error('Failed to mark attendance:', error);
        showMessage('Failed to mark attendance. Please try again.', 'error');
    }
}

// Face Registration
async function openFaceRegistration() {
    try {
        isRegistrationActive = true;
        faceRegistrationModal.style.display = 'block';
        
        // Request camera access
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });
        
        const video = document.getElementById('registrationVideo');
        video.srcObject = videoStream;
        
        updateRegistrationStatus('Camera ready. Position your face in the frame.', 'info');
        document.getElementById('registrationCaptureBtn').disabled = false;
        
    } catch (error) {
        console.error('Camera access error:', error);
        updateRegistrationStatus('Camera access denied. Please allow camera permissions.', 'error');
        showMessage('Camera access is required for face registration.', 'error');
    }
}

async function captureForRegistration() {
    if (registrationInProgress) return;
    
    registrationInProgress = true;
    const captureBtn = document.getElementById('registrationCaptureBtn');
    captureBtn.disabled = true;
    
    try {
        updateRegistrationStatus('Capturing image...', 'info');
        updateRegistrationProgress(20);
        
        // Capture frame
        const video = document.getElementById('registrationVideo');
        const canvas = document.getElementById('registrationCanvas');
        const context = canvas.getContext('2d');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        
        updateRegistrationStatus('Processing face detection...', 'info');
        updateRegistrationProgress(40);
        
        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateRegistrationStatus('Extracting face features...', 'info');
        updateRegistrationProgress(60);
        
        // Simulate feature extraction delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateRegistrationStatus('Saving face data...', 'info');
        updateRegistrationProgress(80);
        
        // Register face with server
        const session = localStorage.getItem('studentSession');
        const sessionData = JSON.parse(session);
        
        const response = await fetch(`${API_BASE_URL}/students/register-face`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionData.session_token || 'mock_token'}`
            },
            body: JSON.stringify({
                imageData: imageData
            })
        });
        
        const data = await response.json();
        
        updateRegistrationProgress(100);
        
        if (data.success) {
            updateRegistrationStatus('Face registered successfully!', 'success');
            showMessage('Face registration completed successfully!', 'success');
            
            // Update face registration status
            setTimeout(() => {
                closeFaceRegistration();
                checkFaceRegistrationStatus();
            }, 2000);
        } else {
            updateRegistrationStatus(data.message || 'Face registration failed', 'error');
            showMessage('Face registration failed. Please try again.', 'error');
            
            // Reset for retry
            setTimeout(() => {
                registrationInProgress = false;
                captureBtn.disabled = false;
                updateRegistrationProgress(0);
                updateRegistrationStatus('Ready to capture. Position your face in the frame.', 'info');
            }, 3000);
        }
        
    } catch (error) {
        console.error('Face registration error:', error);
        updateRegistrationStatus('Registration failed. Please try again.', 'error');
        showMessage('Face registration error. Please try again.', 'error');
        
        setTimeout(() => {
            registrationInProgress = false;
            captureBtn.disabled = false;
            updateRegistrationProgress(0);
        }, 2000);
    }
}

function closeFaceRegistration() {
    isRegistrationActive = false;
    registrationInProgress = false;
    
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    
    faceRegistrationModal.style.display = 'none';
    const video = document.getElementById('registrationVideo');
    video.srcObject = null;
    updateRegistrationProgress(0);
    document.getElementById('registrationCaptureBtn').disabled = true;
}

// Utility Functions
function updateRegistrationStatus(message, type = 'info') {
    const statusMessage = document.getElementById('registrationStatusMessage');
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

function updateRegistrationProgress(percentage) {
    const progress = document.getElementById('registrationProgress');
    progress.style.width = `${percentage}%`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTimeRange(startTime, endTime) {
    const start = new Date(startTime);
    const end = new Date(endTime);
    
    const startStr = start.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const endStr = end.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    return `${startStr} - ${endStr}`;
}

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

// Logout
async function logout() {
    try {
        const session = localStorage.getItem('studentSession');
        if (session) {
            const sessionData = JSON.parse(session);
            
            // Call logout API
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${sessionData.session_token || 'mock_token'}`
                }
            });
        }
        
        // Clear local session
        localStorage.removeItem('studentSession');
        
        // Redirect to login
        window.location.href = 'index.html';
        
    } catch (error) {
        console.error('Logout error:', error);
        // Still redirect even if logout API fails
        localStorage.removeItem('studentSession');
        window.location.href = 'index.html';
    }
}

// Keyboard shortcuts
function handleKeyboardShortcuts(e) {
    // Escape key to close modal
    if (e.key === 'Escape' && faceRegistrationModal.style.display === 'block') {
        closeFaceRegistration();
    }
    
    // Enter key to capture in registration modal
    if (e.key === 'Enter' && faceRegistrationModal.style.display === 'block') {
        e.preventDefault();
        const captureBtn = document.getElementById('registrationCaptureBtn');
        if (!captureBtn.disabled && !registrationInProgress) {
            captureForRegistration();
        }
    }
}

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        checkAuthentication,
        loadDashboardData,
        markAttendance,
        openFaceRegistration,
        captureForRegistration,
        formatDate,
        formatTimeRange
    };
}
