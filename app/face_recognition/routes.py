import logging
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, request, current_app

from app.face_recognition.services import FaceRecognitionHandler, handle_camera_feed
from app.utils import format_response

face_recognition_bp = Blueprint('face_recognition', __name__)

logging.basicConfig(level=logging.INFO)

max_workers = current_app.config.get('MAX_WORKERS', 5)
executor = ThreadPoolExecutor(max_workers=max_workers)


@face_recognition_bp.route('/api/receive', methods=['POST'])
def face_recognition_route():
    """
    Handle face recognition requests by processing the uploaded image file.
    """
    if 'faceImage' not in request.files:
        return format_response(
            data={"error": "No face image provided"},
            message="Bad Request",
            status_code=400,
        )

    file = request.files['faceImage']
    file_bytes = file.read()

    try:
        future = executor.submit(lambda: FaceRecognitionHandler().handle_face_recognition(file_bytes))
        response_data, status_code = future.result()
        return format_response(
            data=response_data,
            message="Face recognition completed",
            status_code=status_code,
        )
    except Exception as e:
        logging.error(f"Error processing face recognition request: {e}")
        return format_response(
            data={"error": "Internal Server Error"},
            message="Internal Server Error",
            status_code=500,
        )


@face_recognition_bp.route('/api/cameras/<int:camera_id>/recognize', methods=['POST'])
def recognize_faces_from_camera(camera_id):
    """
    Handle face recognition requests for a specific camera.
    """
    if 'faceImage' not in request.files:
        return format_response(
            data={"error": "No face image provided"},
            message="Bad Request",
            status_code=400,
        )

    file = request.files['faceImage']
    file_bytes = file.read()

    try:
        future = executor.submit(lambda: handle_camera_feed(camera_id, file_bytes))
        response_data, status_code = future.result()
        return format_response(
            data=response_data,
            message="Face recognition completed",
            status_code=status_code,
        )
    except Exception as e:
        logging.error(f"Error processing face recognition request from camera {camera_id}: {e}")
        return format_response(
            data={"error": "Internal Server Error"},
            message="Internal Server Error",
            status_code=500,
        )
