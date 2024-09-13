import os

from werkzeug.datastructures import FileStorage

from app.face_recognition.models import FaceEncoding, RecognitionLog
from app.user.models import User
from app.user.schemas import UserCreateRequest, UserResponse, UserLoginRequest
from app.utils import encode_face, save_portrait


def handle_login(user_login_data: UserLoginRequest):
    """
    مدیریت درخواست ورود.
    """
    if user_login_data.username == os.getenv('ADMIN_USERNAME') and user_login_data.password == os.getenv('ADMIN_PASSWORD'):
        return {'message': 'Login successful', 'status_code': 200}
    else:
        return {'message': 'Invalid credentials', 'status_code': 401}
            

def handle_get_users():
    """
    دریافت لیست کاربران.
    """
    users = User.get_all_users()
    users_list = [UserResponse.from_orm(user).dict() for user in users]

    return {'users': users_list, 'status_code': 200}


def handle_create_user(
        user_data: UserCreateRequest,
        portrait: FileStorage,
):
    """
    ایجاد یک کاربر جدید.
    """
    try:
        portrait_path = save_portrait(portrait=portrait)
    except Exception as e:
        return {'error': f'Failed to save portrait: {e}', 'status_code': 500}

    user, error = User.create_user(
        user_data=user_data,
        portrait_path=portrait_path,
    )
    if error:
        return {'error': error, 'status_code': 400}

    try:
        user_encoding = encode_face(portrait_path)
        FaceEncoding.create_encoding(
            user_id=user.id,
            encoding=user_encoding.tobytes(),
        )
    except Exception as e:
        return {'error': f'Failed to encode face: {e}', 'status_code': 500}

    return {'status_code': 201}


def handle_get_recognition_logs():
    """
    دریافت لیست لاگ‌های شناسایی.
    """
    logs = RecognitionLog.get_all_logs_with_users()
    logs_list = []
    for log in logs:
        logs_list.append({
            'id': log.id,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'recognized_user': {
                'first_name': log.user.first_name if log.user else None,
                'last_name': log.user.last_name if log.user else None,
            } if log.user else None,
            'image_path': log.snapshot_filename
        })
    return {'logs_list': logs_list, 'status_code': 200}

