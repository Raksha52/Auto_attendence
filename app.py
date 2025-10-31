import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_pymongo import PyMongo # MongoDB import
import cv2
import numpy as np
import json
import requests
from dotenv import load_dotenv
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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    db.Column('student_id', db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), primary_key=True)
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
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', backref=db.backref('student_user', uselist=False))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present' or 'absent'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AttendanceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    wifi_connected = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id))

# --- FACE DETECTION SYSTEM ---
# This class only performs simple face detection using OpenCV Haar Cascades
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
        # Convert OpenCV format (x, y, w, h) to face_recognition format (top, right, bottom, left)
        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))
        
        return face_locations

# Initialize face system later in app context
face_system = None


# --- ROUTES ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('choose'))

@app.route('/choose')
def choose():
    """Common landing page where user selects Teacher or Student flow."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('choose.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
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
    if session.get('student_user_id'):
        return redirect(url_for('student_dashboard'))
        
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

        # Store student session separately from teacher login
        session['student_user_id'] = student.id
        flash('Login successful')
        return redirect(url_for('student_dashboard'))

    return render_template('student_login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if session.get('student_user_id'):
        return redirect(url_for('student_dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        subject_ids = request.form.getlist('subject_id')

        if not name or not roll_number or not email or not password or not subject_ids:
            flash('All fields are required')
            subjects = Subject.query.all()
            return render_template('student_register.html', subjects=subjects)

        if StudentUser.query.filter_by(email=email).first():
            flash('Email already registered')
            subjects = Subject.query.all()
            return render_template('student_register.html', subjects=subjects)

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
        
        # Determine today's status for this subject
        today = datetime.now().date()
        today_record = Attendance.query.filter_by(student_id=student.id, subject_id=subj.id, date=today).first()
        # FIX: Corrected potential AttributeError: 'NoneType' object has no attribute 'status'
        today_status = today_record.status if today_record else 'N/A' 

        subject_stats.append({
            'subject': subj,
            'total': total_records,
            'present': present_count,
            'percent': percent,
            'today_status': today_status
        })

    return render_template('student_dashboard.html', student=student, subject_stats=subject_stats)

@app.route('/student/<int:student_id>/upload_face', methods=['GET', 'POST'])
def upload_face(student_id):
    """Page to capture multiple face images and save encodings for a student."""
    student = Student.query.get_or_404(student_id)

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
            
        data = request.get_json() or {}
        img_data = data.get('image')
        if not img_data:
            return jsonify({'success': False, 'message': 'No image data provided'}), 400

        header, encoded = img_data.split(',', 1)
        try:
            img_bytes = base64.b64decode(encoded)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            encs = face_recognition.face_encodings(rgb)
            if not encs:
                return jsonify({'success': False, 'message': 'No face found in image. Please ensure your face is clearly visible.'}), 400

            enc = encs[0].tolist()
            existing = []
            if student.face_encoding:
                try:
                    existing = json.loads(student.face_encoding)
                except Exception:
                    existing = []

            existing.append(enc)
            student.face_encoding = json.dumps(existing)
            db.session.commit()
            
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
    count = 0
    if student.face_encoding:
        try:
            count = len(json.loads(student.face_encoding))
        except Exception:
            count = 0

    return render_template('upload_face.html', student=student, count=count, face_recog_available=FACE_RECOG_AVAILABLE)

@app.route('/dashboard')
@login_required
def dashboard():
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

    if subject.teacher_id != current_user.id:
        flash('You are not authorized to delete this subject')
        return redirect(url_for('subjects'))

    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete subject: {str(e)}')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True})

    return redirect(url_for('subjects'))

@app.route('/students/<int:subject_id>')
@login_required
def students(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    # Ensure only the teacher who owns the subject can view
    if subject.teacher_id != current_user.id:
        flash('You are not authorized to view students for this subject.')
        return redirect(url_for('dashboard'))

    students = subject.students.all()
    return render_template('students.html', subject=subject, students=students)

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    roll_number = request.form['roll_number']
    subject_id = request.form['subject_id']
    
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
        
    return redirect(url_for('students', subject_id=subject_id))

@app.route('/attendance/<int:subject_id>')
@login_required
def attendance(subject_id):
    subject = Subject.query.get_or_404(subject_id)
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

@app.route('/start_attendance', methods=['POST'])
@login_required
def start_attendance():
    subject_id = request.form.get('subject_id')
    
    active_session = AttendanceSession.query.filter_by(
        subject_id=subject_id, 
        is_active=True
    ).first()
    
    if active_session:
        return jsonify({'success': False, 'message': 'Attendance session already active', 'session_id': active_session.id})
    
    session_record = AttendanceSession(
        subject_id=subject_id,
        teacher_id=current_user.id,
        start_time=datetime.utcnow(),
        is_active=True
    )
    
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

@app.route('/stop_attendance', methods=['POST'])
@login_required
def stop_attendance():
    session_id = request.form['session_id']
    
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
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Session not found'})

@app.route('/mark_present', methods=['POST'])
@login_required
def mark_present():
    student_id = request.form['student_id']
    subject_id = request.form['subject_id']
    
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

        cap = cv2.VideoCapture(0)
        
        while True:
            success, frame = cap.read()
            if not success:
                break
            
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
         
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stream_worker')
@login_required
def stream_worker():
    """Stream MJPEG frames served by the background CameraWorker."""
    # Ensure worker starts only if not running (and a session is active, ideally)
    # The worker is primarily controlled by start_attendance/stop_attendance
    try:
        if not cam_worker.running:
            cam_worker.start()
    except Exception as e:
        app.logger.error(f"Error starting cam_worker: {e}")

    def gen():
        while True:
            frame = cam_worker.get_frame()
            if frame:
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # Return a minimal placeholder frame if camera is not ready
                # This prevents the stream from hanging completely.
                # In a real app, this should be an actual error image
                time.sleep(1) # Slow down if no frame to prevent tight loop
                continue 
            time.sleep(0.03) # Frame rate control

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stream_recognize')
@login_required
def stream_recognize():
    """Stream MJPEG frames annotated with recognition results from cam_worker."""
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
                pass

            if annotated:
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + annotated + b'\r\n')
            else:
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
                time.sleep(1) # Throttle on empty frame
            time.sleep(0.03)

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recognitions_json')
@login_required
def recognitions_json():
    # Only return recognitions if a session is active
    if not cam_worker.active_session:
        return jsonify({'recognitions': [], 'message': 'No active attendance session.'})
    try:
        # NOTE: cam_worker.last_recognitions should be thread-safe in a real app
        # The minimal mock version does not enforce thread safety
        return jsonify({'recognitions': cam_worker.last_recognitions})
    except Exception:
        return jsonify({'recognitions': []})


# Attendance callback to integrate worker recognitions into attendance table
# This function is executed inside the cam_worker's thread in a real setup,
# but it must have an app context to interact with SQLAlchemy.
def _attendance_callback(rec, subject_id, session_id):
    # The cam_worker should call this function inside the Flask app context.
    # In the minimal mock, this is just a placeholder.
    # Assuming this is called correctly from a background worker with app_context...
    try:
        sid = rec.get('student_id')
        if not sid or not subject_id:
            return
        
        today = datetime.now().date()
        existing = Attendance.query.filter_by(student_id=sid, subject_id=subject_id, date=today).first()
        
        if existing:
            existing.status = 'present'
            existing.timestamp = datetime.utcnow()
        else:
            attendance = Attendance(student_id=sid, subject_id=subject_id, date=today, status='present')
            db.session.add(attendance)

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
    subject_id = request.form.get('subject_id')
    session_id = request.form.get('session_id')
    try:
        cam_worker.active_subject = int(subject_id) if subject_id else None
        cam_worker.active_session = int(session_id) if session_id else None
        cam_worker.attendance_callback = _attendance_callback
        cam_worker.start() # Start the worker if it's not running
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/export_attendance')
@login_required
def export_attendance():
    """Export attendance as CSV or Excel."""
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
            pass # Ignore invalid subject_id, export all for the date

    rows = q.all()

    if fmt == 'csv' or not HAVE_OPENPYXL:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['student_id', 'student_name', 'roll_number', 'subject_id', 'subject_name', 'date', 'status', 'timestamp', 'snapshot_file'])
        
        # Snapshot logic moved outside the loop setup
        import os
        snaps_dir = os.path.join(os.getcwd(), 'snapshots')
        
        for r in rows:
            try:
                student = Student.query.get(r.student_id)
                subject = Subject.query.get(r.subject_id)
                
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
                continue

        output.seek(0)
        return Response(output.getvalue(), mimetype='text/csv', headers={
            'Content-Disposition': f'attachment; filename=attendance_{date_obj.isoformat()}.csv'
        })

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
        
        for r in rows:
            try:
                student = Student.query.get(r.student_id)
                subject = Subject.query.get(r.subject_id)
                
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
    
    # Get all students associated with the subject (many-to-many relationship)
    # The original query was complex, let's simplify by using the relationship:
    all_students_for_subject = subject.students.all()
    
    # Get present students today
    present_records_today = Attendance.query.filter(
        Attendance.subject_id == subject_id,
        Attendance.date == today,
        Attendance.status == 'present'
    ).all()
    
    # Find absent students
    present_ids = {r.student_id for r in present_records_today}
    # Students who are in the subject but whose ID is not in the present_ids set
    absent_students = [s for s in all_students_for_subject if s.id not in present_ids]
    
    return render_template('absence_list.html', subject=subject, 
                            absent_students=absent_students, today=today)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message="Page not found (404)"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f"500 Internal Error: {error}\n{traceback.format_exc()}")
    return render_template('error.html', error_message="Internal server error (500)"), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Perform rollback unless it's a non-database-related error
    if not isinstance(e, (FileNotFoundError, ConnectionRefusedError, ImportError)): 
        db.session.rollback()
        
    app.logger.error(f"Unhandled Exception: {e}\n{traceback.format_exc()}")
    return render_template('error.html', error_message=f"Error: {str(e)}"), 500


@app.route('/__debug_subjects')
def debug_subjects():
    try:
        subs = Subject.query.all()
        out = [{'id': s.id, 'name': s.name, 'code': s.code, 'teacher_id': s.teacher_id, 'created_at': s.created_at.isoformat() if s.created_at else None} for s in subs]
        return jsonify({'count': len(out), 'subjects': out})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/__render_test')
def render_test():
    subs = Subject.query.all()
    # Note: This requires a 'dashboard.html' template
    return render_template('dashboard.html', subjects=subs)

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
    
    # Stop the minimal worker on shutdown
    import atexit
    atexit.register(cam_worker.stop) 
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)