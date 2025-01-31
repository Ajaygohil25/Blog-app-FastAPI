from typing import Optional, List
from pydantic import BaseModel

class Blog_schema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class User_schema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class User_login_schema(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

class TokenData(BaseModel):
    email: str | None = None
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    class Config:
        from_attributes = True

class ResetPassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    class Config:
        from_attributes = True

class ForgotPassword(BaseModel):
    new_password: str
    confirm_password: str
    class Config:
        from_attributes = True

class UserMail(BaseModel):
    email: str
