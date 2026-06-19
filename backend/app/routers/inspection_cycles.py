from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/inspection-cycles", tags=["质检周期管理"])


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_inspection_cycles(db: Session = Depends(get_db)):
    cycles = db.query(models.InspectionCycle).order_by(models.InspectionCycle.id).all()
    result = []
    for cycle in cycles:
        cycle_data = schemas.InspectionCycleWithStyle.model_validate(cycle).model_dump()
        result.append(cycle_data)
    return schemas.ApiResponse(data={"items": result})


@router.post("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def create_inspection_cycle(cycle_in: schemas.InspectionCycleCreate, db: Session = Depends(get_db)):
    existing = db.query(models.InspectionCycle).filter(
        models.InspectionCycle.style_id == cycle_in.style_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该款式已设置质检周期")

    style = db.query(models.Style).filter(models.Style.id == cycle_in.style_id).first()
    if not style:
        raise HTTPException(status_code=400, detail="款式不存在")

    cycle = models.InspectionCycle(**cycle_in.model_dump())
    db.add(cycle)
    db.commit()
    db.refresh(cycle)

    return schemas.ApiResponse(
        message="创建成功",
        data=schemas.InspectionCycleWithStyle.model_validate(cycle).model_dump()
    )


@router.put("/{cycle_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def update_inspection_cycle(cycle_id: int, cycle_in: schemas.InspectionCycleUpdate, db: Session = Depends(get_db)):
    cycle = db.query(models.InspectionCycle).filter(models.InspectionCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="质检周期不存在")

    if cycle_in.style_id and cycle_in.style_id != cycle.style_id:
        existing = db.query(models.InspectionCycle).filter(
            models.InspectionCycle.style_id == cycle_in.style_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="该款式已设置质检周期")

        style = db.query(models.Style).filter(models.Style.id == cycle_in.style_id).first()
        if not style:
            raise HTTPException(status_code=400, detail="款式不存在")

    for key, value in cycle_in.model_dump(exclude_unset=True).items():
        setattr(cycle, key, value)

    db.commit()
    db.refresh(cycle)

    return schemas.ApiResponse(
        message="更新成功",
        data=schemas.InspectionCycleWithStyle.model_validate(cycle).model_dump()
    )


@router.delete("/{cycle_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_admin)])
def delete_inspection_cycle(cycle_id: int, db: Session = Depends(get_db)):
    cycle = db.query(models.InspectionCycle).filter(models.InspectionCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="质检周期不存在")

    db.delete(cycle)
    db.commit()

    return schemas.ApiResponse(message="删除成功")
