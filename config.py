import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret')
    
    # Database
    # Standardizing SQLite connection string for Vercel (read-only filesystem fix)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:////tmp/agritech.db')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads/')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10485760)) # 10MB limit
    
    # APIs
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # Models
    MODEL_PATH = os.environ.get('MODEL_PATH', 'models/')
