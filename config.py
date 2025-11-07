"""
Production-ready configuration management
"""
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""

    # Application root directory
    BASE_DIR = Path(__file__).parent.absolute()

    # Google AI Configuration
    GOOGLE_GENAI_USE_VERTEXAI = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '0') == '1'
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))

    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # Frontend Configuration
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'backend/nutrition_app.db')

    # Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'backend/uploads')
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', 16))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert to bytes
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', '1') == '1'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

    # Security
    SESSION_COOKIE_SECURE = FLASK_ENV == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # 24 hours

    @classmethod
    def validate(cls):
        """Validate critical configuration values"""
        errors = []

        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is not set")

        if cls.FLASK_ENV == 'production' and cls.SECRET_KEY == secrets.token_hex(32):
            errors.append("SECRET_KEY must be explicitly set in production (not auto-generated)")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors))

        return True


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    FLASK_ENV = 'development'
    FLASK_DEBUG = True
    ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:5000', 'http://127.0.0.1:3000', 'http://127.0.0.1:5000']


class ProductionConfig(Config):
    """Production-specific configuration"""
    FLASK_ENV = 'production'
    FLASK_DEBUG = False

    @classmethod
    def validate(cls):
        """Additional production validation"""
        super().validate()

        errors = []

        if 'localhost' in cls.FRONTEND_URL or '127.0.0.1' in cls.FRONTEND_URL:
            errors.append("FRONTEND_URL should not be localhost in production")

        if any('localhost' in origin or '127.0.0.1' in origin for origin in cls.ALLOWED_ORIGINS):
            errors.append("ALLOWED_ORIGINS should not include localhost in production")

        if errors:
            raise ValueError("Production configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors))

        return True


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'production')

    if env == 'development':
        return DevelopmentConfig
    else:
        return ProductionConfig


# Export the active configuration
active_config = get_config()
