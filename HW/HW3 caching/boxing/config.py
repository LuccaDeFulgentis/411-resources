import os

class ProductionConfig():
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = False  # Needless to say, don't do this
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_DOMAIN = None
    SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")  # Default secret key for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Docker-compatible database path with fallback
    if os.environ.get('DOCKER_ENV') == '1':
        SQLALCHEMY_DATABASE_URI = 'sqlite:////app/db/app.db'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'

class TestConfig():
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for tests
