from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import base64
import cv2
import numpy as np
from PIL import Image
import io
import json
import hashlib

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Database Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    face_embedding = db.Column(db.Text)  # JSON string of face embedding
    face_image_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AttendanceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_session.id'), nullable=False)
    attendance_time = db.Column(db.DateTime, default=datetime.utcnow)
    login_method = db.Column(db.String(20), nullable=False)  # 'password' or 'face'
    face_image_path = db.Column(db.String(255))
    confidence_score = db.Column(db.Float)
    is_verified = db.Column(db.Boolean, default=True)

    # Relationships
    student = db.relationship('Student', backref=db.backref('attendance_records', lazy=True))
    session = db.relationship('AttendanceSession', backref=db.backref('attendance_records', lazy=True))

class LoginSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    login_method = db.Column(db.String(20), nullable=False)

    student = db.relationship('Student', backref=db.backref('login_sessions', lazy=True))

# Face Recognition Helper Functions
class FaceRecognitionService:
    def __init__(self):
        # Initialize face detection and recognition models
        # In production, you would load pre-trained models here
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def detect_faces(self, image):
        """Detect faces in an image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces
    
    def extract_face_embedding(self, image, face_coords):
        """Extract face embedding for recognition"""
        x, y, w, h = face_coords
        face_roi = image[y:y+h, x:x+w]
        
        # In production, you would use a pre-trained model like FaceNet
        # For now, we'll create a mock embedding
        face_resized = cv2.resize(face_roi, (160, 160))
        embedding = np.random.rand(128)  # Mock 128-dimensional embedding
        
        return embedding
    
    def compare_embeddings(self, embedding1, embedding2, threshold=0.6):
        """Compare two face embeddings"""
        # Calculate cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        similarity = dot_product / (norm1 * norm2)
        return similarity > threshold, similarity
    
    def anti_spoofing_check(self, image, face_coords):
        """Perform anti-spoofing checks"""
        x, y, w, h = face_coords
        face_roi = image[y:y+h, x:x+w]
        
        # Convert to grayscale for analysis
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Simple texture analysis using Laplacian variance
        laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
        
        # Simple edge density analysis
        edges = cv2.Canny(gray_face, 50, 150)
        edge_density = np.sum(edges > 0) / (w * h)
        
        # Mock anti-spoofing score (in production, use more sophisticated methods)
        spoof_score = (laplacian_var / 1000) + (edge_density * 10)
        is_live = spoof_score > 0.5  # Threshold for live face
        
        return is_live, spoof_score

# Initialize face recognition service
face_service = FaceRecognitionService()

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate student with credentials"""
    try:
        data = request.get_json()
        student_id = data.get('studentId')
        password = data.get('password')
        remember_me = data.get('rememberMe', False)
        
        if not student_id or not password:
            return jsonify({
                'success': False,
                'message': 'Student ID and password are required'
            }), 400
        
        # Find student
        student = Student.query.filter_by(student_id=student_id, is_active=True).first()
        
        if not student or not check_password_hash(student.password_hash, password):
            return jsonify({
                'success': False,
                'message': 'Invalid Student ID or Password'
            }), 401
        
        # Create login session
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(hours=24 if remember_me else 8)
        
        login_session = LoginSession(
            student_id=student.id,
            session_token=session_token,
            expires_at=expires_at,
            login_method='password'
        )
        
        db.session.add(login_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'student': student.to_dict(),
            'session_token': session_token,
            'expires_at': expires_at.isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/auth/face-login', methods=['POST'])
def face_login():
    """Authenticate student using face recognition"""
    try:
        data = request.get_json()
        image_data = data.get('imageData')
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': 'Image data is required'
            }), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect faces
        faces = face_service.detect_faces(image_cv)
        
        if len(faces) == 0:
            return jsonify({
                'success': False,
                'message': 'No face detected in the image'
            }), 400
        
        if len(faces) > 1:
            return jsonify({
                'success': False,
                'message': 'Multiple faces detected. Please ensure only one face is visible'
            }), 400
        
        # Get the first (and only) face
        face_coords = faces[0]
        
        # Anti-spoofing check
        is_live, spoof_score = face_service.anti_spoofing_check(image_cv, face_coords)
        
        if not is_live:
            return jsonify({
                'success': False,
                'message': 'Anti-spoofing check failed. Please ensure you are using a live face'
            }), 400
        
        # Extract face embedding
        face_embedding = face_service.extract_face_embedding(image_cv, face_coords)
        
        # Find matching student
        best_match = None
        best_similarity = 0
        
        students = Student.query.filter_by(is_active=True).all()
        
        for student in students:
            if student.face_embedding:
                stored_embedding = np.array(json.loads(student.face_embedding))
                is_match, similarity = face_service.compare_embeddings(face_embedding, stored_embedding)
                
                if is_match and similarity > best_similarity:
                    best_match = student
                    best_similarity = similarity
        
        if not best_match or best_similarity < 0.7:  # Confidence threshold
            return jsonify({
                'success': False,
                'message': 'Face not recognized. Please try again or use regular login'
            }), 401
        
        # Create login session
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(hours=8)
        
        login_session = LoginSession(
            student_id=best_match.id,
            session_token=session_token,
            expires_at=expires_at,
            login_method='face'
        )
        
        db.session.add(login_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Face recognition successful',
            'student': best_match.to_dict(),
            'session_token': session_token,
            'expires_at': expires_at.isoformat(),
            'confidence': best_similarity
        })
        
    except Exception as e:
        app.logger.error(f"Face login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Face recognition failed. Please try again'
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout student and invalidate session"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if session_token:
            login_session = LoginSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if login_session:
                login_session.is_active = False
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Logout failed'
        }), 500

@app.route('/api/auth/verify-session', methods=['GET'])
def verify_session():
    """Verify if session is valid"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_token:
            return jsonify({
                'success': False,
                'message': 'No session token provided'
            }), 401
        
        login_session = LoginSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not login_session or login_session.expires_at < datetime.utcnow():
            return jsonify({
                'success': False,
                'message': 'Invalid or expired session'
            }), 401
        
        return jsonify({
            'success': True,
            'student': login_session.student.to_dict(),
            'expires_at': login_session.expires_at.isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Session verification error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Session verification failed'
        }), 500

@app.route('/api/attendance/mark', methods=['POST'])
def mark_attendance():
    """Mark attendance for a student"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_token:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Verify session
        login_session = LoginSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not login_session or login_session.expires_at < datetime.utcnow():
            return jsonify({
                'success': False,
                'message': 'Invalid or expired session'
            }), 401
        
        data = request.get_json()
        session_id = data.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'message': 'Session ID is required'
            }), 400
        
        # Check if attendance session exists and is active
        attendance_session = AttendanceSession.query.filter_by(
            id=session_id,
            is_active=True
        ).first()
        
        if not attendance_session:
            return jsonify({
                'success': False,
                'message': 'Invalid attendance session'
            }), 400
        
        # Check if student already marked attendance for this session
        existing_record = AttendanceRecord.query.filter_by(
            student_id=login_session.student_id,
            session_id=session_id
        ).first()
        
        if existing_record:
            return jsonify({
                'success': False,
                'message': 'Attendance already marked for this session'
            }), 400
        
        # Create attendance record
        attendance_record = AttendanceRecord(
            student_id=login_session.student_id,
            session_id=session_id,
            login_method=login_session.login_method,
            attendance_time=datetime.utcnow()
        )
        
        db.session.add(attendance_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Attendance marked successfully',
            'attendance_time': attendance_record.attendance_time.isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Mark attendance error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to mark attendance'
        }), 500

@app.route('/api/attendance/sessions', methods=['GET'])
def get_attendance_sessions():
    """Get active attendance sessions"""
    try:
        sessions = AttendanceSession.query.filter_by(is_active=True).all()
        
        session_list = []
        for session in sessions:
            session_list.append({
                'id': session.id,
                'session_name': session.session_name,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat(),
                'is_active': session.is_active
            })
        
        return jsonify({
            'success': True,
            'sessions': session_list
        })
        
    except Exception as e:
        app.logger.error(f"Get sessions error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve sessions'
        }), 500

@app.route('/api/students/register-face', methods=['POST'])
def register_face():
    """Register face for a student"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_token:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Verify session
        login_session = LoginSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not login_session or login_session.expires_at < datetime.utcnow():
            return jsonify({
                'success': False,
                'message': 'Invalid or expired session'
            }), 401
        
        data = request.get_json()
        image_data = data.get('imageData')
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': 'Image data is required'
            }), 400
        
        # Decode and process image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect faces
        faces = face_service.detect_faces(image_cv)
        
        if len(faces) == 0:
            return jsonify({
                'success': False,
                'message': 'No face detected in the image'
            }), 400
        
        if len(faces) > 1:
            return jsonify({
                'success': False,
                'message': 'Multiple faces detected. Please ensure only one face is visible'
            }), 400
        
        # Extract face embedding
        face_coords = faces[0]
        face_embedding = face_service.extract_face_embedding(image_cv, face_coords)
        
        # Save face embedding to student record
        student = Student.query.get(login_session.student_id)
        student.face_embedding = json.dumps(face_embedding.tolist())
        
        # Save face image (optional)
        face_image_path = f"faces/student_{student.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
        os.makedirs(os.path.dirname(face_image_path), exist_ok=True)
        cv2.imwrite(face_image_path, image_cv)
        student.face_image_path = face_image_path
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Face registered successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Register face error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to register face'
        }), 500

# Utility Functions
def generate_session_token():
    """Generate a secure session token"""
    return hashlib.sha256(f"{datetime.utcnow()}{os.urandom(16)}".encode()).hexdigest()

def create_sample_data():
    """Create sample data for testing"""
    # Create sample students
    students_data = [
        {
            'student_id': 'STU001',
            'name': 'John Doe',
            'email': 'john.doe@university.edu',
            'password': 'password123'
        },
        {
            'student_id': 'STU002',
            'name': 'Jane Smith',
            'email': 'jane.smith@university.edu',
            'password': 'password123'
        },
        {
            'student_id': 'STU003',
            'name': 'Mike Johnson',
            'email': 'mike.johnson@university.edu',
            'password': 'password123'
        }
    ]
    
    for student_data in students_data:
        existing_student = Student.query.filter_by(student_id=student_data['student_id']).first()
        if not existing_student:
            student = Student(
                student_id=student_data['student_id'],
                name=student_data['name'],
                email=student_data['email'],
                password_hash=generate_password_hash(student_data['password'])
            )
            db.session.add(student)
    
    # Create sample attendance session
    existing_session = AttendanceSession.query.filter_by(session_name='Morning Class').first()
    if not existing_session:
        session = AttendanceSession(
            session_name='Morning Class',
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=2)
        )
        db.session.add(session)
    
    db.session.commit()

# Initialize database and create tables
@app.before_first_request
def create_tables():
    db.create_all()
    create_sample_data()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
