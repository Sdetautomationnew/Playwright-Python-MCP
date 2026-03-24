from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: Optional[str] = None
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None