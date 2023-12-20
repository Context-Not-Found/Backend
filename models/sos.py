from typing import Dict, List
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    BOOLEAN,
)
from configuration.database import Base

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import ticket
from schemas import sos as sos_schema


class SOS(Base):
    __tablename__ = "sos"
    sos_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    lat = Column(Float(precision=53), nullable=False)
    long = Column(Float(precision=53), nullable=False)
    is_open = Column(BOOLEAN, default=True, nullable=False)


async def get_open_sos_for_user_id(db: Session, user_id: int):
    try:
        return (
            db.query(SOS)
            .filter(SOS.user_id == user_id)
            .filter(SOS.is_open == True)
            .first()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def create_sos(db: Session, sos: sos_schema.SOSCreate, user_id: int):
    try:
        sos = SOS(user_id=user_id, lat=sos.lat, long=sos.long, is_open=True)
        db.add(sos)
        db.commit()
        db.refresh(sos)
        return sos
    except Exception as exc:
        # Handle any other unexpected errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def close_sos(db: Session, sos_id: Column[int] | int):
    try:
        id = db.query(SOS).filter(SOS.sos_id == sos_id).update({"is_open": False})
        db.commit()
        return id
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def get_sos(db: Session):
    try:
        return db.query(SOS).filter(SOS.is_open == True).all()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def get_all_coords(db: Session):
    try:
        soss = db.query(SOS).all()
        reports = db.query(ticket.TicketReport).all()

        coords: List[Dict[str, float]] = []
        for sos in soss:
            coord = {"latitude": float(str(sos.lat)), "longitude": float(str(sos.long))}
            coords.append(coord)

        for report in reports:
            coord = {
                "latitude": float(str(report.lat)),
                "longitude": float(str(report.long)),
            }
            coords.append(coord)

        return coords
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
