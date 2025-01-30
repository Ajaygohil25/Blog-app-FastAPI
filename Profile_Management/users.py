from datetime import timedelta
from urllib.request import Request
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response
from database import get_db
from mail import send_mail
from models import Users
from schemas import User_schema, User_login_schema, Token
from hashing import Hash
from tokon import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from constant import LOGIN_SUCCESS, LOGOIN_CONTENT, LOGIN_SUB

router = APIRouter()


@router.post("/create_user", tags=["users"])
def create_user(request_data: User_schema, response: Response, db: Session = Depends(get_db)):
    encrypted_password = Hash.encrypt(request_data.password)
    user_data = Users(
        name = request_data.name,
        email= request_data.email,
        password = encrypted_password
    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data

@router.post("/user_login", tags=["users"])
async def login_user(login_data: User_login_schema, db: Session = Depends(get_db)):
    input_email = login_data.email
    input_password = login_data.password
    user_data = db.query(Users).filter(Users.email == input_email).first()
    if user_data:
        if Hash.verify_password(input_password, user_data.password):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": input_email}, expires_delta=access_token_expires
            )
            await send_mail(input_email, LOGIN_SUB, LOGOIN_CONTENT)
            return Token(access_token=access_token, token_type="bearer")
        else:
            return "Invalid credentials"
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{input_email} not found in database")

# @router.post("/user/forgot_password", tags=["users"])
# async def forgot_password(request: Request, db: Session = Depends(get_db)):
#     pass