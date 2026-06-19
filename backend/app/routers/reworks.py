from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/reworks", tags=["返工管理"])

REWORK_STATUS_MAP = {
    "pending": "待处理",
    "processing": "处理中",
    "waiting_inspection": "待复检",
    "completed": "已完成",
    "cancelled": "已取消"
}

REWORK_STATUS_COLOR_MAP = {
    "pending": "#f59e0b",
    "processing": "#3b82f6",
    "waiting_inspection": "#8b5cf6",
    "completed": "#10b981",
    "cancelled": "#6b7280"
}


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_rework_records(
    batch_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    responsible_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.ReworkRecord)

    if batch_id:
        query = query.filter(models.ReworkRecord.batch_id == batch_id)
    if status:
        query = query.filter(models.ReworkRecord.status == status)
    if responsible_id:
        query = query.filter(models.ReworkRecord.responsible_id == responsible_id)
    if keyword:
        query = query.join(models.Batch).filter(models.Batch.code.contains(keyword))

    records = query.order_by(models.ReworkRecord.created_at.desc()).all()

    result = []
    for record in records:
        data = schemas.ReworkRecordWithDetails.model_validate(record).model_dump()
        data["initiator"] = schemas.User.model_validate(record.initiator).model_dump()
        data["responsible"] = schemas.User.model_validate(record.responsible).model_dump()
        data["batch_code"] = record.batch.code
        data["style_name"] = record.batch.style.name
        data["status_name"] = REWORK_STATUS_MAP.get(record.status, record.status)
        data["status_color"] = REWORK_STATUS_COLOR_MAP.get(record.status, "#6b7280")
        result.append(data)

    return schemas.ApiResponse(data={"items": result})


@router.get("/stats", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_rework_stats(db: Session = Depends(get_db)):
    now = datetime.now()

    pending_count = db.query(models.ReworkRecord).filter(
        models.ReworkRecord.status.in_(["pending", "processing"])
    ).count()

    overdue_count = db.query(models.ReworkRecord).filter(
        models.ReworkRecord.status.in_(["pending", "processing"]),
        models.ReworkRecord.expected_finish_time.isnot(None),
        models.ReworkRecord.expected_finish_time < now
    ).count()

    waiting_inspection_count = db.query(models.ReworkRecord).filter(
        models.ReworkRecord.status == "waiting_inspection"
    ).count()

    total_count = db.query(models.ReworkRecord).count()

    stats = schemas.ReworkStats(
        pending_rework=pending_count,
        overdue_rework=overdue_count,
        waiting_inspection=waiting_inspection_count,
        total_rework=total_count
    )

    return schemas.ApiResponse(data=stats.model_dump())


@router.get("/{rework_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_rework_detail(rework_id: int, db: Session = Depends(get_db)):
    record = db.query(models.ReworkRecord).filter(models.ReworkRecord.id == rework_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="返工记录不存在")

    data = schemas.ReworkRecordWithDetails.model_validate(record).model_dump()
    data["initiator"] = schemas.User.model_validate(record.initiator).model_dump()
    data["responsible"] = schemas.User.model_validate(record.responsible).model_dump()
    data["batch_code"] = record.batch.code
    data["style_name"] = record.batch.style.name
    data["status_name"] = REWORK_STATUS_MAP.get(record.status, record.status)
    data["status_color"] = REWORK_STATUS_COLOR_MAP.get(record.status, "#6b7280")

    return schemas.ApiResponse(data=data)


@router.post("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def create_rework(
    rework_in: schemas.ReworkRecordCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == rework_in.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    last_rework = db.query(models.ReworkRecord).filter(
        models.ReworkRecord.batch_id == rework_in.batch_id
    ).order_by(models.ReworkRecord.rework_no.desc()).first()
    rework_no = (last_rework.rework_no + 1) if last_rework else 1

    rework = models.ReworkRecord(
        **rework_in.model_dump(),
        rework_no=rework_no,
        initiator_id=current_user.id,
        status="pending"
    )
    db.add(rework)

    batch.status = "reworking"
    db.commit()
    db.refresh(rework)

    return schemas.ApiResponse(
        message="返工记录已创建",
        data=schemas.ReworkRecord.model_validate(rework).model_dump()
    )


@router.put("/{rework_id}/start", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def start_rework(
    rework_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    rework = db.query(models.ReworkRecord).filter(models.ReworkRecord.id == rework_id).first()
    if not rework:
        raise HTTPException(status_code=404, detail="返工记录不存在")

    if rework.status != "pending":
        raise HTTPException(status_code=400, detail="当前状态不允许开始返工")

    rework.status = "processing"
    db.commit()

    return schemas.ApiResponse(message="已开始返工处理")


@router.put("/{rework_id}/submit-inspection", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_technician)])
def submit_rework_for_inspection(
    rework_id: int,
    rework_in: schemas.ReworkRecordComplete,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    rework = db.query(models.ReworkRecord).filter(models.ReworkRecord.id == rework_id).first()
    if not rework:
        raise HTTPException(status_code=404, detail="返工记录不存在")

    if rework.status not in ["processing", "pending"]:
        raise HTTPException(status_code=400, detail="当前状态不允许提交复检")

    rework.status = "waiting_inspection"
    rework.actual_finish_time = rework_in.actual_finish_time
    rework.rework_result = rework_in.rework_result

    batch = rework.batch
    batch.status = "pending_inspect"
    db.commit()

    return schemas.ApiResponse(message="返工完成，已提交复检")


@router.put("/{rework_id}/complete", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_inspector)])
def complete_rework(
    rework_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    rework = db.query(models.ReworkRecord).filter(models.ReworkRecord.id == rework_id).first()
    if not rework:
        raise HTTPException(status_code=404, detail="返工记录不存在")

    if rework.status != "waiting_inspection":
        raise HTTPException(status_code=400, detail="当前状态不允许完成返工")

    rework.status = "completed"
    db.commit()

    return schemas.ApiResponse(message="返工复检完成")


@router.put("/{rework_id}/cancel", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def cancel_rework(
    rework_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    rework = db.query(models.ReworkRecord).filter(models.ReworkRecord.id == rework_id).first()
    if not rework:
        raise HTTPException(status_code=404, detail="返工记录不存在")

    if rework.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="当前状态不允许取消")

    rework.status = "cancelled"
    db.commit()

    return schemas.ApiResponse(message="返工记录已取消")
