from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# Association table for many-to-many relationship between students and courses
student_course = db.Table('student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    short_desc = db.Column(db.String(300))
    content = db.Column(db.Text)
    price = db.Column(db.Float, default=0.0)
    image = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    featured = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Course {self.title}>'

from flask_login import UserMixin

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_avatar(self):
        from flask import url_for
        if self.profile_picture:
            return url_for('uploads', filename=self.profile_picture)
        return f"https://ui-avatars.com/api/?name={self.name.replace(' ', '+')}&background=random"

    def __repr__(self):
        return f'<Student {self.name}>'

# Add relationship to Course after both classes are defined
Course.students = db.relationship('Student', secondary=student_course, backref=db.backref('courses', lazy='dynamic'))

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    course = db.relationship('Course', backref=db.backref('testimonials', lazy='dynamic'))

    def __repr__(self):
        return f'<Testimonial {self.student_name}>'

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    timestamps = db.Column(db.Text)  # JSON format
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    course = db.relationship('Course', backref=db.backref('videos', lazy='dynamic', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Video {self.title}>'

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    questions = db.Column(db.Text, nullable=False)  # JSON format
    scheduled_date = db.Column(db.DateTime)
    exam_type = db.Column(db.String(50), default='post_lecture') # monthly, post_lecture
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    course = db.relationship('Course', backref=db.backref('exams', lazy='dynamic', cascade="all, delete-orphan"))

    def get_questions(self):
        try:
            return json.loads(self.questions)
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self):
        return f'<Exam {self.title}>'