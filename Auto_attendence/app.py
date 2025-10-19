import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import cv2
import numpy as np
import json
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
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

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    face_encoding = db.Column(db.Text, nullable=True)  # Store face encoding as JSON
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present' or 'absent'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AttendanceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    wifi_connected = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id))

# Face Detection System (Simplified)
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
        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))
        
        return face_locations

# Initialize face system after app context is available
face_system = None

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
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

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
        return render_template('dashboard.html', subjects=subjects)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}')
        return render_template('dashboard.html', subjects=[])

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

@app.route('/students/<int:subject_id>')
@login_required
def students(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    students = Student.query.filter_by(subject_id=subject_id).all()
    return render_template('students.html', subject=subject, students=students)

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    roll_number = request.form['roll_number']
    subject_id = request.form['subject_id']
    
    if Student.query.filter_by(roll_number=roll_number).first():
        flash('Roll number already exists')
        return redirect(url_for('students', subject_id=subject_id))
    
    student = Student(name=name, roll_number=roll_number, subject_id=subject_id)
    db.session.add(student)
    db.session.commit()
    
    flash('Student added successfully!')
    return redirect(url_for('students', subject_id=subject_id))

@app.route('/attendance/<int:subject_id>')
@login_required
def attendance(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    students = Student.query.filter_by(subject_id=subject_id).all()
    
    # Get today's attendance
    today = datetime.now().date()
    attendance_records = Attendance.query.filter_by(subject_id=subject_id, date=today).all()
    
    # Create attendance status dictionary
    attendance_status = {record.student_id: record.status for record in attendance_records}
    
    return render_template('attendance.html', subject=subject, students=students, 
                         attendance_status=attendance_status, today=today)

@app.route('/start_attendance', methods=['POST'])
@login_required
def start_attendance():
    subject_id = request.form['subject_id']
    
    # Check if there's already an active session
    active_session = AttendanceSession.query.filter_by(
        subject_id=subject_id, 
        is_active=True
    ).first()
    
    if active_session:
        return jsonify({'success': False, 'message': 'Attendance session already active'})
    
    # Create new attendance session
    session = AttendanceSession(
        subject_id=subject_id,
        teacher_id=current_user.id,
        start_time=datetime.utcnow(),
        is_active=True
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({'success': True, 'session_id': session.id})

@app.route('/stop_attendance', methods=['POST'])
@login_required
def stop_attendance():
    session_id = request.form['session_id']
    
    session = AttendanceSession.query.get(session_id)
    if session:
        session.is_active = False
        session.end_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Session not found'})

@app.route('/mark_present', methods=['POST'])
@login_required
def mark_present():
    student_id = request.form['student_id']
    subject_id = request.form['subject_id']
    
    # Check if already marked today
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
        global face_system
        if face_system is None:
            face_system = FaceDetectionSystem()
            
        cap = cv2.VideoCapture(0)
        
        while True:
            success, frame = cap.read()
            if not success:
                break
            
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
    
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/absence_list/<int:subject_id>')
@login_required
def absence_list(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    today = datetime.now().date()
    
    # Get all students for this subject
    all_students = Student.query.filter_by(subject_id=subject_id).all()
    
    # Get present students today
    present_students = db.session.query(Student).join(Attendance).filter(
        Attendance.subject_id == subject_id,
        Attendance.date == today,
        Attendance.status == 'present'
    ).all()
    
    # Find absent students
    present_ids = [s.id for s in present_students]
    absent_students = [s for s in all_students if s.id not in present_ids]
    
    return render_template('absence_list.html', subject=subject, 
                         absent_students=absent_students, today=today)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message="Page not found (404)"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_message="Internal server error (500)"), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error.html', error_message=f"Error: {str(e)}"), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
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
    
    app.run(debug=True, host='0.0.0.0', port=5000)
