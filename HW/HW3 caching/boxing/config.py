import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///boxing.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

class ProductionConfig:
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_DOMAIN = None
    SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:////app/db/app.db")

class TestConfig:
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'

class DevelopmentConfig:
    """Development configuration."""
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def get_config(env):
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestConfig
    return DevelopmentConfig
