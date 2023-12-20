from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import utils
from models import user
from schemas import user as user_schema


async def create_user(userSchema: user_schema.UserCreate, db: Session):
    db_user = await user.get_user_by_email(db, email=userSchema.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )

    if len(userSchema.phone_number) != 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Phone Number invalid"
        )

    return user.create_user(db=db, user=userSchema)


async def login_user(userSchema: user_schema.UserLogin, db: Session):
    db_user = await user.get_user_by_email(db, email=userSchema.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not registered"
        )

    # check if password matches
    if not utils.verify_password(userSchema.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User credentials invalid",
        )

    return db_user
