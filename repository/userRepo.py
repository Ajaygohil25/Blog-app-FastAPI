from datetime import timedelta
from http.client import HTTPException

from starlette import status

from constant import LOGIN_SUB, LOGOIN_CONTENT
from core.models import Users
from core.schemas import User_schema, Token
from mail.mail import send_mail
from authentication.hashing import Hash
from authentication.tokon import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token


def add_user(request_data: User_schema, db):
    """ This method add a new user """
    encrypted_password = Hash.encrypt(request_data.password)
    user_data = Users(
        name=request_data.name,
        email=request_data.email,
        password=encrypted_password
    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data

async def user_login(login_data, db):
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