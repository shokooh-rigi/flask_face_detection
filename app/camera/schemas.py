from typing import Optional
from pydantic import BaseModel


class CameraSchema(BaseModel):
    id: int
    name: str
    ip_address: str
    location: Optional[str]


class CameraUpdateSchema(BaseModel):
    name:  Optional[str]
    ip_address:  Optional[str]
    location: Optional[str]
