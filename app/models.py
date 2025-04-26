from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
import json
import os
from sqlalchemy.sql import func

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profile_picture = db.Column(db.String(100), default='default.jpg')
    actual_cv = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    interviews = db.relationship('Interview', backref='user', lazy=True)
    cvs = db.relationship('CV', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Profession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    questions = db.relationship('Question', backref='profession', lazy=True)
    
    def __repr__(self):
        return f'<Profession {self.name}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=False)
    grade = db.Column(db.String(20), nullable=False)  # Junior, Middle, Senior
    question_text = db.Column(db.Text, nullable=False)
    
    answers = db.relationship('Answer', backref='question', lazy=True)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:30]}...>'

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=False)
    grade = db.Column(db.String(20), nullable=False)  # Junior, Middle, Senior
    overall_rating = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    answers = db.relationship('Answer', backref='interview', lazy=True)
    profession = db.relationship('Profession')
    
    def __repr__(self):
        return f'<Interview {self.id}: {self.profession.name} - {self.grade}>'

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    audio_path = db.Column(db.String(255), nullable=True)
    transcribed_text = db.Column(db.Text, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Answer {self.id} for Question {self.question_id}>'

class CV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    review = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CV {self.id}: {self.filename}>'