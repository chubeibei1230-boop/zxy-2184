from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'technician', 'inspector')"),
    )

    technician_batches = relationship("Batch", foreign_keys="Batch.technician_id", back_populates="technician")
    inspector_batches = relationship("Batch", foreign_keys="Batch.inspector_id", back_populates="inspector")
    process_records = relationship("ProcessRecord", back_populates="operator")
    inspection_records = relationship("InspectionRecord", back_populates="inspector")


class Style(Base):
    __tablename__ = "styles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    batches = relationship("Batch", back_populates="style")
    molds = relationship("Mold", back_populates="style")
    inspection_cycle = relationship("InspectionCycle", back_populates="style", uselist=False)


class WaxBatch(Base):
    __tablename__ = "wax_batches"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    material = Column(String(100), nullable=False)
    production_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    batches = relationship("Batch", back_populates="wax_batch")


class Mold(Base):
    __tablename__ = "molds"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=False)
    max_cavities = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="available")
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('available', 'in_use', 'maintenance')"),
    )

    style = relationship("Style", back_populates="molds")
    batches = relationship("Batch", back_populates="mold")


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="idle")
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("type IN ('pour', 'demold', 'trim', 'inspect')"),
        CheckConstraint("status IN ('idle', 'occupied', 'disabled')"),
    )

    batches = relationship("Batch", back_populates="station")


class InspectionCycle(Base):
    __tablename__ = "inspection_cycles"

    id = Column(Integer, primary_key=True, index=True)
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=False, unique=True)
    cycle_days = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    style = relationship("Style", back_populates="inspection_cycle")


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=False)
    wax_batch_id = Column(Integer, ForeignKey("wax_batches.id"), nullable=False)
    mold_id = Column(Integer, ForeignKey("molds.id"), nullable=False)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), nullable=False, default="pending_pour")
    review_status = Column(String(20), nullable=False, default="not_required")
    planned_start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    quantity = Column(Integer, nullable=False)
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('pending_pour', 'molding', 'pending_inspect', 'reworking', 'deliverable', 'paused')"),
        CheckConstraint("review_status IN ('not_required', 'pending_review', 'reviewed')"),
    )

    style = relationship("Style", back_populates="batches")
    wax_batch = relationship("WaxBatch", back_populates="batches")
    mold = relationship("Mold", back_populates="batches")
    station = relationship("Station", back_populates="batches")
    technician = relationship("User", foreign_keys=[technician_id], back_populates="technician_batches")
    inspector = relationship("User", foreign_keys=[inspector_id], back_populates="inspector_batches")
    process_records = relationship("ProcessRecord", back_populates="batch", cascade="all, delete-orphan")
    inspection_records = relationship("InspectionRecord", back_populates="batch", cascade="all, delete-orphan")
    delivery_review = relationship("DeliveryReview", back_populates="batch", uselist=False, cascade="all, delete-orphan")


class ProcessRecord(Base):
    __tablename__ = "process_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    type = Column(String(20), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_time = Column(DateTime, nullable=False)
    temperature = Column(Float)
    pressure = Column(Float)
    hold_time = Column(Integer)
    cooling_time = Column(Integer)
    bubble_description = Column(Text)
    bubble_count = Column(Integer)
    rework_reason = Column(Text)
    rework_count = Column(Integer)
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("type IN ('pour', 'demold', 'trim', 'bubble', 'rework')"),
    )

    batch = relationship("Batch", back_populates="process_records")
    operator = relationship("User", back_populates="process_records")


class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspect_time = Column(DateTime, nullable=False)
    dimension_deviation = Column(String(500), nullable=False)
    surface_flatness = Column(Float, nullable=False)
    is_pass = Column(Boolean, nullable=False)
    opinion = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    batch = relationship("Batch", back_populates="inspection_records")
    inspector = relationship("User", back_populates="inspection_records")


class DeliveryReview(Base):
    __tablename__ = "delivery_reviews"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, unique=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_time = Column(DateTime, nullable=False)
    delivered_quantity = Column(Integer, nullable=False)
    final_quality_conclusion = Column(String(500), nullable=False)
    is_pass = Column(Boolean, nullable=False)
    exception_remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    batch = relationship("Batch", back_populates="delivery_review")
    reviewer = relationship("User")
