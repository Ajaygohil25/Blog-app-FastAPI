# from passlib.context import CryptContext
from passlib.context import CryptContext

class Hash():
    def encrypt(password: str):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    def verify_password(input_passwod: str, hashed_password: str):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(input_passwod, hashed_password)