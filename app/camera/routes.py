from flask import Blueprint, request
from pydantic import ValidationError

from .schemas import CameraSchema, CameraUpdateSchema
from .services import CameraService
from ..utils import format_response

camera_bp = Blueprint('camera_bp', __name__)


@camera_bp.route('/cameras', methods=['POST'])
def create_camera():
    try:
        camera_data = request.json
        camera_schema = CameraSchema(**camera_data)
        result = CameraService.create_camera(
            camera_schema=camera_schema
        )
        return format_response(
            data=result.to_dict(),
            message="Camera created successfully",
            status_code=201,
        )
    except ValidationError as e:
        return format_response(
            data={'errors': e.errors()},
            message="Validation Error",
            status_code=422,
        )
    except Exception as e:
        return format_response(
            data={},
            message=str(e),
            status_code=500,
        )


@camera_bp.route('/cameras/<int:camera_id>', methods=['PUT'])
def update_camera(camera_id):
    try:
        camera_update_data = request.json
        data = CameraUpdateSchema(**camera_update_data)
        result = CameraService.update_camera(
            camera_id=camera_id,
            data=data,
        )
        return format_response(
            data=result.to_dict(),
            message="Camera updated successfully",
            status_code=200,
        )
    except ValidationError as e:
        return format_response(
            data={'errors': e.errors()},
            message="Validation Error",
            status_code=422,
        )
    except Exception as e:
        return format_response(
            data={},
            message=str(e),
            status_code=500,
        )


@camera_bp.route('/cameras/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    try:
        result = CameraService.delete_camera(camera_id)
        return format_response(
            data=result,
            message="Camera deleted successfully",
            status_code=204,
        )
    except Exception as e:
        return format_response(
            data={},
            message=str(e),
            status_code=500,
        )


@camera_bp.route('/cameras', methods=['GET'])
def get_all_cameras():
    try:
        cameras = CameraService.get_all_cameras()
        return format_response(
            data=[camera.to_dict() for camera in cameras],
            message="Cameras retrieved successfully",
            status_code=200,
        )
    except Exception as e:
        return format_response(
            data={},
            message=str(e),
            status_code=500,
        )

