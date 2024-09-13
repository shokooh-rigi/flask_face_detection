from typing import Optional, Tuple, List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean

from app.user.schemas import UserCreateRequest
from model_base import BareBaseModel

db = SQLAlchemy()


class User(BareBaseModel):

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15))
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    portrait_path = Column(String(255))

    def __repr__(self) -> str:
        return f'<User {self.email}>'

    @classmethod
    def create_user(
            cls,
            user_data: UserCreateRequest,
            portrait_path: Optional[str] = None,
    ) -> Tuple[Optional['User'], Optional[str]]:

        """
        Create a new user and save it to the database.

        :param user_data: Object containing user details.
        :param portrait_path: Optional path to the user's portrait.
        :return: Tuple containing the created user object and error message (if any).
        """
        if cls.query.filter_by(email=user_data.email).first():
            return None, 'Email already exists'

        user = cls(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone=user_data.phone,
            portrait_path=portrait_path
        )
        user.save()
        return user, None

    @classmethod
    def get_all_users(cls) -> List['User']:
        """
        Get a list of all users.

        :return: List of user objects.
        """
        return cls.query.all()

    @classmethod
    def get_user_by_id(cls, id: int) -> Optional['User']:
        return cls.query.filter_by(id=id).first()
