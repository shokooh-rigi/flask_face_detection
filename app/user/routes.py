import os

from flask import Blueprint, request, send_from_directory, current_app

from app.user.schemas import UserCreateRequest, RecognitionLogResponse, UserLoginRequest
from app.user.services import handle_get_users, handle_create_user, handle_get_recognition_logs, handle_login
from app.utils import format_response

user_bp = Blueprint(
    'user',
    __name__,
    static_folder='../static',
)


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_login_data = UserLoginRequest(**data)
    response_data = handle_login(user_login_data=user_login_data)
    return format_response(
        data=response_data,
        message="Login request processed",
        status_code=response_data.get('status_code', 200),
    )


@user_bp.route('/users', methods=['GET'])
def get_users():
    response_data = handle_get_users()
    return format_response(
        data=response_data,
        message="Users retrieved successfully",
        status_code=response_data.get('status_code', 200),
    )


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.form
    portrait = request.files.get('portrait')

    user_data = UserCreateRequest(**data)
    if not portrait:
        return format_response(
            data={'error': 'Portrait file is missing'},
            message="Bad Request",
            status_code=400,
        )

    response_data = handle_create_user(
        user_data=user_data,
        portrait=portrait,
    )
    return format_response(
        data=response_data,
        message="User created successfully",
        status_code=response_data.get('status_code', 201),
    )


@user_bp.route('/recognition-logs', methods=['GET'])
def get_recognition_logs():
    response_data = handle_get_recognition_logs()
    return format_response(
        data=response_data,
        message="Recognition logs retrieved successfully",
        status_code=response_data.get('status_code', 200),
    )


@user_bp.route('/uploads/portraits/<filename>')
def uploaded_portrait(filename):
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
    )


@user_bp.route('/uploads/face-capture/<filename>')
def uploaded_face_capture(filename):
    return send_from_directory(
        current_app.config['CAPTURED_FACES_PATH'],
        filename,
    )


@user_bp.route('/', defaults={'path': ''})
@user_bp.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(user_bp.static_folder, path)):
        return send_from_directory(user_bp.static_folder, path)
    else:
        return send_from_directory(user_bp.static_folder, 'index.html')
