from datetime import datetime
from typing import Optional, List, Any
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
    image_url: str
    class Config:
        from_attributes = True

class LikeResponse(BaseModel):
    user_name : str

    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: int
    commented_by: str
    comment: str
    reply_by: Optional[str] = None
    reply: Optional[str] = None

    class Config:
        from_attributes = True

class BlogsResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    images: List
    likes: List
    liked_by_you: bool
    total_likes: int # Only the last three likes
    view_all_likes: str
    comments: List
    total_comments: int
    view_all_comments: str

    class Config:
        from_attributes = True

class CommentSchema(BaseModel):
    comment: str

class ReplyComment(BaseModel):
    reply : str

