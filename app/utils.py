import os
from typing import Optional

import numpy as np
from flask import current_app, jsonify
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

import face_recognition as face_rec


def format_response(
        data,
        message: str = '',
        status_code: int = 200,
):
    return jsonify({
        'status': status_code,
        'message': message,
        'data': data
    }), status_code


def encode_face(image_path: str) -> np.ndarray:
    """
    Extracts facial encodings from an image file.

    Args:
        image_path (str): The path to the image file.

    Returns:
        np.ndarray: The encoding of the face found in the image.

    Raises:
        ValueError: If no face is found in the image.
        FileNotFoundError: If the image file does not exist.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"The file at {image_path} does not exist.")

    image = face_rec.load_image_file(image_path)
    encodings = face_rec.face_encodings(image)

    if encodings:
        return encodings[0]
    else:
        raise ValueError("No face found in the image.")


def save_portrait(portrait: Optional[FileStorage]) -> str:

    try:
        filename = secure_filename(portrait.filename)
        portrait_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        portrait.save(portrait_path)
        return portrait_path
    except Exception as e:
        raise RuntimeError(f'Failed to save portrait: {e}')


