from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile, File
from pydantic import BaseModel


class BlogSchema(BaseModel):
    title: str
    content: str
    images: Optional[List[UploadFile]] = File(None)

class UpdateBlogImage(BaseModel):
    images: List[UploadFile]

class UserSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserLoginSchema(BaseModel):
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

class ImageResponse(BaseModel):
    id: int
    image_name: str
    class Config:
        from_attributes = True

class LikeResponse(BaseModel):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: int
    comment: str
    reply: Optional[str] = None
    user_id: int

    class Config:
        from_attributes = True

class BlogsResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: str
    images: List[ImageResponse]
    last_likes: List[LikeResponse]   # Only the last three likes
    comments: List[CommentResponse]

    class Config:
        from_attributes = True

class CommentSchema(BaseModel):
    comment: str

class ReplyComment(BaseModel):
    reply : str

