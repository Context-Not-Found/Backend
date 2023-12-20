from contextlib import contextmanager
from datetime import datetime, timedelta
import os
import bcrypt
from jose import jwt
import socketio
from sqlalchemy.orm import Session
from sqlalchemy.schema import Column
from dependencies.db import get_db
from models import user as user_model


sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)


SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = os.environ["JWT_ALGORITHM"]
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()
print(SECRET_KEY, ALGORITHM)
print()
print()
print()
print()
print()
print()
print()
print()
print()


async def authenticate_user(db: Session, email: str, password: str):
    user = await user_model.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def verify_password(password: str, hashed_password: Column[str]):
    return bcrypt.checkpw(
        password.encode("utf-8"), str(hashed_password).encode("utf-8")
    )


def decode_token(token: str):
    payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return payload


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


get_db_manager = contextmanager(get_db)
