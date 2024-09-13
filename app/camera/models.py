from sqlalchemy import Column, String
from model_base import BareBaseModel


class Camera(BareBaseModel):
    name = Column(String(50), nullable=False)
    ip_address = Column(String(50), nullable=False)
    location = Column(String(100))

    def __repr__(self) -> str:
        return f'<Camera {self.id}>'

    @classmethod
    def create_camera(
            cls,
            name: str,
            ip_address: str,
            location: str,
    ) -> 'Camera':
        camera = cls(
            name=name,
            ip_address=ip_address,
            location=location,
        )
        camera.save()
        return camera

    @classmethod
    def get_all_cameras(cls):
        return cls.query.all()

    @classmethod
    def get_camera_by_id(cls, camera_id):
        return cls.query.get(camera_id)

    @classmethod
    def update_camera(cls, camera_id: int, data: dict):
        camera = cls.query.get(camera_id)
        if camera:
            for key, value in data.items():
                setattr(camera, key, value)
            camera.save()
            return camera
        return None

    @classmethod
    def delete_camera(cls, camera_id: int) -> bool:
        camera = cls.query.get(camera_id)
        if camera:
            camera.delete()
            return True
        return False
