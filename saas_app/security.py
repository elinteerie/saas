from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from models import User
from email_validator import (validate_email, EmailNotValidError)
from operations import pwd_context
from jose import jwt, JWTError
from operations import get_user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from database import get_db

def authenticate_user(session: Session, username_or_email: str, password: str) -> User | None:
    user = get_user(session, username_or_email)
    print(user)

    if not user or not pwd_context.verify(password, user.hashed_password):
        return 
    return user

load_dotenv()  



SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    print(to_encode)
    expire = datetime.utcnow() + timedelta(minutes =ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def decode_access_token(token: str, session: Session) -> User | None:
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        print(payload)
        username: str = payload.get('sub')
    except JWTError:
        return 
    if not username:
        return 
    user = get_user(session, username)
    return user

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post('/token', response_model=Token, responses ={
    status.HTTP_401_UNAUTHORIZED: {
        'description': "Incorrect username or password"
    }
})
def get_user_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    user = authenticate_user(session, form_data.username, form_data.password)
    print(form_data.username)
    if not user: 
        raise HTTPException(
            status_code=401,

        )
    access_token = create_access_token(data={"sub": user.username})
    return {
        'access_token': access_token,
        "token_type": "bearer"
    }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

@router.get('/users/me')
def read_user_me(
    token: str = Depends(oauth2_scheme), session:Session = Depends(get_db)
):
    user = decode_access_token(token, session)
    print(user)
    if not user:
        raise HTTPException(
            status_code=401
        )
    return {
        "description": f"{user.username} authorizzed"
    }