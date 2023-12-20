from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dependencies.auth import get_authorization, get_current_user
from dependencies.db import get_db
from controllers import sos
from schemas import UpdateResponse, sos as sos_schema, user as user_schema


router = APIRouter(
    prefix="/sos",
    tags=["SOS"],
)


@router.post("/create", response_model=sos_schema.SOS)
async def create_sos(
    request: sos_schema.SOSCreate,
    user: Annotated[user_schema.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    return await sos.create_sos(request, user, db)


@router.patch("/close/", response_model=UpdateResponse)
async def close_sos(
    user_id: Annotated[int, Depends(get_authorization)],
    db: Session = Depends(get_db),
):
    id = await sos.close_sos(user_id, db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"respone": f"success, updated id ${id}"}),
    )


@router.get("/", response_model=List[sos_schema.SOS])
async def get_sos(
    _: Annotated[int, Depends(get_authorization)], db: Session = Depends(get_db)
):
    return await sos.get_sos(db)
