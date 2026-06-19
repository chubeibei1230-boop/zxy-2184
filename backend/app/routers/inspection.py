from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/batches", tags=["质检管理"])


@router.post("/{batch_id}/inspect", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_inspector)])
def record_inspection(
    batch_id: int,
    record_in: schemas.InspectionRecordCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    if batch.status != "pending_inspect":
        raise HTTPException(status_code=400, detail="当前状态不允许质检")

    record = models.InspectionRecord(
        batch_id=batch_id,
        inspector_id=current_user.id,
        inspect_time=record_in.inspect_time,
        dimension_deviation=record_in.dimension_deviation,
        surface_flatness=record_in.surface_flatness,
        is_pass=record_in.is_pass,
        opinion=record_in.opinion
    )
    db.add(record)

    if record_in.is_pass:
        batch.status = "deliverable"
        batch.actual_end_date = record_in.inspect_time
        batch.review_status = "pending_review"

        waiting_rework = db.query(models.ReworkRecord).filter(
            models.ReworkRecord.batch_id == batch_id,
            models.ReworkRecord.status == "waiting_inspection"
        ).order_by(models.ReworkRecord.created_at.desc()).first()
        if waiting_rework:
            waiting_rework.status = "completed"
    else:
        batch.status = "reworking"
        batch.review_status = "not_required"

    batch.inspector_id = current_user.id
    db.commit()

    message = "质检通过，批次已进入可交付状态，待交付复核" if record_in.is_pass else "质检未通过，批次进入返工状态"
    return schemas.ApiResponse(message=message)
