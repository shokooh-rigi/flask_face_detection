import os


class Config:
    """Base configuration."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'portraits')
    CAPTURED_FACES_PATH = os.path.join(os.getcwd(), 'uploads', 'face_capture')
    NX_WITNESS_URL = f"http://{os.getenv('NX_SERVER_IP')}:{os.getenv('NX_SERVER_PORT')}/rest/v2/devices/{{deviceId}}/bookmarks"
    NX_WITNESS_AUTH = (os.getenv('NX_AUTH_USER'), os.getenv('NX_AUTH_PASS'))
    NX_DEVICE_ID = os.getenv('NX_DEVICE_ID')
    NX_SERVER_ID = os.getenv('NX_SERVER_ID')
    CAMERA_IP = os.getenv('CAMERA_IP')
    NX_SERVER_IP = os.getenv('NX_SERVER_IP')
    NX_SERVER_PORT = os.getenv('NX_SERVER_PORT')
    NX_AUTH_USER = os.getenv('NX_AUTH_USER')
    NX_AUTH_PASS = os.getenv('NX_AUTH_PASS')
    USE_NX_WITNESS: bool = os.getenv('USE_NX_WITNESS', 'False').lower() in ['true', '1', 'yes']
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 5))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
