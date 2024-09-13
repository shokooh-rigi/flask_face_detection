import io
import json
import logging
import os
import time
from datetime import datetime, timezone

import face_recognition as face_rec
import requests
from flask import current_app
from pydantic import ValidationError
from werkzeug.datastructures import FileStorage

from app.face_recognition.models import FaceEncoding, RecognitionLog
from app.face_recognition.schemas import FaceRecognitionResponse
from app.user.models import User


class FaceRecognitionHandler:
    def __init__(self):
        pass

    @staticmethod
    def _process_face_image(file):
        """
        Process the uploaded face image and extract face encoding.
        """
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}.jpg"
        file_path = os.path.join(current_app.config['CAPTURED_FACES_PATH'], filename)
        file.save(file_path)
        logging.info(
            "Image saved at %s to %s",
            datetime.now(timezone.utc),
            file_path,
        )
        load_image_start = time.time()
        image = face_rec.load_image_file(file_path)
        face_encodings = face_rec.face_encodings(image)
        load_image_end = time.time()
        logging.info(
            "Image loaded and encoded in %f seconds",
            load_image_end - load_image_start,
        )
        if not face_encodings:
            return None, filename

        encoding = face_encodings[0]
        return encoding, filename

    @staticmethod
    def _recognize_face(encoding):
        """
        Recognize the face by comparing with known encodings.
        """
        known_faces = FaceEncoding.get_all_encodings()
        known_encodings = {face.user_id: face.get_face_encoding() for face in known_faces}

        for user_id, known_encoding in known_encodings.items():
            compare_start = time.time()
            matches = face_rec.compare_faces([known_encoding], encoding)
            compare_end = time.time()
            logging.info(
                "Face comparison for user %d took %f seconds",
                user_id,
                compare_end - compare_start,
            )
            if True in matches:
                return User.get_user_by_id(user_id)

        return None

    @staticmethod
    def _create_recognition_log(user, filename):
        """
        Create a recognition log entry in the database.
        """
        user_id = user.id if user else None
        return RecognitionLog.create_log(user_id=user_id, snapshot_filename=filename)

    @staticmethod
    def _create_nx_bookmark(user, filename):
        """
        Create a bookmark in NX Witness for the recognized face.
        """
        now_utc = int(time.time() * 1000)  # Convert current time to milliseconds
        payload = {
            "serverId": current_app.config['NX_SERVER_ID'],
            "name": "Face Recognized",
            "description": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "startTimeMs": now_utc,
            "durationMs": 1000,
            "tags": ["Face Recognition"],
            "creationTimeMs": now_utc
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            logging.debug("Sending bookmark request to NX Witness")
            response = requests.post(
                url=current_app.config['NX_WITNESS_URL'].format(deviceId=current_app.config['NX_DEVICE_ID']),
                headers=headers,
                data=json.dumps(payload),
                auth=current_app.config['NX_WITNESS_AUTH'],
                timeout=10,
                verify=False,
                allow_redirects=False
            )

            if response.status_code == 307:
                redirected_url = response.headers['Location']
                response = requests.post(
                    url=redirected_url,
                    headers=headers,
                    data=json.dumps(payload),
                    auth=current_app.config['NX_WITNESS_AUTH'],
                    timeout=10,
                    verify=False
                )

            if response.status_code == 200:
                logging.info("Bookmark created successfully: %s", response.json())
            else:
                logging.error(
                    "Failed to create bookmark: %d, %s",
                    response.status_code,
                    response.text,
                )
        except Exception as e:
            logging.error("Exception while creating bookmark: %s", e)

    def handle_face_recognition(self, file_bytes: bytes):
        """
        Main handler for processing face recognition requests.
        """
        try:
            file = FileStorage(stream=io.BytesIO(file_bytes), filename='image.jpg')
            encoding, filename = self._process_face_image(file)
            if encoding is None:
                return {"error": "No face found in the image"}, 400

            user = self._recognize_face(encoding)
            self._create_recognition_log(user, filename)

            if current_app.config.get('USE_NX_WITNESS', False):
                self._create_nx_bookmark(user, filename)

            if user:
                return FaceRecognitionResponse(
                    message="Face recognized",
                    user=f"{user.first_name} {user.last_name}"
                ).dict(), 200
            else:
                return {'message': 'Face not recognized'}, 200

        except ValidationError as e:
            return {'error': str(e)}, 400

        except Exception as e:
            return {'error': str(e)}, 500
