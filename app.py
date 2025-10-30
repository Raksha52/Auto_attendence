import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import cv2
import numpy as np
import json
import requests
from dotenv import load_dotenv
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

# Association table for many-to-many Student <-> Subject
student_subject = db.Table(
    'student_subject',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
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
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', backref=db.backref('student_user', uselist=False))

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
    return redirect(url_for('choose'))


@app.route('/choose')
def choose():
    """Common landing page where user selects Teacher or Student flow."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('choose.html')

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

# =========================
# Student Authentication
# =========================
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
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

        # (Removed) same-WiFi restriction — students may login without teacher IP checks

        # Store student session separately from teacher login
        session['student_user_id'] = student.id
        flash('Login successful')
        return redirect(url_for('student_dashboard'))

    return render_template('student_login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        # Accept multiple subject IDs (form should send subject_id as list when multiple select)
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
        today_status = today_record.status if today_record else 'absent'

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

    if request.method == 'POST':
        data = request.get_json() or {}
        img_data = data.get('image')
        if not img_data:
            return jsonify({'success': False, 'message': 'No image data provided'}), 400

        # img_data is a data URL like 'data:image/jpeg;base64,/9j/4AAQ...'
        header, encoded = img_data.split(',', 1)
        try:
            img_bytes = base64.b64decode(encoded)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # convert BGR to RGB for face_recognition
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if not FACE_RECOG_AVAILABLE:
                return jsonify({'success': False, 'message': 'face_recognition library not installed on server'}), 500

            encs = face_recognition.face_encodings(rgb)
            if not encs:
                return jsonify({'success': False, 'message': 'No face found in image'}), 400

            enc = encs[0].tolist()

            # load existing encodings list or create
            existing = []
            if student.face_encoding:
                try:
                    existing = json.loads(student.face_encoding)
                except Exception:
                    existing = []

            existing.append(enc)
            student.face_encoding = json.dumps(existing)
            db.session.commit()

            return jsonify({'success': True, 'count': len(existing)})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # GET -> render page
    # count existing encodings
    count = 0
    if student.face_encoding:
        try:
            count = len(json.loads(student.face_encoding))
        except Exception:
            count = 0

    return render_template('upload_face.html', student=student, count=count)

@app.route('/dashboard')
@login_required
def dashboard():
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

    # Only the teacher who owns the subject (or an admin) can delete
    if subject.teacher_id != current_user.id:
        flash('You are not authorized to delete this subject')
        return redirect(url_for('subjects'))

    try:
        # remove many-to-many association rows first to avoid orphaned references
        try:
            db.session.execute(student_subject.delete().where(student_subject.c.subject_id == sid))
        except Exception:
            pass
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete subject: {str(e)}')

    # Support AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True})

    return redirect(url_for('subjects'))

@app.route('/students/<int:subject_id>')
@login_required
def students(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    # find students associated with this subject
    students = subject.students.all()
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
    return redirect(url_for('students', subject_id=subject_id))

@app.route('/attendance/<int:subject_id>')
@login_required
def attendance(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    # fetch students associated with this subject
    students = subject.students.all()
    
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


@app.route('/stream_worker')
@login_required
def stream_worker():
    """Stream MJPEG frames served by the background CameraWorker."""
    # start worker lazily
    try:
        if not cam_worker.running:
            cam_worker.start()
    except Exception:
        pass

    def gen():
        while True:
            frame = cam_worker.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # send a tiny blank image if nothing yet
                blank = b''
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + blank + b'\r\n')
            time.sleep(0.03)

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stream_recognize')
@login_required
def stream_recognize():
    """Stream MJPEG frames annotated with recognition results from cam_worker."""
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
                pass

            if annotated:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + annotated + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
            time.sleep(0.03)

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recognitions_json')
@login_required
def recognitions_json():
    # return the last recognitions as JSON
    try:
        return jsonify({'recognitions': cam_worker.last_recognitions})
    except Exception:
        return jsonify({'recognitions': []})


# Attendance callback to integrate worker recognitions into attendance table
def _attendance_callback(rec, subject_id, session_id):
    try:
        sid = rec.get('student_id')
        if not sid or not subject_id:
            return
        # check today's record
        today = datetime.now().date()
        existing = Attendance.query.filter_by(student_id=sid, subject_id=subject_id, date=today).first()
        if existing:
            # update timestamp if already present
            existing.status = 'present'
            existing.timestamp = datetime.utcnow()
        else:
            attendance = Attendance(student_id=sid, subject_id=subject_id, date=today, status='present')
            db.session.add(attendance)

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
    subject_id = request.form.get('subject_id')
    session_id = request.form.get('session_id')
    try:
        cam_worker.active_subject = int(subject_id) if subject_id else None
        cam_worker.active_session = int(session_id) if session_id else None
        # register callback
        cam_worker.attendance_callback = _attendance_callback
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/export_attendance')
@login_required
def export_attendance():
    """Export attendance as CSV or Excel.

    Query params:
      - subject_id (optional)
      - date (YYYY-MM-DD) optional; defaults to today
      - format: 'csv' (default) or 'xlsx'
    """
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
            pass

    rows = q.all()

    # Build CSV in-memory
    if fmt == 'csv' or not HAVE_OPENPYXL:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['student_id', 'student_name', 'roll_number', 'subject_id', 'subject_name', 'date', 'status', 'timestamp', 'snapshot'])
        for r in rows:
            try:
                student = Student.query.get(r.student_id)
                subject = Subject.query.get(r.subject_id)
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
                continue

        output.seek(0)
        return Response(output.getvalue(), mimetype='text/csv', headers={
            'Content-Disposition': f'attachment; filename=attendance_{date_obj.isoformat()}.csv'
        })

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
        for r in rows:
            try:
                student = Student.query.get(r.student_id)
                subject = Subject.query.get(r.subject_id)
                snapshot_file = ''
                if os.path.isdir(snaps_dir):
                    for f in os.listdir(snaps_dir):
                        if f.startswith(f"snap_{r.student_id}_"):
                            snapshot_file = f
                            break
                ws.append([r.student_id, student.name if student else '', student.roll_number if student else '', r.subject_id, subject.name if subject else '', r.date.isoformat(), r.status, r.timestamp.isoformat(), snapshot_file])
            except Exception:
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


# Debug-only route: list subjects known to the running app (JSON)
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
        return jsonify({
            'is_authenticated': bool(getattr(current_user, 'is_authenticated', False)),
            'id': getattr(current_user, 'id', None),
            'username': getattr(current_user, 'username', None)
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
    # Render the dashboard template with all subjects (bypasses login) for testing
    subs = Subject.query.all()
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
