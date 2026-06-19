from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/batches", tags=["批次管理"])

STATUS_MAP = {
    "pending_pour": "待浇注",
    "molding": "成型中",
    "pending_inspect": "待质检",
    "reworking": "返工中",
    "deliverable": "可交付",
    "paused": "暂停"
}


def check_mold_availability(db: Session, mold_id: int, start_date: date, end_date: date, exclude_batch_id: Optional[int] = None) -> bool:
    overlapping = db.query(models.Batch).filter(
        models.Batch.mold_id == mold_id,
        models.Batch.status.notin_(["deliverable", "paused"]),
        models.Batch.planned_start_date <= end_date,
        models.Batch.planned_end_date >= start_date
    )
    if exclude_batch_id:
        overlapping = overlapping.filter(models.Batch.id != exclude_batch_id)
    return overlapping.first() is None


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_batches(
    style_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    technician_id: Optional[int] = Query(None),
    inspector_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Batch)

    if style_id:
        query = query.filter(models.Batch.style_id == style_id)
    if status:
        query = query.filter(models.Batch.status == status)
    if technician_id:
        query = query.filter(models.Batch.technician_id == technician_id)
    if inspector_id:
        query = query.filter(models.Batch.inspector_id == inspector_id)
    if start_date:
        query = query.filter(models.Batch.planned_start_date >= start_date)
    if end_date:
        query = query.filter(models.Batch.planned_end_date <= end_date)
    if keyword:
        query = query.filter(models.Batch.code.contains(keyword))

    batches = query.order_by(models.Batch.created_at.desc()).all()

    result = []
    for batch in batches:
        batch_data = schemas.Batch.model_validate(batch).model_dump()
        batch_data["style_name"] = batch.style.name
        batch_data["technician_name"] = batch.technician.name
        batch_data["inspector_name"] = batch.inspector.name if batch.inspector else None
        batch_data["status_name"] = STATUS_MAP.get(batch.status, batch.status)
        result.append(batch_data)

    return schemas.ApiResponse(data={"items": result})


@router.get("/{batch_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_batch_detail(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    batch_data = schemas.BatchDetail.model_validate(batch).model_dump()
    batch_data["status_name"] = STATUS_MAP.get(batch.status, batch.status)

    process_records = []
    for pr in batch.process_records:
        pr_data = schemas.ProcessRecordWithOperator.model_validate(pr).model_dump()
        process_records.append(pr_data)
    batch_data["process_records"] = process_records

    inspection_records = []
    for ir in batch.inspection_records:
        ir_data = schemas.InspectionRecordWithInspector.model_validate(ir).model_dump(by_alias=True)
        inspection_records.append(ir_data)
    batch_data["inspection_records"] = inspection_records

    return schemas.ApiResponse(data=batch_data)


@router.post("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def create_batch(batch_in: schemas.BatchCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Batch).filter(models.Batch.code == batch_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="批次编码已存在")

    if not check_mold_availability(db, batch_in.mold_id, batch_in.planned_start_date, batch_in.planned_end_date):
        raise HTTPException(status_code=400, detail="该模具在计划时间段内已有安排，请调整时间或更换模具")

    batch = models.Batch(**batch_in.model_dump())
    batch.status = "pending_pour"
    db.add(batch)
    db.commit()
    db.refresh(batch)

    return schemas.ApiResponse(
        message="创建成功",
        data=schemas.Batch.model_validate(batch).model_dump()
    )


@router.put("/{batch_id}/status", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def update_batch_status(batch_id: int, status_in: schemas.BatchUpdateStatus, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if status_in.status not in STATUS_MAP:
        raise HTTPException(status_code=400, detail="无效的状态值")

    batch.status = status_in.status
    if status_in.remark:
        batch.remark = status_in.remark

    if status_in.status == "deliverable" and not batch.actual_end_date:
        batch.actual_end_date = datetime.now()

    db.commit()
    db.refresh(batch)

    return schemas.ApiResponse(message="状态更新成功")


@router.post("/{batch_id}/pour", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def record_pour(
    batch_id: int,
    record_in: schemas.PourRecordCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if batch.status not in ["pending_pour", "reworking"]:
        raise HTTPException(status_code=400, detail="当前状态不允许记录浇注")

    record = models.ProcessRecord(
        batch_id=batch_id,
        type="pour",
        operator_id=current_user.id,
        record_time=record_in.record_time,
        temperature=record_in.temperature,
        pressure=record_in.pressure,
        hold_time=record_in.hold_time,
        cooling_time=record_in.cooling_time,
        remark=record_in.remark
    )
    db.add(record)

    batch.status = "molding"
    batch.actual_start_date = record_in.record_time
    db.commit()

    return schemas.ApiResponse(message="浇注记录已保存")


@router.post("/{batch_id}/demold", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def record_demold(
    batch_id: int,
    record_in: schemas.DemoldRecordCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if batch.status != "molding":
        raise HTTPException(status_code=400, detail="当前状态不允许记录脱模")

    record = models.ProcessRecord(
        batch_id=batch_id,
        type="demold",
        operator_id=current_user.id,
        record_time=record_in.record_time,
        temperature=record_in.temperature,
        cooling_time=record_in.cooling_time,
        remark=record_in.remark
    )
    db.add(record)
    db.commit()

    return schemas.ApiResponse(message="脱模记录已保存")


@router.post("/{batch_id}/trim", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def record_trim(
    batch_id: int,
    record_in: schemas.TrimRecordCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if batch.status != "molding":
        raise HTTPException(status_code=400, detail="当前状态不允许记录修边")

    record = models.ProcessRecord(
        batch_id=batch_id,
        type="trim",
        operator_id=current_user.id,
        record_time=record_in.record_time,
        remark=record_in.remark
    )
    db.add(record)

    batch.status = "pending_inspect"
    db.commit()

    return schemas.ApiResponse(message="修边记录已保存，批次进入待质检状态")


@router.post("/{batch_id}/bubble", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def record_bubble(
    batch_id: int,
    record_in: schemas.BubbleRecordCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    record = models.ProcessRecord(
        batch_id=batch_id,
        type="bubble",
        operator_id=current_user.id,
        record_time=record_in.record_time,
        bubble_description=record_in.bubble_description,
        bubble_count=record_in.bubble_count,
        remark=record_in.remark
    )
    db.add(record)
    db.commit()

    return schemas.ApiResponse(message="气泡记录已保存")


@router.post("/{batch_id}/rework", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def record_rework(
    batch_id: int,
    record_in: schemas.ReworkRecordCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if batch.status != "reworking":
        raise HTTPException(status_code=400, detail="当前状态不允许提交返工申请")

    record = models.ProcessRecord(
        batch_id=batch_id,
        type="rework",
        operator_id=current_user.id,
        record_time=record_in.record_time,
        rework_reason=record_in.rework_reason,
        rework_count=record_in.rework_count,
        remark=record_in.remark
    )
    db.add(record)

    batch.status = "pending_inspect"
    db.commit()

    return schemas.ApiResponse(message="返工申请已提交，批次重新进入待质检状态")
