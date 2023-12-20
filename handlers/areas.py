from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from dependencies.db import get_db
from controllers import areas
from schemas import areas as areas_schema


router = APIRouter(
    prefix="/areas",
    tags=["HeatMap"],
)


@router.get("/", response_model=areas_schema.Markers)
async def get_areas(db: Session = Depends(get_db)):
    markers = await areas.get_areas(db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"markers": markers}),
    )
