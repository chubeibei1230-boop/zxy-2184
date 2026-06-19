from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import date, datetime, timedelta

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])

STATUS_COLORS = {
    "pending_pour": "#f59e0b",
    "molding": "#3b82f6",
    "pending_inspect": "#8b5cf6",
    "reworking": "#ef4444",
    "deliverable": "#10b981",
    "paused": "#6b7280"
}

STATUS_NAMES = {
    "pending_pour": "待浇注",
    "molding": "成型中",
    "pending_inspect": "待质检",
    "reworking": "返工中",
    "deliverable": "可交付",
    "paused": "暂停"
}

STATION_TYPE_NAMES = {
    "pour": "浇注台",
    "demold": "脱模台",
    "trim": "修边台",
    "inspect": "质检台"
}


def _apply_batch_filters(query, style_id=None, status=None, technician_id=None,
                         start_date=None, end_date=None, keyword=None):
    if style_id:
        query = query.filter(models.Batch.style_id == style_id)
    if status:
        query = query.filter(models.Batch.status == status)
    if technician_id:
        query = query.filter(models.Batch.technician_id == technician_id)
    if start_date:
        query = query.filter(models.Batch.planned_start_date >= start_date)
    if end_date:
        query = query.filter(models.Batch.planned_end_date <= end_date)
    if keyword:
        query = query.filter(models.Batch.code.contains(keyword))
    return query


@router.get("/summary", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_summary(
    style_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    technician_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    base_query = db.query(models.Batch)
    base_query = _apply_batch_filters(base_query, style_id, status, technician_id,
                                      start_date, end_date, keyword)

    total = base_query.count()
    status_counts = {}
    for s in STATUS_NAMES:
        count = base_query.filter(models.Batch.status == s).count()
        status_counts[s] = count

    from .warnings import get_all_warnings_internal
    warnings = get_all_warnings_internal(db)

    pending_review_count = base_query.filter(
        models.Batch.status == "deliverable",
        models.Batch.review_status == "pending_review"
    ).count()

    summary = schemas.DashboardSummary(
        total_batches=total,
        pending_pour=status_counts.get("pending_pour", 0),
        molding=status_counts.get("molding", 0),
        pending_inspect=status_counts.get("pending_inspect", 0),
        reworking=status_counts.get("reworking", 0),
        deliverable=status_counts.get("deliverable", 0),
        paused=status_counts.get("paused", 0),
        pending_delivery_review=pending_review_count,
        warning_count=len(warnings)
    )

    return schemas.ApiResponse(data=summary.model_dump())


@router.get("/batch-progress", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_batch_progress(
    style_id: Optional[int] = Query(None),
    technician_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    base_query = db.query(models.Batch)
    base_query = _apply_batch_filters(base_query, style_id, None, technician_id,
                                      start_date, end_date, keyword)

    result = []
    for status, name in STATUS_NAMES.items():
        count = base_query.filter(models.Batch.status == status).count()
        result.append(schemas.BatchProgressItem(
            status=status,
            status_name=name,
            count=count,
            color=STATUS_COLORS.get(status, "#6b7280")
        ).model_dump())

    return schemas.ApiResponse(data={"items": result})


@router.get("/station-load", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_station_load(
    style_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    technician_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    stations = db.query(models.Station).all()
    result = []

    for station in stations:
        base_query = db.query(models.Batch).filter(models.Batch.station_id == station.id)
        base_query = _apply_batch_filters(base_query, style_id, status, technician_id,
                                          start_date, end_date, keyword)

        occupied_query = base_query.filter(
            models.Batch.status.notin_(["deliverable", "paused"])
        )

        occupied_count = occupied_query.count()
        total_count = base_query.count()

        rate = (occupied_count / total_count * 100) if total_count > 0 else 0

        result.append(schemas.StationLoadItem(
            id=station.id,
            code=station.code,
            name=station.name,
            type=station.type,
            type_name=STATION_TYPE_NAMES.get(station.type, station.type),
            occupied=occupied_count,
            total=total_count,
            rate=round(rate, 1)
        ).model_dump())

    return schemas.ApiResponse(data={"items": result})


@router.get("/pending-inspections", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_pending_inspections(
    style_id: Optional[int] = Query(None),
    technician_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Batch).filter(models.Batch.status == "pending_inspect")

    if style_id:
        query = query.filter(models.Batch.style_id == style_id)
    if technician_id:
        query = query.filter(models.Batch.technician_id == technician_id)
    if start_date:
        query = query.filter(models.Batch.planned_start_date >= start_date)
    if end_date:
        query = query.filter(models.Batch.planned_end_date <= end_date)
    if keyword:
        query = query.filter(models.Batch.code.contains(keyword))

    batches = query.order_by(models.Batch.created_at.desc()).all()

    result = []
    now = datetime.now().date()
    for batch in batches:
        cycle = db.query(models.InspectionCycle).filter(
            models.InspectionCycle.style_id == batch.style_id
        ).first()

        cycle_days = cycle.cycle_days if cycle else 7
        days_since_created = (now - batch.created_at.date()).days
        days_overdue = max(0, days_since_created - cycle_days)

        result.append(schemas.PendingInspectionItem(
            id=batch.id,
            code=batch.code,
            style_name=batch.style.name,
            technician_name=batch.technician.name,
            created_at=batch.created_at,
            days_overdue=days_overdue
        ).model_dump())

    return schemas.ApiResponse(data={"items": result})


@router.get("/pending-delivery-reviews", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_pending_delivery_reviews(
    style_id: Optional[int] = Query(None),
    technician_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Batch).filter(
        models.Batch.status == "deliverable",
        models.Batch.review_status == "pending_review"
    )

    if style_id:
        query = query.filter(models.Batch.style_id == style_id)
    if technician_id:
        query = query.filter(models.Batch.technician_id == technician_id)
    if start_date:
        query = query.filter(models.Batch.planned_start_date >= start_date)
    if end_date:
        query = query.filter(models.Batch.planned_end_date <= end_date)
    if keyword:
        query = query.filter(models.Batch.code.contains(keyword))

    batches = query.order_by(models.Batch.actual_end_date.desc().nullslast(), models.Batch.created_at.desc()).all()

    result = []
    now = datetime.now().date()
    for batch in batches:
        base_date = batch.actual_end_date.date() if batch.actual_end_date else batch.created_at.date()
        days_pending = (now - base_date).days

        result.append(schemas.PendingDeliveryReviewItem(
            id=batch.id,
            code=batch.code,
            style_name=batch.style.name,
            technician_name=batch.technician.name,
            inspector_name=batch.inspector.name if batch.inspector else None,
            quantity=batch.quantity,
            actual_end_date=batch.actual_end_date,
            days_pending=days_pending
        ).model_dump())

    return schemas.ApiResponse(data={"items": result})
