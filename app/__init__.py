
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_executor import Executor
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
executor = Executor()


def create_app():
    app = Flask(
        __name__,
        static_folder='../',
        static_url_path='/',
    )

    # Setup logging
    log_dir = os.path.join(
        os.getcwd(),
        'logs',
    )
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(
        log_dir,
        f'face_engine_{datetime.now().strftime("%Y%m%d")}.log',
    )
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s',
    )

    logging.debug("Starting the create_app function")

    exe_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(exe_dir, '.env')
    if os.path.exists(env_path):
        logging.info(f"Loading .env file from: {env_path}")
        load_dotenv(env_path)
    else:
        logging.error(f".env file not found at: {env_path}")

    for key, value in os.environ.items():
        logging.debug(f'{key}: {value}')

    try:
        app.config.from_object(os.getenv('APP_SETTINGS', 'config.DevelopmentConfig'))
        logging.debug(f"App settings loaded: {os.getenv('APP_SETTINGS', 'config.DevelopmentConfig')}")
    except Exception as e:
        logging.error(f"Error loading app settings: {e}")

    try:
        if not app.config['SQLALCHEMY_DATABASE_URI']:
            logging.error("SQLALCHEMY_DATABASE_URI is not set.")
            raise RuntimeError("Either 'SQLALCHEMY_DATABASE_URI' or 'SQLALCHEMY_BINDS' must be set.")
        db.init_app(app)
        logging.debug("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

    try:
        executor.init_app(app)
        logging.debug("Executor initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing executor: {e}")

    try:
        CORS(app)
        logging.debug("CORS initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing CORS: {e}")

    # Create directories if they don't exist
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['CAPTURED_FACES_PATH'], exist_ok=True)
        logging.debug("Upload directories created successfully")
    except Exception as e:
        logging.error(f"Error creating upload directories: {e}")
    try:
        with app.app_context():
            from app.camera.routes import camera_bp
            from app.face_recognition.routes import face_recognition_bp
            from app.user.routes import user_bp
            app.register_blueprint(user_bp)
            app.register_blueprint(camera_bp)
            app.register_blueprint(face_recognition_bp)
            db.create_all()
            logging.debug("Blueprints registered and database tables created successfully")
    except Exception as e:
        logging.error(f"Error during app context: {e}")

    logging.info("App created successfully")
    return app
