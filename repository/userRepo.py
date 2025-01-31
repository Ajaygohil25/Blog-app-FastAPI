from datetime import timedelta
from starlette import status
from fastapi import BackgroundTasks, HTTPException
from starlette.responses import JSONResponse
from authentication import token_management
from constant import LOGIN_SUB, LOGIN_CONTENT
from core.models import Users
from core.schemas import User_schema, Token
from mail.mail import send_mail
from authentication.hashing import Hash
from authentication.token_management import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    create_reset_password_token, verify_access_token


def add_user(request_data: User_schema, db):
    """ This method add a new user """
    encrypted_password = Hash.encrypt(request_data.password)
    user_data = Users(
        name = request_data.name,
        email = request_data.email,
        password = encrypted_password
    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data

async def user_login(login_data, db, background_tasks: BackgroundTasks):
    input_email = login_data.username
    input_password = login_data.password

    user_data = db.query(Users).filter(Users.email == input_email).first()
    if user_data:
        if Hash.verify_password(input_password, user_data.password):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": input_email}, expires_delta=access_token_expires
            )
            background_tasks.add_task(send_mail, input_email, LOGIN_SUB, LOGIN_CONTENT)
            return Token(access_token=access_token, token_type="bearer")
        else:
            return HTTPException(status_code = status.HTTP_401_UNAUTHORIZED)
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"{input_email} not found in database")

def get_user(email_id, db):
    user_data = db.query(Users).filter(Users.email == email_id).first()
    return user_data

def reset_user_password(token, request_data, email_id, db):
    user_data = get_user(email_id, db)
    if not request_data.new_password == request_data.confirm_password:\
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "new password and confirm password is not matching! Try again")

    if user_data and Hash.verify_password(request_data.current_password, user_data.password):
        updated_hash_password = Hash.encrypt(request_data.new_password)
        user_data.password = updated_hash_password
        db.commit()
        db.refresh(user_data)
        token_management.blacklist_token(token)
        return JSONResponse({"detail": "password changed successfully", "sing-in in app " : "http://127.0.0.1:8000/user/sing-in"})
    else:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "{Credential is unauthorized}")


def forgot_user_password(request_data,background_tasks, db):
        try:
            user_data = get_user(request_data.email, db)
            if not user_data:
                raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail = "Email id is not registered")

            secret_token = create_reset_password_token(request_data.email)
            forgot_password_link = f"http://127.0.0.1:8000/user/reset-forgot-password/?token={secret_token}"
            background_tasks.add_task(send_mail, request_data.email, "For forget password", forgot_password_link)

            return JSONResponse(status_code = status.HTTP_200_OK,
                                content = {"message": "Email has been sent for reset password", "success": True,
                                         "status_code": status.HTTP_200_OK})
        except Exception as e:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail = "Something Unexpected, Server Error")

def reset_forgot_user_password(request_data, token, db):
    token_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Token might be expired! ",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token,token_exception)
    if request_data.new_password == request_data.confirm_password:
        user_data = get_user(token_data.email, db)
        updated_hash_password = Hash.encrypt(request_data.new_password)
        user_data.password = updated_hash_password
        db.commit()
        db.refresh(user_data)
        token_management.blacklist_token(token)
        return JSONResponse(
            {"detail": "password changed successfully", "sing-in in app ": "http://127.0.0.1:8000/user/sing-in"})

    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="new password and confirm password is not matching! Try again")

def logout_current_user(token):
    token_management.blacklist_token(token)
    return JSONResponse(status_code = status.HTTP_200_OK,
                        content = {"message": "Logout Successfully",
                                 "sing-in in app " : "http://127.0.0.1:8000/user/sing-in"})
