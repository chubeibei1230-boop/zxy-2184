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


@router.get("/summary", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_summary(db: Session = Depends(get_db)):
    total = db.query(models.Batch).count()
    status_counts = {}
    for status in STATUS_NAMES:
        count = db.query(models.Batch).filter(models.Batch.status == status).count()
        status_counts[status] = count

    from .warnings import get_all_warnings_internal
    warnings = get_all_warnings_internal(db)

    summary = schemas.DashboardSummary(
        total_batches=total,
        pending_pour=status_counts.get("pending_pour", 0),
        molding=status_counts.get("molding", 0),
        pending_inspect=status_counts.get("pending_inspect", 0),
        reworking=status_counts.get("reworking", 0),
        deliverable=status_counts.get("deliverable", 0),
        paused=status_counts.get("paused", 0),
        warning_count=len(warnings)
    )

    return schemas.ApiResponse(data=summary.model_dump())


@router.get("/batch-progress", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_batch_progress(db: Session = Depends(get_db)):
    result = []
    for status, name in STATUS_NAMES.items():
        count = db.query(models.Batch).filter(models.Batch.status == status).count()
        result.append(schemas.BatchProgressItem(
            status=status,
            status_name=name,
            count=count,
            color=STATUS_COLORS.get(status, "#6b7280")
        ).model_dump())

    return schemas.ApiResponse(data={"items": result})


@router.get("/station-load", response_model=schemas.ApiResponse, dependencies=[Depends(auth.allow_all)])
def get_station_load(db: Session = Depends(get_db)):
    stations = db.query(models.Station).all()
    result = []

    for station in stations:
        occupied_count = db.query(models.Batch).filter(
            models.Batch.station_id == station.id,
            models.Batch.status.notin_(["deliverable", "paused"])
        ).count()

        total_count = db.query(models.Batch).filter(
            models.Batch.station_id == station.id
        ).count()

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
