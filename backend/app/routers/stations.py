from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/stations", tags=["台位管理"])


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_stations(db: Session = Depends(get_db)):
    stations = db.query(models.Station).order_by(models.Station.code).all()
    return schemas.ApiResponse(
        data={"items": [schemas.Station.model_validate(s).model_dump() for s in stations]}
    )


@router.post("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def create_station(station_in: schemas.StationCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Station).filter(models.Station.code == station_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="台位编码已存在")

    station = models.Station(**station_in.model_dump())
    db.add(station)
    db.commit()
    db.refresh(station)

    return schemas.ApiResponse(
        message="创建成功",
        data=schemas.Station.model_validate(station).model_dump()
    )


@router.put("/{station_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def update_station(station_id: int, station_in: schemas.StationUpdate, db: Session = Depends(get_db)):
    station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="台位不存在")

    if station_in.code and station_in.code != station.code:
        existing = db.query(models.Station).filter(models.Station.code == station_in.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="台位编码已存在")

    for key, value in station_in.model_dump(exclude_unset=True).items():
        setattr(station, key, value)

    db.commit()
    db.refresh(station)

    return schemas.ApiResponse(
        message="更新成功",
        data=schemas.Station.model_validate(station).model_dump()
    )


@router.delete("/{station_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def delete_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="台位不存在")

    has_batches = db.query(models.Batch).filter(models.Batch.station_id == station_id).first()
    if has_batches:
        raise HTTPException(status_code=400, detail="该台位有关联批次，无法删除")

    db.delete(station)
    db.commit()

    return schemas.ApiResponse(message="删除成功")
