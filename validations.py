import re

from fastapi import HTTPException

from constant import INVALID_EMAIL, INVALID_PASSWORD


def validate_email(email: str):
    """ This method validate email input"""
    if not re.fullmatch(r'^[\w.-]+@[\w.-]+\.\w{2,4}$', email):
        return False
    return True
def validate_password(password: str):
    """ This method validate password."""
    if not re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        return False
    return True

def validate_input(values):
    if not validate_email(values.email):
        raise HTTPException(status_code=400, detail=INVALID_EMAIL)
    if not validate_password(values.password):
        raise HTTPException(status_code=400, detail=INVALID_PASSWORD)
    return values