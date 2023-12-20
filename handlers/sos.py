from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dependencies.db import get_db
from controllers import sos
from schemas import UpdateResponse, sos as sos_schema


router = APIRouter(
    prefix="/sos",
    tags=["SOS"],
)


@router.post("/create", response_model=sos_schema.SOS)
async def create_sos(request: sos_schema.SOSCreate, db: Session = Depends(get_db)):
    return await sos.create_sos(request, db)


@router.patch("/close/", response_model=UpdateResponse)
async def close_sos(
    user_id: Annotated[
        int,
        Query(title="User ID", description="ID of the User"),
    ],
    db: Session = Depends(get_db),
):
    id = await sos.close_sos(user_id, db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"respone": f"success, updated id ${id}"}),
    )


@router.get("/", response_model=List[sos_schema.SOS])
async def get_sos(db: Session = Depends(get_db)):
    return await sos.get_sos(db)
