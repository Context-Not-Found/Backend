from datetime import timedelta
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
    user = await utils.authenticate_user(db, userSchema.email, userSchema.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Generate Access Token for 7 Days
    access_token = utils.create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=timedelta(weeks=1)
    )

    user_dict = user.__dict__
    user_dict.update({"token": {"access_token": access_token, "token_type": "bearer"}})
    return user_dict
