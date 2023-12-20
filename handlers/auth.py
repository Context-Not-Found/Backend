from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends

from dependencies.db import get_db
from controllers import auth
from schemas import user as user_schema


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=user_schema.User)
async def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    return await auth.create_user(user, db)


@router.post("/login", response_model=user_schema.UserLoginResp)
async def login_user(user: user_schema.UserLogin, db: Session = Depends(get_db)):
    return await auth.login_user(user, db)
