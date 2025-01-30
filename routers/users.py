from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.schemas import User_schema, User_login_schema
from repository.userRepo import add_user, user_login

router = APIRouter(
    tags=["users"],
)


@router.post("/user/create_user")
def create_user(request_data: User_schema, db: Session = Depends(get_db)):
    return add_user(request_data, db)

@router.post("/user/user_login")
async def login_user(login_data: User_login_schema, db: Session = Depends(get_db)):
    return user_login(login_data, db)
