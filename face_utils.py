import cv2
import face_recognition
import json
import os
from flask import Flask, db
from app import app, Student

def encode_face_from_image(image_path):
    """Encode a face from an image file"""
    try:
        # Load image
        image = face_recognition.load_image_file(image_path)
        
        # Find face encodings
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) > 0:
            # Return the first face encoding
            return face_encodings[0].tolist()
        else:
            print(f"No face found in {image_path}")
            return None
            
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None

def update_student_face_encoding(student_id, image_path):
    """Update student's face encoding in database"""
    with app.app_context():
        student = Student.query.get(student_id)
        if student:
            encoding = encode_face_from_image(image_path)
            if encoding:
                student.face_encoding = json.dumps(encoding)
                db.session.commit()
                print(f"Face encoding updated for student: {student.name}")
                return True
            else:
                print(f"Failed to encode face for student: {student.name}")
                return False
        else:
            print(f"Student with ID {student_id} not found")
            return False

def batch_encode_faces_from_folder(folder_path):
    """Batch encode faces from images in a folder"""
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist")
        return
    
    with app.app_context():
        students = Student.query.all()
        
        for student in students:
            # Look for image file with student's roll number
            image_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg')) 
                          and student.roll_number in f]
            
            if image_files:
                image_path = os.path.join(folder_path, image_files[0])
                print(f"Processing {student.name} ({student.roll_number})...")
                update_student_face_encoding(student.id, image_path)
            else:
                print(f"No image found for {student.name} ({student.roll_number})")

if __name__ == "__main__":
    print("Face Recognition Utility")
    print("======================")
    print()
    print("1. Encode single face")
    print("2. Batch encode from folder")
    print()
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        student_id = int(input("Enter student ID: "))
        image_path = input("Enter image path: ")
        update_student_face_encoding(student_id, image_path)
        
    elif choice == "2":
        folder_path = input("Enter folder path containing student images: ")
        batch_encode_faces_from_folder(folder_path)
        
    else:
        print("Invalid choice")
