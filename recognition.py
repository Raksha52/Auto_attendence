import json
import numpy as np
try:
    import face_recognition
    FACE_RECOG_AVAILABLE = True
except Exception:
    FACE_RECOG_AVAILABLE = False


def load_student_encodings(db_session, Student):
    """Load encodings from DB into a list of (student_id, name, encoding)"""
    students = Student.query.all()
    encs = []
    for s in students:
        if s.face_encoding:
            try:
                arrs = json.loads(s.face_encoding)
                for e in arrs:
                    encs.append((s.id, s.name, np.array(e)))
            except Exception:
                continue
    return encs


def recognize_face(face_rgb, known_encodings, threshold=0.6):
    """Recognize using face_recognition compare_faces if available.
    known_encodings: list of (student_id, name, encoding)
    Returns best match or None
    """
    if not FACE_RECOG_AVAILABLE:
        return None, None, None

    try:
        enc = face_recognition.face_encodings(face_rgb)
        if not enc:
            return None, None, None
        enc = enc[0]
        dists = []
        for sid, name, ke in known_encodings:
            try:
                d = np.linalg.norm(ke - enc)
            except Exception:
                d = 1e6
            dists.append((d, sid, name))
        dists.sort()
        best = dists[0]
        if best[0] <= threshold:
            return best[1], best[2], float(best[0])
    except Exception:
        return None, None, None
    return None, None, None
