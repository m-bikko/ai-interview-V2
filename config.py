import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    CV_FOLDER = os.path.join(UPLOAD_FOLDER, 'cvs')
    PROFILE_PICS_FOLDER = os.path.join(UPLOAD_FOLDER, 'profile_pics')
    AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Default profile picture
    DEFAULT_PROFILE_PIC = 'default.jpg'
    
    # Google Gemini API settings
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GEMINI_MODEL = 'gemini-1.5-flash-latest'