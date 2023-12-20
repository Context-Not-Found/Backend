from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dependencies.db import get_db
from schemas import token as token_schema
from models import user as user_model
from utils import Session, decode_token


security = HTTPBearer(
    bearerFormat="JWT", scheme_name="bearer", description="JWT Token for authorization"
)

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# Route Dependency to extract token from the header and return the associating user
async def get_authorization(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise _credentials_exception
        token_data = token_schema.TokenData(user_id=user_id)
    except Exception:
        raise _credentials_exception
    return token_data.user_id


async def get_current_user(
    user_id: Annotated[int, Depends(get_authorization)],
    db: Session = Depends(get_db),
):
    user = await user_model.get_user(db, user_id)
    if user is None:
        raise _credentials_exception
    return user
