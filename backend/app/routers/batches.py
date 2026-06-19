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
    "delivered": "已交付",
    "paused": "暂停"
}

STATUS_COLOR_MAP = {
    "pending_pour": "#f59e0b",
    "molding": "#3b82f6",
    "pending_inspect": "#8b5cf6",
    "reworking": "#ef4444",
    "deliverable": "#10b981",
    "delivered": "#0ea5e9",
    "paused": "#6b7280"
}

REVIEW_STATUS_MAP = {
    "not_required": "无需复核",
    "pending_review": "待交付复核",
    "reviewed": "已复核"
}

REVIEW_STATUS_COLOR_MAP = {
    "not_required": "#6b7280",
    "pending_review": "#f59e0b",
    "reviewed": "#10b981"
}


def check_mold_availability(db: Session, mold_id: int, start_date: date, end_date: date, exclude_batch_id: Optional[int] = None) -> bool:
    overlapping = db.query(models.Batch).filter(
        models.Batch.mold_id == mold_id,
        models.Batch.status.notin_(["deliverable", "delivered", "paused"]),
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
    review_status: Optional[str] = Query(None),
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
    if review_status:
        query = query.filter(models.Batch.review_status == review_status)
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
        batch_data["status_color"] = STATUS_COLOR_MAP.get(batch.status, "#6b7280")
        batch_data["review_status_name"] = REVIEW_STATUS_MAP.get(batch.review_status, batch.review_status)
        batch_data["review_status_color"] = REVIEW_STATUS_COLOR_MAP.get(batch.review_status, "#6b7280")
        result.append(batch_data)

    return schemas.ApiResponse(data={"items": result})


@router.get("/{batch_id}", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_batch_detail(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    batch_data = schemas.BatchDetail.model_validate(batch).model_dump()
    batch_data["status_name"] = STATUS_MAP.get(batch.status, batch.status)
    batch_data["status_color"] = STATUS_COLOR_MAP.get(batch.status, "#6b7280")
    batch_data["review_status_name"] = REVIEW_STATUS_MAP.get(batch.review_status, batch.review_status)
    batch_data["review_status_color"] = REVIEW_STATUS_COLOR_MAP.get(batch.review_status, "#6b7280")

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

    if batch.delivery_review:
        dr_data = schemas.DeliveryReviewWithReviewer.model_validate(batch.delivery_review).model_dump(by_alias=True)
        batch_data["delivery_review"] = dr_data

    if batch.delivery_archive:
        da_data = schemas.DeliveryArchiveWithArchiver.model_validate(batch.delivery_archive).model_dump()
        batch_data["delivery_archive"] = da_data

    rework_records = []
    from .reworks import REWORK_STATUS_MAP, REWORK_STATUS_COLOR_MAP
    for rr in batch.rework_records:
        rr_data = schemas.ReworkRecordWithDetails.model_validate(rr).model_dump()
        rr_data["initiator"] = schemas.User.model_validate(rr.initiator).model_dump()
        rr_data["responsible"] = schemas.User.model_validate(rr.responsible).model_dump()
        rr_data["status_name"] = REWORK_STATUS_MAP.get(rr.status, rr.status)
        rr_data["status_color"] = REWORK_STATUS_COLOR_MAP.get(rr.status, "#6b7280")
        rework_records.append(rr_data)
    batch_data["rework_records"] = rework_records

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

    if batch.status not in ["molding", "reworking"]:
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

    return schemas.ApiResponse(message="返工完成，批次重新进入待质检状态")


@router.post("/{batch_id}/delivery-review", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_inspector)])
def record_delivery_review(
    batch_id: int,
    record_in: schemas.DeliveryReviewCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if batch.status != "deliverable":
        raise HTTPException(status_code=400, detail="当前状态不允许交付复核")

    if batch.review_status == "reviewed":
        raise HTTPException(status_code=400, detail="该批次已完成交付复核，不可重复提交")

    if record_in.delivered_quantity <= 0:
        raise HTTPException(status_code=400, detail="交付数量必须大于0")

    if record_in.delivered_quantity > batch.quantity:
        raise HTTPException(status_code=400, detail="交付数量不能超过批次总数量")

    existing_review = db.query(models.DeliveryReview).filter(
        models.DeliveryReview.batch_id == batch_id
    ).first()
    if existing_review:
        db.delete(existing_review)
        db.flush()

    review = models.DeliveryReview(
        batch_id=batch_id,
        reviewer_id=current_user.id,
        review_time=record_in.review_time,
        delivered_quantity=record_in.delivered_quantity,
        final_quality_conclusion=record_in.final_quality_conclusion,
        is_pass=record_in.is_pass,
        exception_remark=record_in.exception_remark
    )
    db.add(review)

    batch.review_status = "reviewed"
    if not record_in.is_pass:
        batch.status = "reworking"
    db.commit()

    return schemas.ApiResponse(message="交付复核完成")


@router.get("/{batch_id}/delivery-review", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_delivery_review(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if not batch.delivery_review:
        return schemas.ApiResponse(data=None)

    review_data = schemas.DeliveryReviewWithReviewer.model_validate(
        batch.delivery_review
    ).model_dump(by_alias=True)
    return schemas.ApiResponse(data=review_data)


@router.post("/{batch_id}/delivery-archive", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_inspector)])
def record_delivery_archive(
    batch_id: int,
    record_in: schemas.DeliveryArchiveCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if batch.status != "deliverable":
        raise HTTPException(status_code=400, detail="当前状态不允许交付归档")

    if batch.delivery_archive:
        raise HTTPException(status_code=400, detail="该批次已完成交付归档，不可重复提交")

    if not batch.delivery_review or not batch.delivery_review.is_pass:
        raise HTTPException(status_code=400, detail="请先完成交付复核且复核通过后再进行交付归档")

    if record_in.delivered_quantity <= 0:
        raise HTTPException(status_code=400, detail="交付数量必须大于0")

    if record_in.delivered_quantity > batch.quantity:
        raise HTTPException(status_code=400, detail="交付数量不能超过批次总数量")

    latest_inspection = None
    if batch.inspection_records:
        latest_inspection = max(batch.inspection_records, key=lambda x: x.inspect_time)
    quality_conclusion = latest_inspection.opinion if latest_inspection else "无质检记录"

    archive = models.DeliveryArchive(
        batch_id=batch_id,
        archiver_id=current_user.id,
        delivery_time=record_in.delivery_time,
        delivered_quantity=record_in.delivered_quantity,
        receiver=record_in.receiver,
        delivery_remark=record_in.delivery_remark,
        quality_conclusion=quality_conclusion
    )
    db.add(archive)

    batch.status = "delivered"
    db.commit()

    return schemas.ApiResponse(message="交付归档完成")


@router.get("/{batch_id}/delivery-archive", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_delivery_archive(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if not batch.delivery_archive:
        return schemas.ApiResponse(data=None)

    archive_data = schemas.DeliveryArchiveWithArchiver.model_validate(
        batch.delivery_archive
    ).model_dump()
    return schemas.ApiResponse(data=archive_data)
