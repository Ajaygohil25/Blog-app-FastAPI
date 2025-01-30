from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from core.schemas import User_schema
from repository import userRepo
from repository.userRepo import add_user

router = APIRouter(
    tags=["users"],
)

@router.post("/user/sing-up")
def create_user(request_data: User_schema, db: Session = Depends(get_db)):
    return add_user(request_data, db)

@router.post("/user/sing-in")
async def login_admin(
        background_tasks: BackgroundTasks,
        login_data:Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)):
   return await userRepo.user_login(login_data, db, background_tasks)
