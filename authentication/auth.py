from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from repository import userRepo

router = APIRouter(
    tags= ["Authentication"]
)
# admin login
@router.post("/token")
def login_admin(login_data:Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
   return userRepo.user_login(login_data, db)