from pydantic import BaseModel
from typing import Optional


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    expires_in: int
    user_id: Optional[str] = None


class AuthContract:
    """Contract definitions for authentication API."""

    @staticmethod
    def validate_auth_request(data: dict) -> AuthRequest:
        return AuthRequest(**data)

    @staticmethod
    def validate_auth_response(data: dict) -> AuthResponse:
        return AuthResponse(**data)