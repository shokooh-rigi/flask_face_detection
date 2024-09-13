from .models import Camera
from .schemas import CameraSchema, CameraUpdateSchema
from concurrent.futures import ThreadPoolExecutor
from flask import current_app
import face_recognition as face_rec
from app.face_recognition.models import FaceEncoding, RecognitionLog
from app.user.models import User
from app.face_recognition.schemas import FaceRecognitionResponse
import logging
executor = ThreadPoolExecutor(max_workers=current_app.config.get('MAX_WORKERS', 5))


class CameraService:

    @staticmethod
    def create_camera(camera_schema: CameraSchema):
        return Camera.create_camera(
            name=camera_schema.name,
            ip_address=camera_schema.ip_address,
            location=camera_schema.location
        )

    @staticmethod
    def get_all_cameras():
        return Camera.get_all_cameras()

    @staticmethod
    def get_camera_by_id(camera_id):
        return Camera.get_camera_by_id(camera_id)

    @staticmethod
    def update_camera(camera_id: int, data: CameraUpdateSchema):
        data_dict = data.dict(exclude_unset=True)
        return Camera.update_camera(camera_id, data_dict)

    @staticmethod
    def delete_camera(camera_id):
        return Camera.delete_camera(camera_id)


def process_camera_feed(camera_id, image_bytes):
    """
    Process image from a camera feed.
    """
    try:
        face_recognition_handler = FaceRecognitionHandler(camera_id)
        file = FileStorage(stream=io.BytesIO(image_bytes), filename='image.jpg')
        encoding, filename = face_recognition_handler._process_face_image(file)

        if encoding is None:
            return {"error": "No face found in the image"}, 400

        user = face_recognition_handler._recognize_face(encoding)
        face_recognition_handler._create_recognition_log(user, filename)

        if current_app.config.get('USE_NX_WITNESS', False):
            face_recognition_handler._create_nx_bookmark(user, filename)

        if user:
            return FaceRecognitionResponse(
                message="Face recognized",
                user=f"{user.first_name} {user.last_name}"
            ).dict(), 200
        else:
            return {'message': 'Face not recognized'}, 200

    except Exception as e:
        logging.error(f"Error processing camera feed: {e}")
        return {'error': str(e)}, 500


def handle_camera_feed(camera_id, image_bytes):
    """
    Submit image processing to the executor.
    """
    future = executor.submit(process_camera_feed, camera_id, image_bytes)
    return future
