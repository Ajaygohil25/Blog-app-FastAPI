from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from authentication.oauth2 import get_current_user, oauth2_scheme
from core.database import get_db
from core.schemas import User_schema, TokenData, ResetPassword, ForgotPassword, UserMail
from repository import userRepo
from repository.userRepo import add_user, reset_user_password, forgot_user_password, logout_current_user, \
    reset_forgot_user_password

router = APIRouter(
    tags=["users"],
)

@router.post("/user/sing-up")
def create_user(request_data: User_schema, db: Session = Depends(get_db)):
    return add_user(request_data, db)

@router.post("/user/sing-in")
async def login_user(
        background_tasks: BackgroundTasks,
        login_data:Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)):
   return await userRepo.user_login(login_data, db, background_tasks)

@router.patch("/user/reset-password")
async def reset_password(
        token: Annotated[str, Depends(oauth2_scheme)],
        request_data: ResetPassword,
        current_user: TokenData  = Depends(get_current_user),
        db: Session = Depends(get_db)):
    return reset_user_password(token,request_data, current_user.email, db)
@router.post("/user/forgot-password")
async def forgot_password(
                        request_data: UserMail,
                        background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db),):
    return forgot_user_password(request_data, background_tasks, db)

@router.post("/user/reset-forgot-password")
async def reset_forgot_password(request_data: ForgotPassword, token,db: Session = Depends(get_db)):
    return reset_forgot_user_password(request_data, token, db)
@router.post("/user/logout")
def logout_user(token: Annotated[str, Depends(oauth2_scheme)], current_user: TokenData  = Depends(get_current_user)):
    return logout_current_user(token)

