<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
<<<<<<< HEAD
from flask_pymongo import PyMongo # MongoDB import
=======
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
import cv2
import numpy as np
import json
import requests
from dotenv import load_dotenv
<<<<<<< HEAD
from sqlalchemy import text, or_
import base64
import io
import time
import csv
from datetime import datetime as _dt
import sys
import traceback
import threading

# --- ENVIRONMENT & APP SETUP ---
load_dotenv()



# 🔹 Step 1: Create Flask app
app = Flask(__name__)

# 🔹 Step 2: Configure MongoDB (before initializing PyMongo)
app.config["MONGO_URI"] = "mongodb+srv://dbflaskuser:flask123@cluster0.tvpcrxu.mongodb.net/attendanceDB"

# 🔹 Step 3: Initialize PyMongo
mongo = PyMongo(app)

# 🔹 Step 4: Access your collections
students_collection = mongo.db.students
subjects_collection = mongo.db.subjects
attendance_collection = mongo.db.attendance

# 🔹 SQLAlchemy (SQLite) Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
instance_db_rel = os.path.join('instance', 'attendance.db')
instance_db_abs = os.path.abspath(instance_db_rel)
# The file existence check is moved inside __name__ == '__main__' to avoid initial context issues
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db' # Always use relative path here
=======
from sqlalchemy import text
import base64
import io
try:
    import face_recognition
    FACE_RECOG_AVAILABLE = True
except Exception:
    FACE_RECOG_AVAILABLE = False

# Camera worker (lightweight capture + frame skipping)
from camera_worker import cam_worker
import json
import time
import io
import csv
from datetime import datetime as _dt
try:
    import openpyxl
    HAVE_OPENPYXL = True
except Exception:
    HAVE_OPENPYXL = False

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
# Prefer the instance DB if it exists (preserves shipped data), otherwise use root attendance.db
instance_db_rel = os.path.join('instance', 'attendance.db')
instance_db_abs = os.path.abspath(instance_db_rel)
if os.path.exists(instance_db_abs) and os.access(instance_db_abs, os.R_OK):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{instance_db_abs}'
else:
    # fallback to root DB; print warning for visibility in server logs
    print(f'Warning: instance DB not accessible at {instance_db_abs}; falling back to attendance.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

<<<<<<< HEAD
# 🔹 Face Recognition Library Check
try:
    import face_recognition
    FACE_RECOG_AVAILABLE = True
except Exception:
    FACE_RECOG_AVAILABLE = False
    print("Warning: face_recognition library not found. Recognition features will be disabled.")

# Minimal Camera Worker Implementation (for self-contained code)
# This is a MOCK/SIMPLIFIED version to ensure the app runs without external 'camera_worker.py'
class MinimalCamWorker:
    def __init__(self):
        self.running = False
        self.last_recognitions = [] # List of {'student_id': 1, 'name': 'John Doe', 'box': [100, 100, 200, 200], 'live': True}
        self.active_subject = None
        self.active_session = None
        self.attendance_callback = None
        self.video_capture = None
        self.encodings_loaded = False
        self.lock = threading.Lock()

    def start(self):
        if not self.running:
            self.running = True
            # In a real app, this would start a background thread for capture and recognition
            # For this simplified version, we'll just open the camera
            if not self.video_capture:
                self.video_capture = cv2.VideoCapture(0)
            if FACE_RECOG_AVAILABLE and not self.encodings_loaded:
                self.load_encodings()
            print("MinimalCamWorker started (Mocking background thread).")

    def get_frame(self):
        if self.video_capture and self.video_capture.isOpened():
            success, frame = self.video_capture.read()
            if success:
                # Mock face detection/recognition for a running worker frame
                # In a real scenario, recognition happens in the background thread.
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                # Simple annotation for detected faces (no recognition here)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "Active Cam", (x, y - 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 0), 1)
                
                ret, buffer = cv2.imencode('.jpg', frame)
                return buffer.tobytes()
        return None

    def load_encodings(self):
        # In a real implementation, this would load all Student.face_encoding data
        # into memory for the background recognition thread.
        # It's called after a new face is uploaded.
        self.encodings_loaded = True
        print("Mock: Encodings reloaded for worker.")
        
    def stop(self):
        if self.video_capture:
            self.video_capture.release()
        self.running = False
        self.active_subject = None
        self.active_session = None
        print("MinimalCamWorker stopped.")

# Initialize the worker (using the minimal implementation)
cam_worker = MinimalCamWorker()
print("Using MinimalCamWorker mock for camera functions.")

# 🔹 OpenPyXL Check
try:
    import openpyxl
    HAVE_OPENPYXL = True
except Exception:
    HAVE_OPENPYXL = False

# --- DATABASE MODELS ---
=======
# Database Models
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
class Teacher(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Association table for many-to-many Student <-> Subject
student_subject = db.Table(
    'student_subject',
<<<<<<< HEAD
    db.Column('student_id', db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), primary_key=True)
=======
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    face_encoding = db.Column(db.Text, nullable=True)  # Store face encoding as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # many-to-many relationship to subjects
    subjects = db.relationship('Subject', secondary=student_subject, backref=db.backref('students', lazy='dynamic'))

class StudentUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
<<<<<<< HEAD
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
=======
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', backref=db.backref('student_user', uselist=False))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
<<<<<<< HEAD
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
=======
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present' or 'absent'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AttendanceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
<<<<<<< HEAD
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id', ondelete='CASCADE'), nullable=False)
=======
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    wifi_connected = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id))

<<<<<<< HEAD
# --- FACE DETECTION SYSTEM ---
# This class only performs simple face detection using OpenCV Haar Cascades
=======
# Face Detection System (Simplified)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
class FaceDetectionSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_students = []
        self.load_known_students()
    
    def load_known_students(self):
        """Load student information from database"""
        students = Student.query.all()
        self.known_students = [{'id': s.id, 'name': s.name, 'roll_number': s.roll_number} for s in students]
    
    def detect_faces(self, frame):
        """Detect faces in the given frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        face_locations = []
<<<<<<< HEAD
        # Convert OpenCV format (x, y, w, h) to face_recognition format (top, right, bottom, left)
=======
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))
        
        return face_locations

<<<<<<< HEAD
# Initialize face system later in app context
face_system = None


# --- ROUTES ---
=======
# Initialize face system after app context is available
face_system = None

# Routes
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('choose'))

<<<<<<< HEAD
=======

>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
@app.route('/choose')
def choose():
    """Common landing page where user selects Teacher or Student flow."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('choose.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
<<<<<<< HEAD
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
=======
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        teacher = Teacher.query.filter_by(username=username).first()
        
        if teacher and check_password_hash(teacher.password_hash, password):
            login_user(teacher)
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
<<<<<<< HEAD
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
=======
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if Teacher.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if Teacher.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        teacher = Teacher(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(teacher)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# =========================
# Student Authentication
# =========================
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
<<<<<<< HEAD
    if session.get('student_user_id'):
        return redirect(url_for('student_dashboard'))
        
=======
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    if request.method == 'POST':
        roll_number = request.form.get('roll_number', '').strip()
        password = request.form.get('password', '')

        student = Student.query.filter_by(roll_number=roll_number).first()
        if not student or not student.student_user:
            flash('Invalid roll number or password')
            return render_template('student_login.html')

        if not check_password_hash(student.student_user.password_hash, password):
            flash('Invalid roll number or password')
            return render_template('student_login.html')

<<<<<<< HEAD
=======
        # (Removed) same-WiFi restriction — students may login without teacher IP checks

>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        # Store student session separately from teacher login
        session['student_user_id'] = student.id
        flash('Login successful')
        return redirect(url_for('student_dashboard'))

    return render_template('student_login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
<<<<<<< HEAD
    if session.get('student_user_id'):
        return redirect(url_for('student_dashboard'))
        
=======
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
<<<<<<< HEAD
=======
        # Accept multiple subject IDs (form should send subject_id as list when multiple select)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        subject_ids = request.form.getlist('subject_id')

        if not name or not roll_number or not email or not password or not subject_ids:
            flash('All fields are required')
            subjects = Subject.query.all()
            return render_template('student_register.html', subjects=subjects)

        if StudentUser.query.filter_by(email=email).first():
            flash('Email already registered')
            subjects = Subject.query.all()
            return render_template('student_register.html', subjects=subjects)

<<<<<<< HEAD
        # Find existing student by roll number or create a new one
        student = Student.query.filter_by(roll_number=roll_number).first()
        
        if student and student.student_user:
            flash('Account already exists for this roll number')
            subjects = Subject.query.all()
            return render_template('student_register.html', subjects=subjects)
        
        if not student:
            # Create student using modern model structure
            student = Student(name=name, roll_number=roll_number)
            db.session.add(student)
            db.session.flush()

        # Associate subjects using the many-to-many relationship
        student.subjects = []
        for sid in subject_ids:
            try:
                sub = Subject.query.get(int(sid))
                if sub:
                    student.subjects.append(sub)
            except ValueError:
                continue # Skip invalid subject IDs
=======

        # Find existing student by roll number or create a new one
        student = Student.query.filter_by(roll_number=roll_number).first()
        if not student:
            # Handle legacy DBs where student.subject_id column still exists and is NOT NULL.
            res = db.session.execute(text("PRAGMA table_info(student);"))
            cols = [r[1] for r in res.fetchall()]
            if 'subject_id' in cols:
                # insert row via SQL including subject_id (use first selected subject if present)
                first_sid = int(subject_ids[0]) if subject_ids else None
                now = datetime.utcnow()
                db.session.execute(
                    text('INSERT INTO student (name, roll_number, face_encoding, created_at, subject_id) VALUES (:name, :roll, :face, :created, :sid)'),
                    {'name': name, 'roll': roll_number, 'face': None, 'created': now, 'sid': first_sid}
                )
                last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
                db.session.commit()
                student = Student.query.get(last_id)
            else:
                student = Student(name=name, roll_number=roll_number)
                db.session.add(student)
                db.session.flush()

        if student.student_user:
            flash('Account already exists for this roll number')
            subjects = Subject.query.all()
            return render_template('student_register.html', subjects=subjects)

        # associate subjects (store associations in the new association table)
        student.subjects = []
        for sid in subject_ids:
            sub = Subject.query.get(sid)
            if sub:
                student.subjects.append(sub)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

        student_user = StudentUser(
            student_id=student.id,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(student_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('student_login'))

    subjects = Subject.query.all()
    return render_template('student_register.html', subjects=subjects)

@app.route('/student/logout')
def student_logout():
    session.pop('student_user_id', None)
    return redirect(url_for('student_login'))

@app.route('/student/dashboard')
def student_dashboard():
    student_id = session.get('student_user_id')
    if not student_id:
        return redirect(url_for('student_login'))

    student = Student.query.get_or_404(student_id)
    # For each subject associated with the student, compute attendance percentage
    subject_stats = []
    for subj in student.subjects:
        total_records = Attendance.query.filter_by(student_id=student.id, subject_id=subj.id).count()
        present_count = Attendance.query.filter_by(student_id=student.id, subject_id=subj.id, status='present').count()
        if total_records > 0:
            percent = round((present_count / total_records) * 100, 1)
        else:
            percent = None
<<<<<<< HEAD
        
        # Determine today's status for this subject
        today = datetime.now().date()
        today_record = Attendance.query.filter_by(student_id=student.id, subject_id=subj.id, date=today).first()
        # FIX: Corrected potential AttributeError: 'NoneType' object has no attribute 'status'
        today_status = today_record.status if today_record else 'N/A' 
=======
        # Determine today's status for this subject
        today = datetime.now().date()
        today_record = Attendance.query.filter_by(student_id=student.id, subject_id=subj.id, date=today).first()
        today_status = today_record.status if today_record else 'absent'
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

        subject_stats.append({
            'subject': subj,
            'total': total_records,
            'present': present_count,
            'percent': percent,
            'today_status': today_status
        })

    return render_template('student_dashboard.html', student=student, subject_stats=subject_stats)

<<<<<<< HEAD
=======

>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
@app.route('/student/<int:student_id>/upload_face', methods=['GET', 'POST'])
def upload_face(student_id):
    """Page to capture multiple face images and save encodings for a student."""
    student = Student.query.get_or_404(student_id)

<<<<<<< HEAD
    # Authorization Check
    is_teacher = current_user.is_authenticated
    is_student_owner = session.get('student_user_id') == student_id
    
    if not (is_teacher or is_student_owner):
        flash('Authorization required to upload face data.')
        # Redirect based on who the user is/was trying to be
        if is_teacher:
             return redirect(url_for('dashboard')) 
        else:
             return redirect(url_for('student_login')) 

    if request.method == 'POST':
        if not FACE_RECOG_AVAILABLE:
            return jsonify({'success': False, 'message': 'face_recognition library not installed on server'}), 500
            
=======
    if request.method == 'POST':
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        data = request.get_json() or {}
        img_data = data.get('image')
        if not img_data:
            return jsonify({'success': False, 'message': 'No image data provided'}), 400

<<<<<<< HEAD
=======
        # img_data is a data URL like 'data:image/jpeg;base64,/9j/4AAQ...'
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        header, encoded = img_data.split(',', 1)
        try:
            img_bytes = base64.b64decode(encoded)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
<<<<<<< HEAD
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            encs = face_recognition.face_encodings(rgb)
            if not encs:
                return jsonify({'success': False, 'message': 'No face found in image. Please ensure your face is clearly visible.'}), 400

            enc = encs[0].tolist()
=======
            # convert BGR to RGB for face_recognition
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if not FACE_RECOG_AVAILABLE:
                return jsonify({'success': False, 'message': 'face_recognition library not installed on server'}), 500

            encs = face_recognition.face_encodings(rgb)
            if not encs:
                return jsonify({'success': False, 'message': 'No face found in image'}), 400

            enc = encs[0].tolist()

            # load existing encodings list or create
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
            existing = []
            if student.face_encoding:
                try:
                    existing = json.loads(student.face_encoding)
                except Exception:
                    existing = []

            existing.append(enc)
            student.face_encoding = json.dumps(existing)
            db.session.commit()
<<<<<<< HEAD
            
            # If the student's encodings were updated, force the cam_worker to reload them
            try:
                cam_worker.load_encodings() 
            except Exception:
                pass
            
            return jsonify({'success': True, 'count': len(existing)})
        except Exception as e:
            # Added more specific traceback for debugging
            app.logger.error(f"Error in upload_face: {e}\n{traceback.format_exc()}")
            return jsonify({'success': False, 'message': f'Server error processing image: {str(e)}'}), 500

    # GET -> render page
=======

            return jsonify({'success': True, 'count': len(existing)})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # GET -> render page
    # count existing encodings
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    count = 0
    if student.face_encoding:
        try:
            count = len(json.loads(student.face_encoding))
        except Exception:
            count = 0

<<<<<<< HEAD
    return render_template('upload_face.html', student=student, count=count, face_recog_available=FACE_RECOG_AVAILABLE)
=======
    return render_template('upload_face.html', student=student, count=count)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

@app.route('/dashboard')
@login_required
def dashboard():
<<<<<<< HEAD
    # FIX: Cleaned up the try/except block for dashboard to handle fallback gracefully
    try:
        # Prioritize subjects owned by the teacher
        subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
        
        if not subjects:
            # Fallback for easier demonstration if teacher has no subjects
            subjects = Subject.query.all() 

        subjects_data = [{'id': s.id, 'name': s.name, 'code': s.code, 'teacher_id': s.teacher_id} for s in subjects]
        return render_template('dashboard.html', subjects=subjects, subjects_json=subjects_data, subjects_count=len(subjects))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error loading dashboard for Teacher {current_user.id}: {str(e)}\n{traceback.format_exc()}')
        flash(f'An error occurred loading the dashboard: {str(e)}')
        return render_template('dashboard.html', subjects=[], subjects_json=[], subjects_count=0)

=======
    try:
        # Load all subjects so Manage Subjects always shows the subjects page content
        subjects = Subject.query.all()
        # Debug: if requested, return JSON of the subjects used for rendering
        if request.args.get('raw'):
            out = [{'id': s.id, 'name': s.name, 'code': s.code, 'teacher_id': s.teacher_id} for s in subjects]
            return jsonify({'subjects': out})
        # Debug: optionally include a response header with subjects count
        if request.args.get('hdr'):
            resp = make_response(render_template('dashboard.html', subjects=subjects))
            resp.headers['X-Subjects-Count'] = str(len(subjects))
            return resp
        # Prepare JSON payload for the template to render client-side (robust)
        try:
            app.logger.info(f"dashboard view: subjects_count={len(subjects)}, ids={[s.id for s in subjects]}")
        except Exception:
            app.logger.info('dashboard view: subjects present but failed to log ids')
        subjects_data = [{'id': s.id, 'name': s.name, 'code': s.code, 'teacher_id': s.teacher_id} for s in subjects]
        return render_template('dashboard.html', subjects=subjects, subjects_json=subjects_data, subjects_count=len(subjects))
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}')
        return render_template('dashboard.html', subjects=[])
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

@app.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/add_subject', methods=['POST'])
@login_required
def add_subject():
    name = request.form['name']
    code = request.form['code']
    
    if Subject.query.filter_by(code=code).first():
        flash('Subject code already exists')
        return redirect(url_for('subjects'))
    
    subject = Subject(name=name, code=code, teacher_id=current_user.id)
    db.session.add(subject)
    db.session.commit()
    
    flash('Subject added successfully!')
    return redirect(url_for('subjects'))

<<<<<<< HEAD
=======

>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
@app.route('/delete_subject', methods=['POST'])
@login_required
def delete_subject():
    """Delete a subject. Accepts form POST with 'subject_id'. Only the owner teacher may delete."""
    subject_id = request.form.get('subject_id')
    if not subject_id:
        flash('No subject specified')
        return redirect(url_for('subjects'))

    try:
        sid = int(subject_id)
    except Exception:
        flash('Invalid subject id')
        return redirect(url_for('subjects'))

    subject = Subject.query.get(sid)
    if not subject:
        flash('Subject not found')
        return redirect(url_for('subjects'))

<<<<<<< HEAD
=======
    # Only the teacher who owns the subject (or an admin) can delete
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    if subject.teacher_id != current_user.id:
        flash('You are not authorized to delete this subject')
        return redirect(url_for('subjects'))

    try:
<<<<<<< HEAD
=======
        # remove many-to-many association rows first to avoid orphaned references
        try:
            db.session.execute(student_subject.delete().where(student_subject.c.subject_id == sid))
        except Exception:
            pass
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete subject: {str(e)}')

<<<<<<< HEAD
=======
    # Support AJAX requests
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True})

    return redirect(url_for('subjects'))

@app.route('/students/<int:subject_id>')
@login_required
def students(subject_id):
    subject = Subject.query.get_or_404(subject_id)
<<<<<<< HEAD
    # Ensure only the teacher who owns the subject can view
    if subject.teacher_id != current_user.id:
        flash('You are not authorized to view students for this subject.')
        return redirect(url_for('dashboard'))

=======
    # find students associated with this subject
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    students = subject.students.all()
    return render_template('students.html', subject=subject, students=students)

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    roll_number = request.form['roll_number']
    subject_id = request.form['subject_id']
    
<<<<<<< HEAD
    student = Student.query.filter_by(roll_number=roll_number).first()
    
    is_new = False
    if student:
        flash(f'Roll number **{roll_number}** already exists. Adding student to subject.')
    else:
        student = Student(name=name, roll_number=roll_number)
        db.session.add(student)
        db.session.flush() # Get student.id for relationship
        is_new = True

    # Associate student with the subject using the many-to-many relationship
    sub = Subject.query.get(subject_id)
    if sub and student:
        if sub not in student.subjects:
            student.subjects.append(sub)
            try:
                db.session.commit()
                flash('Student added/updated successfully!')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to add student to subject: {str(e)}')
        else:
            flash(f'Student **{name}** is already registered for this subject.')
            if is_new:
                # If we created the student, but failed to add to subject, roll back.
                # If the commit was for a new student but failed on the relationship, 
                # this rollback might be too broad if the student was successfully added
                # before the relationship failed. It's safer to ensure the student
                # is only flushed (not committed) until the relationship is ready.
                db.session.rollback() # Rollback the student creation if relationship fails
            
    else:
        flash('Subject not found.')
        
=======
    if Student.query.filter_by(roll_number=roll_number).first():
        flash('Roll number already exists')
        return redirect(url_for('students', subject_id=subject_id))
    
    # create student; handle legacy DB with student.subject_id column
    res = db.session.execute(text("PRAGMA table_info(student);"))
    cols = [r[1] for r in res.fetchall()]
    if 'subject_id' in cols:
        now = datetime.utcnow()
        db.session.execute(
            text('INSERT INTO student (name, roll_number, face_encoding, created_at, subject_id) VALUES (:name, :roll, :face, :created, :sid)'),
            {'name': name, 'roll': roll_number, 'face': None, 'created': now, 'sid': int(subject_id)}
        )
        last_id = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
        db.session.commit()
        student = Student.query.get(last_id)
    else:
        student = Student(name=name, roll_number=roll_number)
        db.session.add(student)
        db.session.flush()

    sub = Subject.query.get(subject_id)
    if sub:
        student.subjects.append(sub)
    db.session.commit()
    
    flash('Student added successfully!')
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    return redirect(url_for('students', subject_id=subject_id))

@app.route('/attendance/<int:subject_id>')
@login_required
def attendance(subject_id):
    subject = Subject.query.get_or_404(subject_id)
<<<<<<< HEAD
    students_list = subject.students.all() # Renamed to avoid shadowing
    
    today = datetime.now().date()
    attendance_records = Attendance.query.filter_by(subject_id=subject_id, date=today).all()
    
    attendance_status = {record.student_id: record.status for record in attendance_records}
    
    active_session = AttendanceSession.query.filter_by(
        subject_id=subject_id, 
        is_active=True
    ).first()
    
    return render_template('attendance.html', subject=subject, students=students_list, 
                            attendance_status=attendance_status, today=today,
                            active_session=active_session)
=======
    # fetch students associated with this subject
    students = subject.students.all()
    
    # Get today's attendance
    today = datetime.now().date()
    attendance_records = Attendance.query.filter_by(subject_id=subject_id, date=today).all()
    
    # Create attendance status dictionary
    attendance_status = {record.student_id: record.status for record in attendance_records}
    
    return render_template('attendance.html', subject=subject, students=students, 
                         attendance_status=attendance_status, today=today)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

@app.route('/start_attendance', methods=['POST'])
@login_required
def start_attendance():
<<<<<<< HEAD
    subject_id = request.form.get('subject_id')
    
=======
    subject_id = request.form['subject_id']
    
    # Check if there's already an active session
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    active_session = AttendanceSession.query.filter_by(
        subject_id=subject_id, 
        is_active=True
    ).first()
    
    if active_session:
<<<<<<< HEAD
        return jsonify({'success': False, 'message': 'Attendance session already active', 'session_id': active_session.id})
    
    session_record = AttendanceSession(
=======
        return jsonify({'success': False, 'message': 'Attendance session already active'})
    
    # Create new attendance session
    session = AttendanceSession(
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        subject_id=subject_id,
        teacher_id=current_user.id,
        start_time=datetime.utcnow(),
        is_active=True
    )
    
<<<<<<< HEAD
    db.session.add(session_record)
    db.session.commit()
    
    # FIX/IMPROVEMENT: Set the active session and callback in the cam_worker
    try:
        cam_worker.active_subject = int(subject_id)
        cam_worker.active_session = session_record.id
        cam_worker.attendance_callback = _attendance_callback
        cam_worker.start() # Ensure worker is running
    except Exception as e:
        # Log this error but don't fail the route, as manual marking is still possible
        app.logger.warning(f"Failed to set cam_worker active session: {e}")
        
    return jsonify({'success': True, 'session_id': session_record.id})
=======
    db.session.add(session)
    db.session.commit()
    
    return jsonify({'success': True, 'session_id': session.id})
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

@app.route('/stop_attendance', methods=['POST'])
@login_required
def stop_attendance():
    session_id = request.form['session_id']
    
<<<<<<< HEAD
    session_record = AttendanceSession.query.get(session_id)
    if session_record:
        session_record.is_active = False
        session_record.end_time = datetime.utcnow()
        db.session.commit()
        
        # IMPROVEMENT: Clear and potentially stop the camera worker
        try:
            cam_worker.stop() # Added stop method for clean camera release
            cam_worker.active_subject = None
            cam_worker.active_session = None
            cam_worker.attendance_callback = None
            cam_worker.last_recognitions = []
        except Exception:
            pass 
        
=======
    session = AttendanceSession.query.get(session_id)
    if session:
        session.is_active = False
        session.end_time = datetime.utcnow()
        db.session.commit()
        
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Session not found'})

@app.route('/mark_present', methods=['POST'])
@login_required
def mark_present():
    student_id = request.form['student_id']
    subject_id = request.form['subject_id']
    
<<<<<<< HEAD
=======
    # Check if already marked today
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    today = datetime.now().date()
    existing = Attendance.query.filter_by(
        student_id=student_id,
        subject_id=subject_id,
        date=today
    ).first()
    
    if existing:
        existing.status = 'present'
        existing.timestamp = datetime.utcnow()
    else:
        attendance = Attendance(
            student_id=student_id,
            subject_id=subject_id,
            date=today,
            status='present'
        )
        db.session.add(attendance)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/video_feed')
@login_required
def video_feed():
    return render_template('video_feed.html')

@app.route('/video')
@login_required
def video():
    def generate_frames():
<<<<<<< HEAD
        # FIX: The context manager is only needed when accessing DB or models.
        # Initializing the FaceDetectionSystem should ideally be done once outside the generator,
        # but for robustness in a multi-threaded web server, we'll keep the logic.
        global face_system
        if face_system is None:
            # We initialize it here without the full app_context, as it mostly uses cv2.
            # If it failed in __main__, it will likely fail here too.
            try:
                face_system = FaceDetectionSystem()
            except Exception as e:
                print(f"Error initializing FaceDetectionSystem in video stream: {e}")
                
        # Use the global cam_worker if it's available and running, for cleaner code
        if cam_worker.running:
            flash("Error: Camera is being used by the background attendance worker. Stop the session to view raw feed.")
            return # Should probably redirect or return an error image

=======
        global face_system
        if face_system is None:
            face_system = FaceDetectionSystem()
            
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        cap = cv2.VideoCapture(0)
        
        while True:
            success, frame = cap.read()
            if not success:
                break
            
<<<<<<< HEAD
            if face_system:
                face_locations = face_system.detect_faces(frame)
                
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, "Face Detected", (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
            else:
                # Add a message if face_system failed to initialize
                cv2.putText(frame, "No Face System", (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
                
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        cap.release() # Release camera resource
    
    # Check if the camera is already in use by the worker
    if cam_worker.running:
         flash("The camera is currently in use by an active attendance session. Please stop the session first.")
         return redirect(url_for('dashboard')) # Redirect user away
         
=======
            # Detect faces
            face_locations = face_system.detect_faces(frame)
            
            # Draw rectangles around faces
            for (top, right, bottom, left) in face_locations:
                # Draw rectangle around face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Draw label
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, "Face Detected", (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stream_worker')
@login_required
def stream_worker():
    """Stream MJPEG frames served by the background CameraWorker."""
<<<<<<< HEAD
    # Ensure worker starts only if not running (and a session is active, ideally)
    # The worker is primarily controlled by start_attendance/stop_attendance
    try:
        if not cam_worker.running:
            cam_worker.start()
    except Exception as e:
        app.logger.error(f"Error starting cam_worker: {e}")
=======
    # start worker lazily
    try:
        if not cam_worker.running:
            cam_worker.start()
    except Exception:
        pass
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

    def gen():
        while True:
            frame = cam_worker.get_frame()
            if frame:
                yield (b'--frame\r\n'
<<<<<<< HEAD
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # Return a minimal placeholder frame if camera is not ready
                # This prevents the stream from hanging completely.
                # In a real app, this should be an actual error image
                time.sleep(1) # Slow down if no frame to prevent tight loop
                continue 
            time.sleep(0.03) # Frame rate control
=======
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # send a tiny blank image if nothing yet
                blank = b''
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + blank + b'\r\n')
            time.sleep(0.03)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stream_recognize')
@login_required
def stream_recognize():
    """Stream MJPEG frames annotated with recognition results from cam_worker."""
<<<<<<< HEAD
    # This route is usually for the teacher's view during an active session.
    # We should only proceed if a session is active and the worker is running.
    if not cam_worker.active_session or not cam_worker.running:
        return Response("Camera worker is not active for recognition.", status=400)

    def gen():
        while True:
            # We use get_frame from the minimal worker for the base image
            frame = cam_worker.get_frame() 
            annotated = frame
            
            try:
                # Mock annotation logic for the minimal worker
                if frame and cam_worker.last_recognitions:
                    nparr = np.frombuffer(frame, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    for rec in cam_worker.last_recognitions:
                        # Assuming rec['box'] is [x1, y1, x2, y2] (OpenCV standard)
                        x1, y1, x2, y2 = rec['box'] 
                        color = (0, 255, 0) if rec.get('live') else (0, 0, 255) 
                        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                        
                        label = rec.get('name') or ('Unknown')
                        cv2.rectangle(img, (x1, y2 - 25), (x2, y2), color, cv2.FILLED)
                        cv2.putText(img, label, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                        
                    ret2, jpg = cv2.imencode('.jpg', img)
                    if ret2:
                        annotated = jpg.tobytes()
            except Exception as e:
                app.logger.error(f"Annotation error: {e}")
=======
    # ensure worker is running
    try:
        if not cam_worker.running:
            cam_worker.start()
    except Exception:
        pass

    def gen():
        while True:
            frame = cam_worker.get_frame()
            # attempt to annotate the frame with recognition boxes and names
            annotated = frame
            try:
                if frame and cam_worker.last_recognitions:
                    import numpy as np
                    nparr = np.frombuffer(frame, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    for rec in cam_worker.last_recognitions:
                        x1, y1, x2, y2 = rec['box']
                        # box color green if live else red
                        color = (16,185,129) if rec.get('live') else (220,38,38)
                        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                        label = rec.get('name') or ('Unknown')
                        cv2.putText(img, label, (x1, max(10, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                    ret2, jpg = cv2.imencode('.jpg', img)
                    if ret2:
                        annotated = jpg.tobytes()
            except Exception:
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
                pass

            if annotated:
                yield (b'--frame\r\n'
<<<<<<< HEAD
                        b'Content-Type: image/jpeg\r\n\r\n' + annotated + b'\r\n')
            else:
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
                time.sleep(1) # Throttle on empty frame
=======
                       b'Content-Type: image/jpeg\r\n\r\n' + annotated + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
            time.sleep(0.03)

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recognitions_json')
@login_required
def recognitions_json():
<<<<<<< HEAD
    # Only return recognitions if a session is active
    if not cam_worker.active_session:
        return jsonify({'recognitions': [], 'message': 'No active attendance session.'})
    try:
        # NOTE: cam_worker.last_recognitions should be thread-safe in a real app
        # The minimal mock version does not enforce thread safety
=======
    # return the last recognitions as JSON
    try:
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        return jsonify({'recognitions': cam_worker.last_recognitions})
    except Exception:
        return jsonify({'recognitions': []})


# Attendance callback to integrate worker recognitions into attendance table
<<<<<<< HEAD
# This function is executed inside the cam_worker's thread in a real setup,
# but it must have an app context to interact with SQLAlchemy.
def _attendance_callback(rec, subject_id, session_id):
    # The cam_worker should call this function inside the Flask app context.
    # In the minimal mock, this is just a placeholder.
    # Assuming this is called correctly from a background worker with app_context...
=======
def _attendance_callback(rec, subject_id, session_id):
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    try:
        sid = rec.get('student_id')
        if not sid or not subject_id:
            return
<<<<<<< HEAD
        
        today = datetime.now().date()
        existing = Attendance.query.filter_by(student_id=sid, subject_id=subject_id, date=today).first()
        
        if existing:
=======
        # check today's record
        today = datetime.now().date()
        existing = Attendance.query.filter_by(student_id=sid, subject_id=subject_id, date=today).first()
        if existing:
            # update timestamp if already present
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
            existing.status = 'present'
            existing.timestamp = datetime.utcnow()
        else:
            attendance = Attendance(student_id=sid, subject_id=subject_id, date=today, status='present')
            db.session.add(attendance)

<<<<<<< HEAD
        # Snapshot saving logic
        snap = rec.get('snapshot')
        if snap:
            try:
                import os
                snaps_dir = os.path.join(os.getcwd(), 'snapshots')
                os.makedirs(snaps_dir, exist_ok=True)
                # Use session_id in the filename for better grouping
                fname = f"snap_{sid}_s{session_id}_{int(time.time())}.jpg"
                with open(os.path.join(snaps_dir, fname), 'wb') as f:
                    f.write(snap)
            except Exception as e:
                app.logger.error(f"Error saving snapshot: {e}")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in attendance callback: {e}\n{traceback.format_exc()}")


@app.route('/worker/set_active', methods=['POST'])
@login_required
def worker_set_active():
    # FIX/IMPROVEMENT: Ensure subject_id and session_id are passed and set correctly.
    # This route is now mostly redundant as the logic is in start_attendance
    # but kept for completeness if AJAX calls it separately.
=======
        # optional: store snapshot to disk for audit
        snap = rec.get('snapshot')
        if snap:
            try:
                # create snapshots directory
                import os
                snaps_dir = os.path.join(os.getcwd(), 'snapshots')
                os.makedirs(snaps_dir, exist_ok=True)
                fname = f"snap_{sid}_{int(time.time())}.jpg"
                with open(os.path.join(snaps_dir, fname), 'wb') as f:
                    f.write(snap)
            except Exception:
                pass

        db.session.commit()
    except Exception:
        db.session.rollback()
        return


# helper route to set active subject/session for camera worker
@app.route('/worker/set_active', methods=['POST'])
@login_required
def worker_set_active():
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    subject_id = request.form.get('subject_id')
    session_id = request.form.get('session_id')
    try:
        cam_worker.active_subject = int(subject_id) if subject_id else None
        cam_worker.active_session = int(session_id) if session_id else None
<<<<<<< HEAD
        cam_worker.attendance_callback = _attendance_callback
        cam_worker.start() # Start the worker if it's not running
=======
        # register callback
        cam_worker.attendance_callback = _attendance_callback
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/export_attendance')
@login_required
def export_attendance():
<<<<<<< HEAD
    """Export attendance as CSV or Excel."""
=======
    """Export attendance as CSV or Excel.

    Query params:
      - subject_id (optional)
      - date (YYYY-MM-DD) optional; defaults to today
      - format: 'csv' (default) or 'xlsx'
    """
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    subject_id = request.args.get('subject_id')
    date_str = request.args.get('date')
    fmt = request.args.get('format', 'csv').lower()

    try:
        if date_str:
            date_obj = _dt.strptime(date_str, '%Y-%m-%d').date()
        else:
            date_obj = datetime.now().date()
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid date format; use YYYY-MM-DD'}), 400

    q = Attendance.query.filter_by(date=date_obj)
    if subject_id:
        try:
            sid = int(subject_id)
            q = q.filter_by(subject_id=sid)
        except Exception:
<<<<<<< HEAD
            pass # Ignore invalid subject_id, export all for the date

    rows = q.all()

    if fmt == 'csv' or not HAVE_OPENPYXL:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['student_id', 'student_name', 'roll_number', 'subject_id', 'subject_name', 'date', 'status', 'timestamp', 'snapshot_file'])
        
        # Snapshot logic moved outside the loop setup
        import os
        snaps_dir = os.path.join(os.getcwd(), 'snapshots')
        
=======
            pass

    rows = q.all()

    # Build CSV in-memory
    if fmt == 'csv' or not HAVE_OPENPYXL:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['student_id', 'student_name', 'roll_number', 'subject_id', 'subject_name', 'date', 'status', 'timestamp', 'snapshot'])
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        for r in rows:
            try:
                student = Student.query.get(r.student_id)
                subject = Subject.query.get(r.subject_id)
<<<<<<< HEAD
                
                # Search for snapshot file
                snapshot_file = ''
                if os.path.isdir(snaps_dir):
                    # We check for a snapshot created close to the attendance timestamp
                    # This check is heuristic and could be improved with better DB record keeping
                    attendance_ts_s = time.mktime(r.timestamp.timetuple())
                    for f in os.listdir(snaps_dir):
                         # Check if the file starts with the student id and was created within a day
                        if f.startswith(f"snap_{r.student_id}_") and os.path.getmtime(os.path.join(snaps_dir, f)) > attendance_ts_s - 86400:
                            snapshot_file = f
                            break
                            
                writer.writerow([
                    r.student_id, 
                    student.name if student else '', 
                    student.roll_number if student else '', 
                    r.subject_id, 
                    subject.name if subject else '', 
                    r.date.isoformat(), 
                    r.status, 
                    r.timestamp.isoformat(), 
                    snapshot_file
                ])
            except Exception:
                # Log the specific row error but continue with the export
                app.logger.error(f"Error processing row for student {r.student_id}: {traceback.format_exc()}")
=======
                # find snapshot filename pattern if exists
                snapshot_file = ''
                import os
                snaps_dir = os.path.join(os.getcwd(), 'snapshots')
                if os.path.isdir(snaps_dir):
                    # pick any matching file for this student on same day (best-effort)
                    for f in os.listdir(snaps_dir):
                        if f.startswith(f"snap_{r.student_id}_"):
                            snapshot_file = f
                            break
                writer.writerow([r.student_id, student.name if student else '', student.roll_number if student else '', r.subject_id, subject.name if subject else '', r.date.isoformat(), r.status, r.timestamp.isoformat(), snapshot_file])
            except Exception:
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
                continue

        output.seek(0)
        return Response(output.getvalue(), mimetype='text/csv', headers={
            'Content-Disposition': f'attachment; filename=attendance_{date_obj.isoformat()}.csv'
        })

<<<<<<< HEAD
    if fmt == 'xlsx':
        if not HAVE_OPENPYXL:
            return jsonify({'success': False, 'message': 'openpyxl not installed; install to enable xlsx export'}), 400
            
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(['student_id', 'student_name', 'roll_number', 'subject_id', 'subject_name', 'date', 'status', 'timestamp', 'snapshot_file'])
        
        # Snapshot logic setup for XLSX
        import os
        snaps_dir = os.path.join(os.getcwd(), 'snapshots')
        
=======
    # Else generate XLSX
    if fmt == 'xlsx':
        if not HAVE_OPENPYXL:
            return jsonify({'success': False, 'message': 'openpyxl not installed; install to enable xlsx export'}), 400
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(['student_id', 'student_name', 'roll_number', 'subject_id', 'subject_name', 'date', 'status', 'timestamp', 'snapshot'])
        import os
        snaps_dir = os.path.join(os.getcwd(), 'snapshots')
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        for r in rows:
            try:
                student = Student.query.get(r.student_id)
                subject = Subject.query.get(r.subject_id)
<<<<<<< HEAD
                
                snapshot_file = ''
                if os.path.isdir(snaps_dir):
                    attendance_ts_s = time.mktime(r.timestamp.timetuple())
                    for f in os.listdir(snaps_dir):
                        if f.startswith(f"snap_{r.student_id}_") and os.path.getmtime(os.path.join(snaps_dir, f)) > attendance_ts_s - 86400:
                            snapshot_file = f
                            break
                            
                ws.append([
                    r.student_id, 
                    student.name if student else '', 
                    student.roll_number if student else '', 
                    r.subject_id, 
                    subject.name if subject else '', 
                    r.date.isoformat(), 
                    r.status, 
                    r.timestamp.isoformat(), 
                    snapshot_file
                ])
            except Exception:
                app.logger.error(f"Error processing row for student {r.student_id} in XLSX: {traceback.format_exc()}")
=======
                snapshot_file = ''
                if os.path.isdir(snaps_dir):
                    for f in os.listdir(snaps_dir):
                        if f.startswith(f"snap_{r.student_id}_"):
                            snapshot_file = f
                            break
                ws.append([r.student_id, student.name if student else '', student.roll_number if student else '', r.subject_id, subject.name if subject else '', r.date.isoformat(), r.status, r.timestamp.isoformat(), snapshot_file])
            except Exception:
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
                continue

        bio = io.BytesIO()
        wb.save(bio)
        bio.seek(0)
        return Response(bio.read(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={
            'Content-Disposition': f'attachment; filename=attendance_{date_obj.isoformat()}.xlsx'
        })

    return jsonify({'success': False, 'message': 'Unsupported format'}), 400

@app.route('/absence_list/<int:subject_id>')
@login_required
def absence_list(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    today = datetime.now().date()
    
<<<<<<< HEAD
    # Get all students associated with the subject (many-to-many relationship)
    # The original query was complex, let's simplify by using the relationship:
    all_students_for_subject = subject.students.all()
    
    # Get present students today
    present_records_today = Attendance.query.filter(
=======
    # Get all students for this subject
    all_students = Student.query.filter_by(subject_id=subject_id).all()
    
    # Get present students today
    present_students = db.session.query(Student).join(Attendance).filter(
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        Attendance.subject_id == subject_id,
        Attendance.date == today,
        Attendance.status == 'present'
    ).all()
    
    # Find absent students
<<<<<<< HEAD
    present_ids = {r.student_id for r in present_records_today}
    # Students who are in the subject but whose ID is not in the present_ids set
    absent_students = [s for s in all_students_for_subject if s.id not in present_ids]
    
    return render_template('absence_list.html', subject=subject, 
                            absent_students=absent_students, today=today)
=======
    present_ids = [s.id for s in present_students]
    absent_students = [s for s in all_students if s.id not in present_ids]
    
    return render_template('absence_list.html', subject=subject, 
                         absent_students=absent_students, today=today)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message="Page not found (404)"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
<<<<<<< HEAD
    app.logger.error(f"500 Internal Error: {error}\n{traceback.format_exc()}")
=======
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
    return render_template('error.html', error_message="Internal server error (500)"), 500

@app.errorhandler(Exception)
def handle_exception(e):
<<<<<<< HEAD
    # Perform rollback unless it's a non-database-related error
    if not isinstance(e, (FileNotFoundError, ConnectionRefusedError, ImportError)): 
        db.session.rollback()
        
    app.logger.error(f"Unhandled Exception: {e}\n{traceback.format_exc()}")
    return render_template('error.html', error_message=f"Error: {str(e)}"), 500


=======
    return render_template('error.html', error_message=f"Error: {str(e)}"), 500


# Debug-only route: list subjects known to the running app (JSON)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
@app.route('/__debug_subjects')
def debug_subjects():
    try:
        subs = Subject.query.all()
        out = [{'id': s.id, 'name': s.name, 'code': s.code, 'teacher_id': s.teacher_id, 'created_at': s.created_at.isoformat() if s.created_at else None} for s in subs]
        return jsonify({'count': len(out), 'subjects': out})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

<<<<<<< HEAD
@app.route('/__whoami')
def debug_whoami():
    try:
        is_authenticated = bool(getattr(current_user, 'is_authenticated', False))
        is_student = 'student_user_id' in session
        return jsonify({
            'is_teacher_authenticated': is_authenticated,
            'teacher_id': getattr(current_user, 'id', None) if is_authenticated else None,
            'teacher_username': getattr(current_user, 'username', None) if is_authenticated else None,
            'is_student_authenticated': is_student,
            'student_id': session.get('student_user_id', None)
=======

@app.route('/__whoami')
def debug_whoami():
    try:
        return jsonify({
            'is_authenticated': bool(getattr(current_user, 'is_authenticated', False)),
            'id': getattr(current_user, 'id', None),
            'username': getattr(current_user, 'username', None)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

<<<<<<< HEAD
=======

>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
@app.route('/__debug_dashboard')
def debug_dashboard():
    try:
        teacher_id = getattr(current_user, 'id', None)
        subjects_by_teacher = [ { 'id': s.id, 'name': s.name, 'teacher_id': s.teacher_id } for s in Subject.query.filter_by(teacher_id=teacher_id).all() ]
        fallback = [ { 'id': s.id, 'name': s.name, 'teacher_id': s.teacher_id } for s in Subject.query.all() ]
        final = subjects_by_teacher if subjects_by_teacher else fallback
        return jsonify({ 'teacher_id': teacher_id, 'subjects_by_teacher': subjects_by_teacher, 'fallback_subjects': fallback, 'final_subjects': final })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

<<<<<<< HEAD
@app.route('/__render_test')
def render_test():
    subs = Subject.query.all()
    # Note: This requires a 'dashboard.html' template
    return render_template('dashboard.html', subjects=subs)

=======

@app.route('/__render_test')
def render_test():
    # Render the dashboard template with all subjects (bypasses login) for testing
    subs = Subject.query.all()
    return render_template('dashboard.html', subjects=subs)


>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
@app.route('/api/subjects')
@login_required
def api_subjects():
    """Return subjects for the logged-in teacher as JSON."""
    try:
        subs = Subject.query.filter_by(teacher_id=current_user.id).all()
        if not subs:
            subs = Subject.query.all()
        out = [{'id': s.id, 'name': s.name, 'code': s.code, 'teacher_id': s.teacher_id} for s in subs]
        return jsonify({'count': len(out), 'subjects': out})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

<<<<<<< HEAD
# --- MAIN RUN BLOCK ---
if __name__ == '__main__':
    with app.app_context():
        # Check and set SQLite URI before calling db.create_all()
        instance_db_rel = os.path.join('instance', 'attendance.db')
        instance_db_abs = os.path.abspath(instance_db_rel)
        if os.path.exists(instance_db_abs) and os.access(instance_db_abs, os.R_OK):
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{instance_db_abs}'
        else:
            print(f'Warning: instance DB not accessible at {instance_db_abs}; falling back to attendance.db')
            # This ensures the database is created at the correct location
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db' 
        
        # Bind the changes to the app (db already initialized at line 50)
        db.create_all()
        
        # Attempt to initialize face detection system
        try:
            face_system = FaceDetectionSystem()
            # If the simple detection works, we print a positive message.
            if face_system.face_cascade.empty():
                 raise Exception("Haar Cascade Classifier failed to load.")
            print("Face Detection System (OpenCV) initialized successfully.")
        except Exception as e:
            app.logger.warning(f"Warning: Could not initialize FaceDetectionSystem (Haar Cascade): {e}")
            
=======
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
        # Create default teacher if none exists
        if not Teacher.query.first():
            default_teacher = Teacher(
                username='admin',
                email='admin@school.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(default_teacher)
            db.session.commit()
            print("Default teacher created: username=admin, password=admin123")
    
<<<<<<< HEAD
    # Stop the minimal worker on shutdown
    import atexit
    atexit.register(cam_worker.stop) 
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
=======
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
>>>>>>> a43efd88c1abf46e3eb56fc98ca023036932b734
=======
    app.run(debug=True, host='0.0.0.0', port=5000)
>>>>>>> e0a5a269c49ffcd2d0741aee0a2ad10f37f98752
