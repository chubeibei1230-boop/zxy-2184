from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/molds", tags=["模具管理"])


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_molds(db: Session = Depends(get_db)):
    molds = db.query(models.Mold).order_by(models.Mold.code).all()
    result = []
    for mold in molds:
        mold_data = schemas.MoldWithStyle.model_validate(mold).model_dump()
        result.append(mold_data)
    return schemas.ApiResponse(data={"items": result})


@router.get("/available", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_available_molds(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    exclude_batch_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    molds = db.query(models.Mold).filter(models.Mold.status == "available").all()

    available_molds = []
    for mold in molds:
        if start_date and end_date:
            overlapping = db.query(models.Batch).filter(
                models.Batch.mold_id == mold.id,
                models.Batch.status.notin_(["deliverable", "paused"]),
                models.Batch.planned_start_date <= end_date,
                models.Batch.planned_end_date >= start_date
            )
            if exclude_batch_id:
                overlapping = overlapping.filter(models.Batch.id != exclude_batch_id)

            if overlapping.first():
                continue

        mold_data = schemas.MoldWithStyle.model_validate(mold).model_dump()
        available_molds.append(mold_data)

    return schemas.ApiResponse(data={"items": available_molds})


@router.post("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def create_mold(mold_in: schemas.MoldCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Mold).filter(models.Mold.code == mold_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="模具编码已存在")

    style = db.query(models.Style).filter(models.Style.id == mold_in.style_id).first()
    if not style:
        raise HTTPException(status_code=400, detail="款式不存在")

    mold = models.Mold(**mold_in.model_dump())
    db.add(mold)
    db.commit()
    db.refresh(mold)

    return schemas.ApiResponse(
        message="创建成功",
        data=schemas.MoldWithStyle.model_validate(mold).model_dump()
    )


@router.put("/{mold_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def update_mold(mold_id: int, mold_in: schemas.MoldUpdate, db: Session = Depends(get_db)):
    mold = db.query(models.Mold).filter(models.Mold.id == mold_id).first()
    if not mold:
        raise HTTPException(status_code=404, detail="模具不存在")

    if mold_in.code and mold_in.code != mold.code:
        existing = db.query(models.Mold).filter(models.Mold.code == mold_in.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="模具编码已存在")

    if mold_in.style_id:
        style = db.query(models.Style).filter(models.Style.id == mold_in.style_id).first()
        if not style:
            raise HTTPException(status_code=400, detail="款式不存在")

    for key, value in mold_in.model_dump(exclude_unset=True).items():
        setattr(mold, key, value)

    db.commit()
    db.refresh(mold)

    return schemas.ApiResponse(
        message="更新成功",
        data=schemas.MoldWithStyle.model_validate(mold).model_dump()
    )


@router.delete("/{mold_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def delete_mold(mold_id: int, db: Session = Depends(get_db)):
    mold = db.query(models.Mold).filter(models.Mold.id == mold_id).first()
    if not mold:
        raise HTTPException(status_code=404, detail="模具不存在")

    has_batches = db.query(models.Batch).filter(models.Batch.mold_id == mold_id).first()
    if has_batches:
        raise HTTPException(status_code=400, detail="该模具有关联批次，无法删除")

    db.delete(mold)
    db.commit()

    return schemas.ApiResponse(message="删除成功")
