import os
from dotenv import load_dotenv
load_dotenv
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2
from sqlalchemy.orm import Session
from models import User
from operations import get_user
from database import get_db


CLIENT_ID = os.getenv("GITHUB_ID")
CLIENT_SECRET =os.getenv('GITHUB_CLIENT_SECRET')

GITHUB_REDIRECT_URI = (
 "http://localhost:8000/github/auth/token"
)
GITHUB_AUTHORIZATION_URL = (
 "https://github.com/login/oauth/authorize"
)

def resolve_github_token(access_token: str = Depends(OAuth2()),
                         session: Session =Depends(get_db)   
                         ) -> User:
    user_response = httpx.get('https://api.github.com/user', headers={"Authorization": access_token},).json()
    username = user_response.get("login", " ")
    user = get_user(session, username)
    if not user:
        email = user_response.get('email', " ")
        print(email)
        user = get_user(session, email)
    if not user:
        raise HTTPException(status_code=403, detail="Token not vaild")
    return user
