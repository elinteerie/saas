from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import get_db
from models import Role
from security import oauth2_scheme, decode_access_token


class UserRequestWithRole(BaseModel):
    username: str
    email: str
    role: Role



def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)) -> UserRequestWithRole:
    user = decode_access_token(token, session)
    if not user: 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not Authorrized")
    return UserRequestWithRole(
            username=user.username,
            email = user.email,
            role = user.role,
        )
    

def get_premium_usee(
        current_user: Annotated[
            get_current_user, Depends()
        ]

):
    if current_user.role != Role.premium:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not Premuum so UNAuthorized"
        )
    return current_user


router = APIRouter()

@router.get('/welcome/all-users')
def all_user_can_access(
    user: Annotated[get_current_user, Depends()]
):
    return {
        f"Hello {user.username}",
        "Welcome to Site"
    }


@router.get('/welcome/premium_user')
def only_premium(user: UserRequestWithRole = Depends(get_premium_usee)):
    return {
        f" Hello Premium {user.username}",
        "THis is the Preium User"
    }