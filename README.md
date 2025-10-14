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
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask application**
   ```bash
   python app.py
   ```

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
