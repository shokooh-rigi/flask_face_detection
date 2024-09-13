from typing import Optional
from pydantic import BaseModel


class FaceRecognitionResponse(BaseModel):
    message: str
    user: Optional[str]
