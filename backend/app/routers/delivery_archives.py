from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/delivery-archives", tags=["交付归档"])

STATUS_MAP = {
    "pending_pour": "待浇注",
    "molding": "成型中",
    "pending_inspect": "待质检",
    "reworking": "返工中",
    "deliverable": "可交付",
    "delivered": "已交付",
    "paused": "暂停"
}


@router.get("", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_delivery_archives(
    style_id: Optional[int] = Query(None),
    batch_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    receiver: Optional[str] = Query(None),
    archiver_id: Optional[int] = Query(None),
    technician_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.DeliveryArchive).join(models.Batch).join(models.Style)

    if style_id:
        query = query.filter(models.Batch.style_id == style_id)
    if batch_id:
        query = query.filter(models.DeliveryArchive.batch_id == batch_id)
    if keyword:
        query = query.filter(models.Batch.code.contains(keyword))
    if receiver:
        query = query.filter(models.DeliveryArchive.receiver.contains(receiver))
    if archiver_id:
        query = query.filter(models.DeliveryArchive.archiver_id == archiver_id)
    if technician_id:
        query = query.filter(models.Batch.technician_id == technician_id)
    if status:
        query = query.filter(models.Batch.status == status)
    if start_date:
        query = query.filter(models.DeliveryArchive.delivery_time >= start_date)
    if end_date:
        query = query.filter(models.DeliveryArchive.delivery_time <= end_date)

    archives = query.order_by(models.DeliveryArchive.delivery_time.desc()).all()

    result = []
    for archive in archives:
        item = schemas.DeliveryArchiveItem(
            id=archive.id,
            batch_id=archive.batch_id,
            batch_code=archive.batch.code,
            style_id=archive.batch.style_id,
            style_name=archive.batch.style.name,
            wax_batch_code=archive.batch.wax_batch.code,
            delivery_time=archive.delivery_time,
            delivered_quantity=archive.delivered_quantity,
            receiver=archive.receiver,
            delivery_remark=archive.delivery_remark,
            quality_conclusion=archive.quality_conclusion,
            archiver_id=archive.archiver_id,
            archiver_name=archive.archiver.name,
            technician_id=archive.batch.technician_id,
            technician_name=archive.batch.technician.name,
            status=archive.batch.status,
            status_name=STATUS_MAP.get(archive.batch.status, archive.batch.status),
            created_at=archive.created_at
        )
        result.append(item.model_dump())

    return schemas.ApiResponse(data={"items": result})
