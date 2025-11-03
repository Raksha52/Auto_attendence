<<<<<<< HEAD
# Face Recognition Auto Attendance System

A comprehensive face recognition-based attendance system with dual WiFi connectivity for classroom management.

## Features

- **Teacher Authentication**: Secure login system for teachers
- **Subject Management**: Manage multiple subjects (3-5 subjects supported)
- **Student Management**: Add and manage students for each subject
- **Face Recognition**: Automatic attendance marking using face recognition
- **Dual WiFi System**: Connect to classroom WiFi for dual system operation
- **Real-time Attendance**: Start/stop attendance sessions with live monitoring
- **Absence Tracking**: Generate absence lists and reports
- **Modern UI**: Beautiful, responsive web interface

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
=======
# Auto Attendance System

A comprehensive face recognition-based attendance system with student login portal, real-time face detection, anti-spoofing measures, and automated attendance marking.

## 🚀 Features

### 1️⃣ Live Video Capture
- Webcam integration for real-time video capture
- CPU-optimized processing (every 2-3 frames)
- High-quality image capture for face recognition

### 2️⃣ Face Detection (YOLOv8 Ready)
- Real-time face detection in video streams
- Bounding box output for detected faces
- Optimized for 2-5 FPS on CPU (sufficient for attendance)

### 3️⃣ Anti-Spoofing / Liveness Check
- Texture analysis using LBP, histogram, and edge detection
- Blink and head movement verification (optional)
- Configurable threshold for liveness detection
- Only live faces proceed to recognition phase

### 4️⃣ Face Recognition (FaceNet Compatible)
- 128-dimensional face embeddings
- Pre-stored student database comparison
- High-accuracy student identification
- Real-time recognition with confidence scoring

### 5️⃣ Student Login Portal
- Modern, responsive web interface
- Dual authentication: Password + Face Recognition
- Session management with secure tokens
- Real-time form validation and feedback

### 6️⃣ Attendance Management
- Automated attendance marking for recognized students
- Session-based attendance rules (once per class/day)
- Audit trail with snapshots and timestamps
- Real-time attendance status updates

### 7️⃣ Report Generation
- CSV/Excel export functionality
- Comprehensive attendance reports
- Student-wise and session-wise analytics
- Historical data tracking

## 🛠️ Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with animations
- **JavaScript (ES6+)** - Interactive functionality
- **Font Awesome** - Icons and UI elements

### Backend
- **Python Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **OpenCV** - Computer vision processing
- **NumPy** - Numerical computations
- **Pillow** - Image processing

### Database
- **SQLite** - Lightweight database (development)
- **PostgreSQL** - Production-ready database (optional)

### Face Recognition
- **OpenCV** - Face detection
- **FaceNet** - Face embeddings (ready for integration)
- **Custom Anti-spoofing** - Liveness detection

## 📁 Project Structure

```
Auto_Attendance_System/
├── index.html              # Student login page
├── styles.css              # Login page styling
├── script.js               # Login page functionality
├── dashboard.html          # Student dashboard
├── dashboard.css           # Dashboard styling
├── dashboard.js            # Dashboard functionality
├── app.py                  # Flask backend application
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser with camera support
- Webcam or connected camera

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Auto_Attendance_System
   ```

2. **Install Python dependencies**
>>>>>>> a43efd88c1abf46e3eb56fc98ca023036932b734
   ```bash
   pip install -r requirements.txt
   ```

<<<<<<< HEAD
3. **Set up environment variables** (optional):
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key-here
   ```

4. **Run the application**:
=======
3. **Run the Flask application**
>>>>>>> a43efd88c1abf46e3eb56fc98ca023036932b734
   ```bash
   python app.py
   ```

<<<<<<< HEAD
5. **Access the system**:
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Default login: username=`admin`, password=`admin123`

## Usage

### 1. Teacher Login
- Register a new teacher account or use the default admin account
- Secure authentication with password hashing

### 2. Subject Management
- Add subjects with names and codes
- Each teacher can manage their own subjects
- Support for 3-5 subjects as requested

### 3. Student Management
- Add students to each subject
- Upload face photos for face recognition
- Manage student roll numbers and details

### 4. Attendance Taking
- Start attendance session with face recognition
- Real-time video feed with face detection
- Automatic marking of present students
- Manual override for corrections
- Stop attendance session when complete

### 5. Absence Management
- View absence list for each subject
- Export absence reports
- Send notifications to absent students
- Track attendance history

## System Requirements

- Python 3.7+
- Webcam for face recognition
- WiFi connectivity for dual system operation
- Modern web browser

## Technical Details

- **Backend**: Flask (Python)
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Face Recognition**: OpenCV + face_recognition library
- **Frontend**: Bootstrap 5 + JavaScript
- **Authentication**: Flask-Login with password hashing

## WiFi Dual System

The system is designed to work with dual WiFi connectivity:
- Primary system connects to classroom WiFi
- Secondary system can connect to backup network
- Automatic failover between systems
- Real-time status monitoring

## Face Recognition Process

1. Students position themselves in front of camera
2. System detects faces in real-time
3. Compares detected faces with registered student faces
4. Automatically marks recognized students as present
5. Updates attendance database in real-time

## Security Features

- Password hashing for teacher accounts
- Session management with Flask-Login
- Secure face data storage
- Input validation and sanitization

## Troubleshooting

### Common Issues:

1. **Camera not working**:
   - Check camera permissions
   - Ensure camera is not used by other applications
   - Try different camera index in code

2. **Face recognition not working**:
   - Ensure students have uploaded face photos
   - Check lighting conditions
   - Verify face_recognition library installation

3. **WiFi connectivity issues**:
   - Check network configuration
   - Verify dual system setup
   - Monitor connection status in dashboard

## Support

For technical support or feature requests, please contact the development team.

## License

This project is developed for educational purposes. Please ensure compliance with privacy laws when handling student data.
=======
4. **Open the application**
   - Navigate to `http://localhost:5000` in your browser
   - Or open `index.html` directly for frontend-only testing

### Default Login Credentials

The system comes with sample student accounts:

| Student ID | Password    | Name         |
|------------|-------------|--------------|
| STU001     | password123 | John Doe     |
| STU002     | password123 | Jane Smith   |
| STU003     | password123 | Mike Johnson |

## 🎯 Usage Guide

### Student Login

1. **Password Login**
   - Enter your Student ID and password
   - Click "Login" to authenticate
   - Option to remember login session

2. **Face Recognition Login**
   - Click "Login with Face Recognition"
   - Allow camera permissions when prompted
   - Position your face within the frame
   - System will automatically capture and recognize

### Dashboard Features

1. **Attendance Sessions**
   - View active attendance sessions
   - Mark attendance with one click
   - Real-time session status updates

2. **Face Registration**
   - Register your face for quick login
   - Update existing face registration
   - View registration status

3. **Attendance History**
   - View recent attendance records
   - Track attendance methods used
   - Monitor attendance patterns

## 🔧 Configuration

### Face Recognition Settings

Edit `app.py` to configure face recognition parameters:

```python
# Face recognition confidence threshold
FACE_RECOGNITION_THRESHOLD = 0.7

# Anti-spoofing sensitivity
ANTI_SPOOFING_THRESHOLD = 0.5

# Face embedding dimensions
EMBEDDING_DIMENSIONS = 128
```

### Session Management

Configure session timeouts in `app.py`:

```python
# Session duration (hours)
SESSION_DURATION = 8
REMEMBER_ME_DURATION = 24
```

## 🔒 Security Features

- **Password Hashing** - Secure password storage using Werkzeug
- **Session Tokens** - Cryptographically secure session management
- **Anti-Spoofing** - Prevents photo/video spoofing attacks
- **Input Validation** - Comprehensive form validation
- **CORS Protection** - Cross-origin request security
- **SQL Injection Prevention** - Parameterized queries

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - Password-based login
- `POST /api/auth/face-login` - Face recognition login
- `POST /api/auth/logout` - Logout and session invalidation
- `GET /api/auth/verify-session` - Session verification

### Attendance
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance/sessions` - Get active sessions

### Student Management
- `POST /api/students/register-face` - Register face for recognition

### System
- `GET /api/health` - Health check endpoint

## 🧪 Testing

### Manual Testing
1. Test login with valid/invalid credentials
2. Test face recognition with different lighting conditions
3. Test anti-spoofing with photos vs live faces
4. Test session timeout and renewal
5. Test attendance marking and history

### Sample Test Data
The system includes sample data for testing:
- 3 sample students with known credentials
- 1 active attendance session
- Mock face recognition responses

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://user:pass@host/db
```

## 🔮 Future Enhancements

- [ ] YOLOv8 integration for improved face detection
- [ ] FaceNet model integration for better recognition
- [ ] Real-time attendance analytics dashboard
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Advanced anti-spoofing techniques
- [ ] Integration with existing student management systems
- [ ] Cloud deployment with AWS/Azure
- [ ] Real-time notifications
- [ ] Advanced reporting and analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- Flask community for the web framework
- Font Awesome for the icon library
- All contributors and testers

---

**Note**: This system is designed for educational and demonstration purposes. For production use, ensure proper security measures, data encryption, and compliance with privacy regulations.
>>>>>>> a43efd88c1abf46e3eb56fc98ca023036932b734
