from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine
from models import Base
from database import get_db
from response import UserCreateBody, UserCreateResponse, ResponseCreateUser
from operations import add_user
import security
import premium_access
import rbac

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="SAAS Application", lifespan=lifespan)
app.include_router(security.router)
app.include_router(premium_access.router)
app.include_router(rbac.router)

@app.post('/register/user', status_code=status.HTTP_201_CREATED, response_model=ResponseCreateUser, responses={
    status.HTTP_409_CONFLICT: {
        'description': "The User already exist"
    }
}
)
def register(user: UserCreateBody, session: Session= Depends(get_db)):
    user = add_user(session=session, **user.model_dump())
    if not user:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username or email already exist")
    user_response = UserCreateResponse(username =user.username, email=user.email)
    return {
        "message": "user createda",
        "user": user_response
    }

