from response import ResponseCreateUser, UserCreateBody, UserCreateResponse
from sqlalchemy.orm import Session
from models import Role
from database import get_db
from fastapi import APIRouter, status, HTTPException, Depends
from operations import add_user
router = APIRouter()

@router.post('/register-premium-user', status_code=201, response_model=ResponseCreateUser)
def regipreium(user: UserCreateBody, session: Session = Depends(get_db)):
    user = add_user(session=session, **user.model_dump(), role = Role.premium)
    if not user: 
        raise HTTPException(status_code=409)
    user_response = UserCreateResponse(
        username=user.username,
        email=user.email
    )
    return {
        "message": "user created",
        "user": user_response
    }
