from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    expires_in: int

class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    class Config:
        from_attributes = True
