from datetime import datetime

import numpy as np
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, LargeBinary
from sqlalchemy.orm import relationship

from app.user.models import User
from model_base import BareBaseModel


class FaceEncoding(BareBaseModel):
    encoding = Column(LargeBinary, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey('user.id', ondelete='CASCADE'),
    )

    __table_args__ = (
        Index('idx_face_encoding_user_id', 'user_id'),
    )

    def get_face_encoding(self) -> np.ndarray:
        return np.frombuffer(self.encoding, dtype=np.float64)

    def __repr__(self) -> str:
        return f'<FaceEncoding {self.id}>'

    @classmethod
    def create_encoding(cls, user_id: int, encoding: bytes) -> 'FaceEncoding':
        face_encoding = cls(user_id=user_id, encoding=encoding)
        face_encoding.save()
        return face_encoding

    @classmethod
    def get_all_encodings(cls):
        return cls.query.all()


class RecognitionLog(BareBaseModel):
    timestamp = Column(DateTime, default=datetime.utcnow)
    snapshot_filename = Column(String(255))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    user = relationship("User", backref="recognition_logs")
    __table_args__ = (
        Index('idx_recognition_log_user_id', 'user_id'),
    )

    def __repr__(self) -> str:
        return f'<RecognitionLog {self.id}>'

    @classmethod
    def create_log(cls, user_id: int, snapshot_filename: str) -> 'RecognitionLog':
        log = cls(
            user_id=user_id,
            snapshot_filename=snapshot_filename,
        )
        log.save()
        return log

    @classmethod
    def get_all_logs_with_users(cls):
        return cls.query.join(User, cls.user_id == User.id).all()
